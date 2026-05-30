"""karan section 15 — FINALIZE: discovery-driven parenting + collection / view-layer wiring.

The LAST build step. Runs on the fully-assembled karan world (all earlier
sections already built into the open .blend) and organizes its scene graph so
the eventual GLB export is clean. It ADDS / ORGANIZES only — it never deletes a
Bruno datablock (keep-everything policy). It is idempotent: safe to re-run on a
freshly rebuilt world.

UNLIKE Bruno's 999_finalize (which hardcodes ~859 parent statements + a fixed
active camera + compositor + a minimap view-layer rig for his car-with-no-free-
camera runtime), this is fully DISCOVERY-DRIVEN. It iterates what actually
exists in bpy.data at runtime and wires only that. The karan runtime is a
walkable character with a free orbit camera driven in Three.js, so this script
does NOT set a Blender active camera, does NOT wire a compositor, and does NOT
replicate Bruno's minimap-camera collection excludes.

What it does, in order:
  PHASE 0  Inventory + flag every loose / orphaned / homeless item (logged).
  PHASE 1  Tidy:
            - rehome the orphan oak trees into a new vegetation/oakTrees coll
            - unlink double-linked objects from the Scene master collection
            - re-home any temp-parent children and drop karan scaffolding
              (tmpParent / Orphan Nodes) preserving world pose
            - remove the stray Icosphere + its glTF_not_exported bucket IF unused
  PHASE 2  Section-root parenting:
            - one `root_<collection>` empty per populated collection
            - nest child-collection roots under their parent-collection root
            - parent each object's top-of-chain under the root of its home
              collection (world pose preserved). Existing pivots (animal /
              airDancer) keep their child meshes and ride along under their
              home collection's root.
  PHASE 3  View-layer: exclude genuinely empty / unused leftover collections
            from the main view layer (datablocks kept, just hidden).
  PHASE 4  Safe scene settings (metric units, fps). No camera / compositor.
  PHASE 5  Summary report (counts + any unresolved loose items).

Run LAST, after every other section. Auto-save is handled by the master runner
(15-section-run-all.py), not here.

Inside Blender — Python Console:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/15-finalize.py').read())
"""
import bpy
import mathutils

ROOT_PROP = "section_root"          # custom prop marking a generated section-root empty
ROOT_PREFIX = "root_"
OAK_COLLECTION = "oakTrees"
OAK_PARENT_COLLECTION = "vegetation"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _recursive_obj_count(coll):
    n = len(coll.objects)
    for ch in coll.children:
        n += _recursive_obj_count(ch)
    return n


def _scene_collection_tree(scene):
    """child-coll-name -> parent Collection (or None), plus ordered list, for
    every collection reachable from the scene master collection."""
    parent_of = {}
    order = []
    seen = set()

    def walk(coll, parent):
        if coll.name in seen:
            return
        seen.add(coll.name)
        order.append(coll)
        parent_of[coll.name] = parent
        for ch in coll.children:
            walk(ch, coll)

    for ch in scene.collection.children:
        walk(ch, None)
    return parent_of, order


def _is_root(obj):
    return obj is not None and obj.get(ROOT_PROP) is not None


def _chain_top(obj):
    top = obj
    guard = 0
    while top.parent is not None and guard < 10000:
        top = top.parent
        guard += 1
    return top


def _clear_parent_keep_world(child):
    mw = child.matrix_world.copy()
    child.parent = None
    child.matrix_world = mw


def _parent_to_root(child, root):
    """Parent preserving world pose: matrix_parent_inverse = parent's current
    world matrix inverse (the parent may sit at its section centroid, not the
    origin). Caller must have flushed the depsgraph so root.matrix_world is
    current."""
    child.parent = root
    child.parent_type = 'OBJECT'
    child.matrix_parent_inverse = root.matrix_world.inverted()


def _collection_centroid(coll):
    """Mean world position of all non-root objects in coll (recursively).
    Used to seat a new section root inside its section so its relationship
    lines stay local instead of all converging on the world origin."""
    acc = mathutils.Vector((0.0, 0.0, 0.0))
    n = 0

    def collect(c):
        nonlocal acc, n
        for o in c.objects:
            if o.get(ROOT_PROP) is None:
                acc += o.matrix_world.translation
                n += 1
        for ch in c.children:
            collect(ch)

    collect(coll)
    return acc / n if n else mathutils.Vector((0.0, 0.0, 0.0))


