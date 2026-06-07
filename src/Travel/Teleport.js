export class Teleport {
  constructor({
    player,
    playerCamera,
    controller,
    terrain,
    navmask,
    transitionFx,
    audio,
    discovery,
    achievements = null,
    sections = null,
    world = null,
  }) {
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.terrain = terrain;
    this.navmask = navmask;
    this.transitionFx = transitionFx;
    this.audio = audio;
    this.discovery = discovery;
    this.achievements = achievements;
    // Section catalog + world handle let toSection() accept a string key (used
    // by the .verify probes and any future quick-jump UI). Map UI still passes
    // full section objects so this is additive.
    this.sections = sections;
    this.world = world;
    this.isActive = false;
  }

  async toSection(section, clickScreenPos = null) {
    if (this.isActive) return false;
    if (typeof section === 'string') {
      section = this.#resolveSectionKey(section);
    }
    if (!section) return false;
    this.isActive = true;
    this.achievements?.onFastTravel?.();
    const center = this.#screenPct(clickScreenPos);
    this.controller?.lock?.();
    this.controller?.clearVirtualInput?.();
    this.audio?.playTeleportWoosh?.();
    this.audio?.duckAmbient?.(0.3, 180);

    await this.transitionFx.play(center.x, center.y, async () => {
      const { x, z, facing } = this.#safeLanding(section);
      const y = (this.terrain?.heightAt?.(x, z) ?? 0) + 0.1;
      if (this.player?.body) this.player.body.teleport(x, y, z);
      this.player?.group?.position?.set(x, y, z);
      if (this.player?.group?.rotation) this.player.group.rotation.y = facing;
      if (this.player) {
        this.player._targetYaw = facing;
        this.player._currentYaw = facing;
      }
      this.playerCamera?.snapTo?.({ x, y, z }, facing);
      this.audio?.playTeleportArrive?.();
      this.discovery?.update?.(x, z);
    });

    this.audio?.duckAmbient?.(1.0, 450);
    this.controller?.unlock?.();
    this.isActive = false;
    return true;
  }

  /**
   * Resolve a string key ('projects', 'skills', 'experience', 'contact',
   * 'resume') to a section object compatible with #safeLanding. Looks first
   * in the catalog passed at construction, then falls back to world.signs
   * for 'resume' (which lives on the portfolio mounts, not SECTIONS).
   */
  #resolveSectionKey(key) {
    if (Array.isArray(this.sections)) {
      const found = this.sections.find((s) => s.id === key);
      if (found) return found;
    }
    if (key === 'resume') {
      const pos = this.world?.signs?.resumePosition;
      if (pos) {
        return {
          id: 'resume',
          name: 'Resume',
          position: [pos.x, pos.y ?? 0, pos.z],
          landingOffset: [0, 0, 2.5],   // stand a couple metres south of the lectern
        };
      }
    }
    return null;
  }

  #screenPct(pos) {
    if (!pos) return { x: 50, y: 50 };
    return {
      x: Math.max(0, Math.min(100, (pos.x / window.innerWidth) * 100)),
      y: Math.max(0, Math.min(100, (pos.y / window.innerHeight) * 100)),
    };
  }

  #safeLanding(section) {
    const [sx, , sz] = section.position;
    // Explicit landing (runtime-resolved stand spot + facing toward the
    // feature). Use it verbatim when clear; otherwise fall through to the
    // ring search around the feature centre below.
    if (section.landing) {
      const { x, z, facing } = section.landing;
      if (!this.navmask || this.#landingIsClear(x, z, facing)) {
        return { x, z, facing };
      }
    }
    const [ox, , oz] = section.landingOffset ?? [0, 0, 0];
    const desired = { x: sx + ox, z: sz + oz };
    const facing = section.landing?.facing ?? Math.atan2(sx - desired.x, sz - desired.z);
    if (!this.navmask || this.#landingIsClear(desired.x, desired.z, facing)) {
      return { ...desired, facing };
    }

    let best = null;
    let bestScore = Infinity;
    const preferred = Math.atan2(desired.z - sz, desired.x - sx);
    for (let r = 6; r <= 14; r += 0.75) {
      for (let i = 0; i < 41; i++) {
        const spread = ((i - 20) / 20) * Math.PI * 0.72;
        const a = preferred + spread;
        const x = sx + Math.cos(a) * r;
        const z = sz + Math.sin(a) * r;
        const candidateFacing = Math.atan2(sx - x, sz - z);
        if (!this.#landingIsClear(x, z, candidateFacing)) continue;
        const sectionDist = Math.hypot(x - sx, z - sz);
        const desiredDist = Math.hypot(x - desired.x, z - desired.z);
        const approachDot = ((x - sx) * (desired.x - sx) + (z - sz) * (desired.z - sz));
        const score = desiredDist + Math.abs(sectionDist - 8.5) * 0.25 - approachDot * 0.002;
        if (score < bestScore) {
          bestScore = score;
          best = { x, z, facing: candidateFacing };
        }
      }
    }
    const landing = best ?? desired;
    return {
      x: landing.x,
      z: landing.z,
      facing: landing.facing ?? Math.atan2(sx - landing.x, sz - landing.z),
    };
  }

  #landingIsClear(x, z, facing) {
    if (!this.navmask.hasClearance(x, z, 1.45)) return false;
    for (const cameraDistance of [3.0, 4.5, 6.0]) {
      const cameraX = x - Math.sin(facing) * cameraDistance;
      const cameraZ = z - Math.cos(facing) * cameraDistance;
      if (!this.navmask.hasClearance(cameraX, cameraZ, 1.05)) return false;
      if (!this.navmask.segmentHasClearance(x, z, cameraX, cameraZ, 0.45)) return false;
    }
    return true;
  }
}