# --------------------------------------------------------------------------- #
# PHASE 0 — inventory
# --------------------------------------------------------------------------- #
def _inventory(scene):
    print("=" * 68)
    print("[15-finalize] PHASE 0 — inventory (pre-wire)")
    print("=" * 68)
    objs = list(bpy.data.objects)
    types = {}
    for o in objs:
        types[o.type] = types.get(o.type, 0) + 1
    print("  objects=%d (%s)  collections=%d"
          % (len(objs), ", ".join(f"{k}={v}" for k, v in sorted(types.items())),
             len(bpy.data.collections)))

    _, order = _scene_collection_tree(scene)
    reachable = {c.name for c in order}
    content = [c for c in order if _recursive_obj_count(c) > 0]
    empty = [c for c in order if _recursive_obj_count(c) == 0]
    print("  scene collections: %d content, %d empty/unused" % (len(content), len(empty)))

    master = scene.collection
    # "homeless" = no usable section home: an object whose only collections are
    # the scene master and/or collections NOT reachable from the scene master
    # (e.g. an orphan Bruno collection like 'oakTrees', which Blender purges on
    # save — leaving the object with no home). Reachability-aware on purpose.
    no_coll = [o for o in objs
               if not any(c is not master and c.name in reachable
                          for c in o.users_collection)]
    if no_coll:
        print("  FLAG homeless objects (no named collection): %s"
              % ", ".join(sorted(o.name for o in no_coll)))

    master = scene.collection
    dbl = [o for o in objs if master in set(o.users_collection) and len(o.users_collection) > 1]
    if dbl:
        from collections import Counter
        per = Counter(next(c.name for c in o.users_collection if c is not master) for o in dbl)
        print("  FLAG double-linked to master: %d (%s)"
              % (len(dbl), ", ".join(f"{k}:{v}" for k, v in sorted(per.items()))))

    parentless = sum(1 for o in objs if o.parent is None and not _is_root(o))
    print("  parentless objects (will be wired to section roots): %d" % parentless)
    return content, empty, no_coll, dbl


# --------------------------------------------------------------------------- #
# PHASE 1 — tidy
# --------------------------------------------------------------------------- #
def _tidy(scene, no_coll, dbl):
    print("\n[15-finalize] PHASE 1 — tidy")
    report = {"oaks": 0, "unlinked": 0, "scaffolding": [], "removed": []}

    # 1a. rehome homeless objects
    if no_coll:
        oaks = [o for o in no_coll if o.name.lower().startswith("oak")]
        others = [o for o in no_coll if o not in oaks]
        if oaks:
            oak_coll = bpy.data.collections.get(OAK_COLLECTION)
            if oak_coll is None:
                oak_coll = bpy.data.collections.new(OAK_COLLECTION)
                print("  + created collection '%s'" % OAK_COLLECTION)
            veg = bpy.data.collections.get(OAK_PARENT_COLLECTION)
            if veg is not None and oak_coll.name not in {c.name for c in veg.children} \
                    and oak_coll.name not in {c.name for c in scene.collection.children}:
                veg.children.link(oak_coll)
                print("  + linked '%s' under '%s'" % (OAK_COLLECTION, OAK_PARENT_COLLECTION))
            master = scene.collection
            for o in oaks:
                if oak_coll not in set(o.users_collection):
                    oak_coll.objects.link(o)
                if master in set(o.users_collection):
                    master.objects.unlink(o)   # was master-only; give it a real home
                report["oaks"] += 1
            print("  rehomed %d orphan oak(s) -> %s" % (report["oaks"], OAK_COLLECTION))
        if others:
            review = bpy.data.collections.get("review_unsorted") \
                or bpy.data.collections.new("review_unsorted")
            if review.name not in {c.name for c in scene.collection.children}:
                scene.collection.children.link(review)
            for o in others:
                if review not in set(o.users_collection):
                    review.objects.link(o)
                if scene.collection in set(o.users_collection):
                    scene.collection.objects.unlink(o)
                print("  ! UNRESOLVED homeless object -> 'review_unsorted' for your review: %s" % o.name)

    # 1b. unlink double-links from the master collection
    master = scene.collection
    for o in dbl:
        if master in set(o.users_collection) and len(o.users_collection) > 1:
            master.objects.unlink(o)
            report["unlinked"] += 1
    if report["unlinked"]:
        print("  unlinked %d object(s) from the Scene master collection" % report["unlinked"])

    # 1c. drop karan temp-parent scaffolding (re-home children, preserve world pose)
    for tmp_name in ("tmpParent",):
        tmp = bpy.data.objects.get(tmp_name)
        if tmp is None:
            continue
        for child in list(tmp.children):
            _clear_parent_keep_world(child)
            print("  re-homed '%s' off scaffolding '%s'" % (child.name, tmp_name))
        bpy.data.objects.remove(tmp, do_unlink=True)
        report["scaffolding"].append(tmp_name)
        print("  - removed scaffolding empty '%s'" % tmp_name)

    # 1d. remove the stray Icosphere if genuinely unused, then its bucket
    ico = bpy.data.objects.get("Icosphere")
    if ico is not None:
        used = any(o.parent is ico for o in bpy.data.objects)
        if not used:
            for m in (mod for o in bpy.data.objects for mod in o.modifiers):
                for a in dir(m):
                    try:
                        if getattr(m, a) is ico:
                            used = True
                    except Exception:
                        pass
        if used:
            print("  ! Icosphere is referenced — leaving it in place")
        else:
            bpy.data.objects.remove(ico, do_unlink=True)
            report["removed"].append("Icosphere")
            print("  - removed stray 'Icosphere' (unreferenced)")

    # 1e. drop now-empty karan leftover buckets
    for cname in ("glTF_not_exported", "Orphan Nodes"):
        c = bpy.data.collections.get(cname)
        if c is not None and len(c.objects) == 0 and len(c.children) == 0:
            bpy.data.collections.remove(c)
            report["removed"].append(cname)
            print("  - removed empty leftover collection '%s'" % cname)

    return report


# --------------------------------------------------------------------------- #
# PHASE 2 — section-root parenting
# --------------------------------------------------------------------------- #
def _wire_parents(scene):
    print("\n[15-finalize] PHASE 2 — section-root parenting")
    bpy.context.view_layer.update()   # PHASE 1 relinked objects; refresh matrix_world for centroids
    parent_of, order = _scene_collection_tree(scene)
    content = [c for c in order if _recursive_obj_count(c) > 0]
    content_names = {c.name for c in content}

    # 2a. one root empty per content collection, seated at the section centroid
    #     so its relationship lines stay local (not all converging on origin).
    #     Existing roots are left where they are — moving a root after its
    #     children are parented would shift them; placing only at creation keeps
    #     this idempotent.
    roots = {}
    made = 0
    for c in content:
        rname = ROOT_PREFIX + c.name
        root = bpy.data.objects.get(rname)
        if root is None:
            centroid = _collection_centroid(c)   # before linking the root in
            root = bpy.data.objects.new(rname, None)   # empty
            root.empty_display_type = 'PLAIN_AXES'
            root.empty_display_size = 1.0
            root.location = centroid
            root.rotation_euler = (0.0, 0.0, 0.0)
            root.scale = (1.0, 1.0, 1.0)
            made += 1
        root[ROOT_PROP] = c.name
        if c not in set(root.users_collection):
            # ensure the root lives in (only) its own collection
            for uc in list(root.users_collection):
                uc.objects.unlink(root)
            c.objects.link(root)
        roots[c.name] = root
    bpy.context.view_layer.update()   # flush root.matrix_world before parenting
    print("  section roots: %d total (%d newly created)" % (len(roots), made))

    # 2b. nest child-collection roots under their parent-collection root
    nested = 0
    for c in content:
        parent_coll = parent_of.get(c.name)
        if parent_coll is not None and parent_coll.name in roots:
            child_root = roots[c.name]
            parent_root = roots[parent_coll.name]
            if child_root.parent is not parent_root:
                _parent_to_root(child_root, parent_root)
                nested += 1
    print("  nested %d section root(s) under parent-section roots" % nested)

    # 2c. parent each object's chain-top under the root of its home collection
    wired = 0
    homeless = []
    bpy.context.view_layer.update()
    for o in list(bpy.data.objects):
        if _is_root(o):
            continue
        top = _chain_top(o)
        if _is_root(top) or top.parent is not None:
            continue                      # already wired under a root
        # home collection = first content collection the chain-top belongs to
        home = next((c for c in top.users_collection if c.name in content_names), None)
        if home is None:
            homeless.append(top.name)
            continue
        _parent_to_root(top, roots[home.name])
        wired += 1
    print("  parented %d chain-top object(s) to their section root" % wired)
    if homeless:
        uniq = sorted(set(homeless))
        print("  ! %d chain-top(s) had no content-collection home (left at scene root): %s"
              % (len(uniq), ", ".join(uniq[:20]) + (" ..." if len(uniq) > 20 else "")))
    return roots, wired, homeless


# --------------------------------------------------------------------------- #
# PHASE 3 — view-layer excludes
# --------------------------------------------------------------------------- #
def _wire_view_layers(scene):
    print("\n[15-finalize] PHASE 3 — view-layer excludes (empty / unused colls)")
    excluded = []

    def walk(lc):
        yield lc
        for ch in lc.children:
            yield from walk(ch)

    for vl in scene.view_layers:
        for lc in walk(vl.layer_collection):
            coll = lc.collection
            if coll is scene.collection:
                continue
            is_empty = _recursive_obj_count(coll) == 0
            if is_empty and not lc.exclude:
                lc.exclude = True
                excluded.append(coll.name)
    if excluded:
        print("  excluded %d empty/unused collection(s) from the main view layer"
              % len(excluded))
        print("    " + ", ".join(sorted(set(excluded))))
    else:
        print("  nothing to exclude")
    return excluded


# --------------------------------------------------------------------------- #
# PHASE 4 — safe scene settings
# --------------------------------------------------------------------------- #
def _scene_settings(scene):
    print("\n[15-finalize] PHASE 4 — scene settings (units / fps only)")
    try:
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 1.0
        scene.unit_settings.length_unit = 'METERS'
    except Exception as e:
        print("  unit settings:", e)
    try:
        scene.render.fps = 24
        scene.render.fps_base = 1.0
    except Exception as e:
        print("  fps:", e)
    cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
    print("  active camera: SKIPPED (free runtime orbit camera; %d Blender cameras present)"
          % len(cams))
    print("  compositor + node-ref fixups: SKIPPED (Bruno-specific; not used by karan runtime)")


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def run():
    scene = bpy.context.scene
    print("\n" + "#" * 68)
    print("# [15-finalize] karan world finalize — %s" % (bpy.data.filepath or "<unsaved>"))
    print("#" * 68)

    content, empty, no_coll, dbl = _inventory(scene)
    tidy = _tidy(scene, no_coll, dbl)
    roots, wired, homeless = _wire_parents(scene)
    excluded = _wire_view_layers(scene)
    _scene_settings(scene)

    print("\n" + "=" * 68)
    print("[15-finalize] SUMMARY")
    print("=" * 68)
    print("  section roots created/ensured : %d" % len(roots))
    print("  objects parented to a root    : %d" % wired)
    print("  orphan oaks rehomed           : %d" % tidy["oaks"])
    print("  unlinked from master coll     : %d" % tidy["unlinked"])
    print("  scaffolding removed           : %s" % (", ".join(tidy["scaffolding"]) or "none"))
    print("  leftovers removed             : %s" % (", ".join(tidy["removed"]) or "none"))
    print("  empty colls excluded (VL)     : %d" % len(excluded))
    if homeless:
        print("  !! UNRESOLVED chain-tops       : %d (see PHASE 2 log)" % len(set(homeless)))
    else:
        print("  unresolved loose items        : none")
    print("[15-finalize] done")


if __name__ == "__main__":
    run()
