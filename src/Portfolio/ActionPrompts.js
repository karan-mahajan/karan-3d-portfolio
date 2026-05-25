import * as THREE from 'three';

const MOVE_KEYS = new Set([
  'KeyW', 'KeyA', 'KeyS', 'KeyD',
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  'Space',
]);
const COMBAT_RESET_SECONDS = 5;
const PUSH_JOKE_DELAY = 1.6;
const PUSH_JOKE_INTERVAL = 2.6;

const PUSH_JOKES = {
  tree: [
    'Even the squirrels are laughing.',
    'This tree was here first.',
    'Real oak, real stubborn.',
    'It pays property tax.',
    'Nature wins. Always.',
    'Try hugging it instead.',
    'Bark stronger than your shoulder.',
    'Photosynthesis 1, you 0.',
  ],
  board: [
    'The HOA approved this.',
    'Bolted to the codebase.',
    'Even my best work wont budge.',
    'Submit a ticket?',
    'Press harder. Same result.',
    'Its rendered, not movable.',
    '404: motion not found.',
  ],
  sign: [
    'The sign disagrees.',
    'Signs are stubborn by design.',
    'Wood doesnt yield.',
    'Even the typography is rigid.',
    'Marker, not a mover.',
    'Move along - literally.',
  ],
  section: [
    'Dont push my buttons.',
    'Load-bearing self-doubt.',
    'The structure prevails.',
    'Solid build, unfortunately.',
    'Even my home page wont move.',
  ],
  rock: [
    'Its a rock. Of course not.',
    'Tectonically speaking, no.',
    'Predates the planet.',
    'Geology disagrees.',
    'Maybe in a thousand years.',
    'Stone-faced refusal.',
    'This boulder has tenure.',
  ],
  log: [
    'Its napping.',
    'Lumberjack required.',
    'Roll over - no, the log.',
    'Even the moss is laughing.',
    'Try a different log.',
  ],
  crate: [
    'Label says fragile - its bluffing.',
    'Shipping ETA: never.',
    'Whats inside? More crates.',
    'Even the postman gave up.',
    'Cardboards flexing on you.',
  ],
  bag: [
    'Punch it instead.',
    'The bag is winning.',
    'Try squaring up first.',
    'It hangs there. Like Mondays.',
    'Maybe ask politely.',
  ],
  generic: [
    'Keep pushing!',
    'It wont budge.',
    'Try a different angle?',
    'Shouldve skipped leg day.',
    'This is futile.',
    'Have you tried turning it off and on again?',
    'Persistence is admirable.',
    'Achievement unlocked: futile effort.',
  ],
};

const PUSH_FACING_MIN_DOT = 0.5; // ±60° arc — matches the bag-punch facing check

function shuffleCopy(arr) {
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/**
 * Drives proximity prompts + push hint + animation triggers for the "do"
 * interactables. Sibling to [src/Portfolio/Interaction.js] (billboards).
 * Modes: oneShot, holdLoop, zoneLoop, combat. Plus a global P key for push.
 */
export class ActionPrompts {
  constructor({ player, controller, audio, billboardInteraction = null, playerCamera = null, achievements = null }) {
    this.player = player;
    this.controller = controller;
    this.audio = audio;
    this.billboardInteraction = billboardInteraction;
    this.playerCamera = playerCamera;
    this.achievements = achievements;

    this.triggers = [];
    this.candidate = null;
    this.activeHoldLoop = null;
    this.activeZoneLoop = null;
    this.combatState = null;
    this.oneShotActive = null;
    this.globalPushActive = false;
    this.pushStartSec = 0;
    this.pushStartMs = 0;
    this.activePushSpot = null;
    this._elapsed = 0;

    this.pushSpots = [];
    this.currentPushSpot = null;
    this._pushJokeDeck = [];
    this._activeJokeText = null;

    this._installDom();
    this._installKeyListeners();
  }

  add(trigger) {
    const pos = trigger.position;
    const v3 = pos instanceof THREE.Vector3 ? pos : new THREE.Vector3(pos.x, pos.y ?? 0, pos.z);
    this.triggers.push({ ...trigger, position: v3 });
  }

  addPushSpot({ position, surfaceRadius, type = 'generic', name = null, colliderRadius = null }) {
    const v3 = position instanceof THREE.Vector3
      ? position
      : new THREE.Vector3(position.x, position.y ?? 0, position.z);
    this.pushSpots.push({ position: v3, surfaceRadius, type, name, colliderRadius });
  }

  /**
   * Pulls push spots from the loaded world. Interactables register their
   * own spots directly via addPushSpot.
   *
   * Pool: every standing solid prop — trees, rocks, billboards, signs,
   * spawn compass — so the joke gag fires when the player tries to push
   * something they obviously can't. Crate + bag are the real pushable
   * interactions and come from Interactables.
   *
   * Excluded: lying-down props (logs, stumps) because the push animation
   * is a standing arms-forward push; firing it at a ground-level log
   * looks broken. Walk-through accents (bushes, pebbles, ferns) have no
   * collider and aren't candidates anyway.
   */
  discoverPushSpots(world) {
    if (!world) return;
    // colliderRadius values mirror the physical collider extents used by
    // Signs.js / Billboards.js — they drive the push-start snap so the hand
    // at apex just touches the visible face instead of clipping through it
    // (for billboards/signs the front slab is ~8 cm thin in local Z).
    if (world.billboards && world.billboards.items) {
      for (const item of world.billboards.items) {
        this.addPushSpot({ position: item.position, surfaceRadius: 3.0, type: 'board', colliderRadius: 0.10 });
      }
    }
    if (world.signs) {
      if (world.signs.compassPosition) {
        this.addPushSpot({ position: world.signs.compassPosition, surfaceRadius: 4.0, type: 'sign', name: 'compass', colliderRadius: 0.13 });
      }
      if (world.signs.experienceItems) {
        for (const item of world.signs.experienceItems) {
          this.addPushSpot({ position: item.position, surfaceRadius: 2.8, type: 'sign', colliderRadius: 0.16 });
        }
      }
      if (world.signs.skillsPosition) {
        this.addPushSpot({ position: world.signs.skillsPosition, surfaceRadius: 4.5, type: 'section', name: 'skills', colliderRadius: 0.30 });
      }
      if (world.signs.contactPosition) {
        this.addPushSpot({ position: world.signs.contactPosition, surfaceRadius: 3.2, type: 'section', name: 'contact', colliderRadius: 0.30 });
      }
    }
    if (world.nature && world.nature.pushSpots) {
      for (const spot of world.nature.pushSpots) {
        // Logs/stumps share kind: 'log' and lie on the ground — the standing
        // push animation doesn't match, so skip them.
        if (spot.type === 'log') continue;
        this.addPushSpot(spot);
      }
    }
    console.log('[ActionPrompts] discovered push spots:', this.pushSpots.length);
  }

  _installDom() {
    this.promptEl = document.createElement('div');
    this.promptEl.className = 'action-prompt hidden';
    this.promptEl.innerHTML = '<span class="key">E</span><span class="label"></span>';
    document.body.appendChild(this.promptEl);

    this.pushHintEl = document.createElement('div');
    this.pushHintEl.className = 'push-hint hidden';
    this.pushHintEl.setAttribute('role', 'status');
    this.pushHintEl.setAttribute('aria-live', 'polite');
    this.pushHintEl.innerHTML = '<span class="key" aria-hidden="true">P</span><span class="label">Press P to push</span>';
    document.body.appendChild(this.pushHintEl);

    this.pushJokeEl = document.createElement('div');
    this.pushJokeEl.className = 'push-joke hidden';
    this.pushJokeEl.setAttribute('role', 'status');
    this.pushJokeEl.setAttribute('aria-live', 'polite');
    document.body.appendChild(this.pushJokeEl);

    // Brief toast for blocked moves ("Not enough space to backflip", etc.).
    // Reuses the warm-palette dark-chip look from the other prompts.
    this.blockedEl = document.createElement('div');
    this.blockedEl.className = 'action-blocked hidden';
    this.blockedEl.setAttribute('role', 'status');
    this.blockedEl.setAttribute('aria-live', 'polite');
    document.body.appendChild(this.blockedEl);
  }

  _showBlockedMessage(text, durationMs = 1500) {
    this.blockedEl.textContent = text;
    this.blockedEl.classList.remove('hidden');
    if (this._blockedTimer) clearTimeout(this._blockedTimer);
    this._blockedTimer = setTimeout(() => {
      this.blockedEl.classList.add('hidden');
      this._blockedTimer = null;
    }, durationMs);
  }

  _showPushHint() { this.pushHintEl.classList.remove('hidden'); }
  _hidePushHint() { this.pushHintEl.classList.add('hidden'); }
  _showPushJoke(text) {
    if (this.pushJokeEl.textContent !== text) this.pushJokeEl.textContent = text;
    this.pushJokeEl.classList.remove('hidden');
  }
  _hidePushJoke() { this.pushJokeEl.classList.add('hidden'); }
  _showPrompt(label) {
    this.promptEl.querySelector('.label').textContent = label;
    this.promptEl.classList.remove('hidden');
  }
  _hidePrompt() { this.promptEl.classList.add('hidden'); }

  _installKeyListeners() {
    this._onKeyDown = (e) => {
      if (this.billboardInteraction && this.billboardInteraction.activeIndex >= 0) return;
      if (this.billboardInteraction && this.billboardInteraction.contactOpen) return;
      if (this.billboardInteraction && this.billboardInteraction.zooming) return;

      // Ignore key presses with modifier keys so we don't conflict with
      // browser shortcuts (Ctrl+B = bookmarks, Ctrl+C = copy, Ctrl+P = print).
      const hasModifier = e.ctrlKey || e.metaKey || e.altKey;

      // Global one-shot actions: B = backflip, C = cartwheel. Doable from
      // anywhere, but refuse if the player is near a pushable obstacle
      // (tree/sign/board/etc.) so the animation doesn't visually clip.
      if (e.code === 'KeyB' && !e.repeat && !hasModifier && this._canStartGlobalAction()) {
        this._triggerGlobalAction('backflip', 'Not enough space to backflip');
        return;
      }
      if (e.code === 'KeyC' && !e.repeat && !hasModifier && this._canStartGlobalAction()) {
        this._triggerGlobalAction('cartwheel', 'Not enough space to cartwheel');
        return;
      }

      if (e.code === 'KeyP' && !e.repeat && !hasModifier) {
        this.startPush();
        return;
      }

      if (this.activeZoneLoop && MOVE_KEYS.has(e.code)) {
        this._exitZoneLoop();
        return;
      }

      if (e.code !== 'KeyE' || e.repeat) return;

      if (this.activeZoneLoop && this.activeZoneLoop.cycleActions && this.activeZoneLoop.cycleActions.length) {
        const t = this.activeZoneLoop;
        t._cycleIndex = ((t._cycleIndex || 0) + 1) % t.cycleActions.length;
        this.player.swapLoopAction(t.cycleActions[t._cycleIndex]);
        if (this.audio) this.audio.playInteract();
        return;
      }

      const t = this.candidate;
      if (!t) return;
      if (t.mode === 'holdLoop') this._startHoldLoop(t);
      else if (t.mode === 'oneShot') this._startOneShot(t);
      else if (t.mode === 'combat') this._advanceCombat(t);
    };

    this._onKeyUp = (e) => {
      if (e.code === 'KeyE' && this.activeHoldLoop) {
        this._endHoldLoop();
      } else if (e.code === 'KeyP' && this.globalPushActive) {
        this._endGlobalPush();
      }
    };

    window.addEventListener('keydown', this._onKeyDown);
    window.addEventListener('keyup', this._onKeyUp);
    window.addEventListener('blur', () => {
      if (this.activeHoldLoop) this._endHoldLoop();
      if (this.globalPushActive) this._endGlobalPush();
    });
  }

  _canStartGlobalAction() {
    return !this.globalPushActive
      && !this.activeHoldLoop
      && !this.oneShotActive
      && !this.activeZoneLoop;
  }

  _triggerGlobalAction(actionName, blockMessage) {
    // Swept-capsule clearance against the static world (incl. heightfield
    // ground). The old proximity-only check using currentPushSpot only
    // covered tagged push spots — walls, dock railings, furniture, mailbox
    // body, slopes, and tree canopies weren't blocked, so limbs clipped
    // through them.
    if (!this._hasClearance(actionName)) {
      this._showBlockedMessage(blockMessage);
      return;
    }
    const action = this.player.character && this.player.character.actions[actionName];
    if (!action) {
      this._showBlockedMessage('Animation not loaded');
      return;
    }
    const clip = action.getClip();
    const duration = (clip && clip.duration) || 2.0;
    if (!this.player.performAction(actionName, { interruptible: false, then: 'idle' })) return;
    this.controller.paused = true;
    // Backflip / cartwheel get the whoosh sample; other future global
    // actions stay silent unless they get their own audio hook.
    if ((actionName === 'backflip' || actionName === 'cartwheel') && this.audio) {
      this.audio.playFlip();
    }
    this.oneShotActive = { trigger: { id: 'global-' + actionName }, untilSec: this._elapsed + duration + 0.1 };
    if (this.playerCamera) this.playerCamera.applyActionZoom();
    if (this.audio) this.audio.playInteract();
    if (this.achievements) {
      const r = this.player?.position
        ? Math.hypot(this.player.position.x, this.player.position.z)
        : 0;
      const inWater = r > 45; // Player.WATER_ENTRY_RADIUS
      if (actionName === 'backflip') this.achievements.onBackflip(inWater);
      else if (actionName === 'cartwheel') this.achievements.onCartwheel();
    }
  }

  /**
   * Swept-capsule clearance for global flips. Casts an upright capsule
   * (radius 0.4, halfHeight 1.2) that conservatively envelopes the player's
   * swept volume during the animation:
   *
   *   backflip  — cast backward 1.5m AND upward 2.5m
   *   cartwheel — cast ±sideways 1.5m AND upward 2.5m
   *
   * The cast origin is lifted to (feet + 1.65m) so the capsule's bottom
   * hemisphere sits ~5cm above the ground — flat terrain stays a non-hit,
   * but a rising slope, low canopy, wall, sign, dock railing, or tree all
   * trigger refusal because the cast intersects them. This is what stops
   * hands/feet/head from clipping through static geometry mid-flip.
   *
   * Excludes the player's own collider so it never self-blocks.
   */
  _hasClearance(actionName) {
    const physics = this.player && this.player.physics;
    if (!physics || !physics.ready) return true;
    const RADIUS = 0.4;
    const HALF_HEIGHT = 1.2;
    const SWEEP_BACK = 1.5;
    const SWEEP_SIDE = 1.5;
    const SWEEP_UP = 2.5;
    const SKIN = 0.05;
    const origin = {
      x: this.player.position.x,
      y: this.player.position.y + HALF_HEIGHT + RADIUS + SKIN,
      z: this.player.position.z,
    };
    const yaw = this.player.group.rotation.y;
    // Forward = (sin(yaw), 0, cos(yaw)); Right = up × forward = (cos(yaw), 0, -sin(yaw))
    const fx = Math.sin(yaw);
    const fz = Math.cos(yaw);
    const rx = fz;
    const rz = -fx;
    const excl = (this.player.body && this.player.body.collider) || null;
    const UP = { x: 0, y: 1, z: 0 };

    if (actionName === 'backflip') {
      const okBack = physics.clearanceFor(origin, { x: -fx, y: 0, z: -fz }, SWEEP_BACK, RADIUS, HALF_HEIGHT, excl);
      const okUp   = physics.clearanceFor(origin, UP, SWEEP_UP, RADIUS, HALF_HEIGHT, excl);
      return okBack && okUp;
    }
    if (actionName === 'cartwheel') {
      const okRight = physics.clearanceFor(origin, { x: rx, y: 0, z: rz }, SWEEP_SIDE, RADIUS, HALF_HEIGHT, excl);
      const okLeft  = physics.clearanceFor(origin, { x: -rx, y: 0, z: -rz }, SWEEP_SIDE, RADIUS, HALF_HEIGHT, excl);
      const okUp    = physics.clearanceFor(origin, UP, SWEEP_UP, RADIUS, HALF_HEIGHT, excl);
      return okRight && okLeft && okUp;
    }
    return true;
  }

  _endGlobalPush() {
    this.globalPushActive = false;
    this.pushStartSec = 0;
    this.pushStartMs = 0;
    this.activePushSpot = null;
    this._pushJokeDeck = [];
    this._activeJokeText = null;
    this.player.stopLoopAction();
    this.controller.paused = false;
    if (this.playerCamera) this.playerCamera.releaseActionZoom();
    if (this.audio) this.audio.endPush();
    this._hidePushJoke();
  }

  // ── Public action triggers ────────────────────────────────────────────
  // Mobile touch buttons (src/UI/UIController.js) call these to reuse the
  // existing clearance / camera-zoom / audio / paused-state logic without
  // simulating keyboard events. Same gates the keyboard listener applies.

  triggerBackflip() {
    if (!this._canStartGlobalAction()) return;
    if (this.billboardInteraction && (this.billboardInteraction.activeIndex >= 0 || this.billboardInteraction.contactOpen || this.billboardInteraction.zooming)) return;
    this._triggerGlobalAction('backflip', 'Not enough space to backflip');
  }

  triggerCartwheel() {
    if (!this._canStartGlobalAction()) return;
    if (this.billboardInteraction && (this.billboardInteraction.activeIndex >= 0 || this.billboardInteraction.contactOpen || this.billboardInteraction.zooming)) return;
    this._triggerGlobalAction('cartwheel', 'Not enough space to cartwheel');
  }

  startPush() {
    if (this.globalPushActive || this.activeHoldLoop || this.oneShotActive || this.activeZoneLoop) return;
    if (this.billboardInteraction && (this.billboardInteraction.activeIndex >= 0 || this.billboardInteraction.contactOpen || this.billboardInteraction.zooming)) return;
    // Realism: P only fires when the player is actually facing a real
    // pushable in range. currentPushSpot is set by tick() after the
    // proximity-and-facing filter, so its presence is the gate.
    if (!this.currentPushSpot) return;
    // Body-clipping fix: the standing push animation extends the arms
    // (and slightly leans the head) forward. If the player is flush
    // against the object, those forward-reaching parts pass through the
    // visible mesh. Snap the player outward along the spot→player ray
    // to a comfortable push distance before the animation plays.
    this.activePushSpot = this.currentPushSpot;
    this._snapToPushDistance(this.activePushSpot, 0);
    if (this.player.startLoopAction('push')) {
      this.globalPushActive = true;
      this.pushStartSec = this._elapsed;
      this.pushStartMs = performance.now();
      const type = (this.currentPushSpot && this.currentPushSpot.type) || 'generic';
      const pool = PUSH_JOKES[type] || PUSH_JOKES.generic;
      this._pushJokeDeck = shuffleCopy(pool);
      this._activeJokeText = null;
      this.controller.paused = true;
      if (this.playerCamera) this.playerCamera.applyActionZoom();
      if (this.audio) this.audio.startPush();
      if (this.achievements) {
        // Identify pushed object by its world position so the set-count for
        // The Bulldozer counts unique props, not unique attempts.
        const p = this.currentPushSpot.position;
        const id = (this.currentPushSpot.name)
          ? `${this.currentPushSpot.type}:${this.currentPushSpot.name}`
          : `${this.currentPushSpot.type}:${p.x.toFixed(2)},${p.z.toFixed(2)}`;
        this.achievements.onPush(id);
      }
    } else {
      this.activePushSpot = null;
    }
  }

  endPush() {
    if (this.globalPushActive) this._endGlobalPush();
  }

  /**
   * Slides the player outward along the (spot → player) ray so the push
   * animation's forward-reaching frame (3rd-phase apex — both arms fully
   * extended) lands the hand against the visible surface instead of clipping
   * through it.
   *
   * Target = colliderRadius (distance from spot centre to the object's visible
   * surface) + a timed reach offset. The push clip starts with bent arms, then
   * leans/stretches forward; parking the root at one fixed distance either
   * clips the full-extension frame or leaves a side-view gap at the start.
   *
   * Falls back to a coarser surfaceRadius-based target if colliderRadius
   * isn't set on the spot. Spots registered by Nature, Interactables, and
   * discoverPushSpots all set it, so the fallback shouldn't normally fire.
   */
  _snapToPushDistance(spot, heldFor = 0) {
    const reach = this._pushReachAt(heldFor);
    const surface = (spot.colliderRadius != null)
      ? spot.colliderRadius
      : Math.max(0, spot.surfaceRadius - 1.2);
    const target = surface + reach;
    const px = this.player.position.x;
    const pz = this.player.position.z;
    const dx = px - spot.position.x;
    const dz = pz - spot.position.z;
    const d = Math.hypot(dx, dz);
    if (d <= 0.05) return; // standing on the spot — nothing sensible to do
    const k = target / d;
    const nx = spot.position.x + dx * k;
    const nz = spot.position.z + dz * k;
    const py = this.player.position.y;
    if (this.player.body) this.player.body.teleport(nx, py, nz);
    this.player.group.position.set(nx, py, nz);
  }

  _pushReachAt(heldFor) {
    const START_REACH = 0.48;
    const FULL_REACH = 0.98;
    const t = Math.min(1, Math.max(0, (heldFor - 0.18) / 0.9));
    const eased = t * t * (3 - 2 * t);
    return START_REACH + (FULL_REACH - START_REACH) * eased;
  }

  _jokeAt(slot) {
    if (!this._pushJokeDeck.length) return null;
    if (slot >= this._pushJokeDeck.length) {
      const last = this._activeJokeText;
      const next = shuffleCopy(this._pushJokeDeck);
      if (next[0] === last && next.length > 1) {
        const tmp = next[0]; next[0] = next[1]; next[1] = tmp;
      }
      this._pushJokeDeck = next;
      slot = 0;
    }
    const text = this._pushJokeDeck[slot];
    this._activeJokeText = text;
    return text;
  }

  tick(playerPosition, delta) {
    this._elapsed += delta;

    // Nearest push spot in range AND in the player's forward arc. The facing
    // check makes the hint context-aware: turning away from a rock hides the
    // prompt, and the keydown gate on currentPushSpot ensures P doesn't fire
    // into empty space behind the player.
    let nearestSpot = null;
    let bestDist = Infinity;
    for (const spot of this.pushSpots) {
      const d = playerPosition.distanceTo(spot.position);
      if (d > spot.surfaceRadius || d >= bestDist) continue;
      if (!this.#facing(spot.position, PUSH_FACING_MIN_DOT)) continue;
      nearestSpot = spot;
      bestDist = d;
    }
    this.currentPushSpot = nearestSpot;

    if (this.globalPushActive) {
      this._hidePushHint();
      const heldFor = this.pushStartMs ? (performance.now() - this.pushStartMs) / 1000 : this._elapsed - this.pushStartSec;
      if (this.activePushSpot) this._snapToPushDistance(this.activePushSpot, heldFor);
      if (heldFor > PUSH_JOKE_DELAY) {
        const slot = Math.floor((heldFor - PUSH_JOKE_DELAY) / PUSH_JOKE_INTERVAL);
        const text = this._jokeAt(slot);
        if (text) this._showPushJoke(text);
      } else {
        this._hidePushJoke();
      }
    } else {
      this._hidePushJoke();
      const billboardFocused = this.billboardInteraction && this.billboardInteraction.activeIndex >= 0;
      const contactOpen = this.billboardInteraction && this.billboardInteraction.contactOpen;
      const otherActive = this.activeHoldLoop || this.activeZoneLoop || this.oneShotActive || billboardFocused || contactOpen;
      if (nearestSpot && !otherActive) this._showPushHint();
      else this._hidePushHint();
    }

    if (this.oneShotActive && this._elapsed >= this.oneShotActive.untilSec) {
      this.controller.paused = false;
      if (this.playerCamera) this.playerCamera.releaseActionZoom();
      this.oneShotActive = null;
    }

    if (this.combatState && this.combatState.ready) {
      this.combatState.timer -= delta;
      if (this.combatState.timer <= 0) this.combatState = null;
    }

    if (this.activeZoneLoop) {
      const d = playerPosition.distanceTo(this.activeZoneLoop.position);
      if (d > this.activeZoneLoop.radius + 0.5) this._exitZoneLoop();
    }

    let closest = null;
    let bestTrigDist = Infinity;
    for (const t of this.triggers) {
      const d = playerPosition.distanceTo(t.position);
      if (d <= t.radius && d < bestTrigDist) {
        closest = t;
        bestTrigDist = d;
      }
    }
    this.candidate = closest;

    if (closest && closest.mode === 'zoneLoop' && !this.activeZoneLoop && !this.activeHoldLoop && !this.oneShotActive) {
      this._enterZoneLoop(closest);
    }

    if (this.activeHoldLoop) {
      this._hidePrompt();
    } else if (this.activeZoneLoop) {
      const t = this.activeZoneLoop;
      const label = (t.cycleActions && t.cycleActions.length)
        ? (t.label + ' (E to switch, move to leave)')
        : (t.label + ' (move to leave)');
      this._showPrompt(label);
    } else if (closest) {
      if (closest.mode === 'combat' && this.combatState && this.combatState.trigger === closest && this.combatState.ready) {
        this._showPrompt(closest.punchLabel || closest.label);
      } else {
        this._showPrompt(closest.label);
      }
    } else {
      this._hidePrompt();
      if (this.combatState && this.combatState.trigger !== this.candidate) this.combatState = null;
    }
  }

  _startHoldLoop(t) {
    if (!this.player.startLoopAction(t.action)) return;
    this.controller.paused = true;
    this.activeHoldLoop = t;
    if (this.playerCamera) this.playerCamera.applyActionZoom();
    if (this.audio) this.audio.playInteract();
    if (t.onActivate) t.onActivate();
  }

  _endHoldLoop() {
    const t = this.activeHoldLoop;
    this.activeHoldLoop = null;
    this.player.stopLoopAction();
    this.controller.paused = false;
    if (this.playerCamera) this.playerCamera.releaseActionZoom();
    if (t && t.onRelease) t.onRelease();
  }

  _startOneShot(t) {
    const action = this.player.character && this.player.character.actions[t.action];
    const clip = action && action.getClip();
    const duration = (clip && clip.duration) || 1.5;
    if (!this.player.performAction(t.action, { interruptible: false, then: 'idle' })) return;
    this.controller.paused = true;
    this.oneShotActive = { trigger: t, untilSec: this._elapsed + duration + 0.1 };
    if (this.playerCamera) this.playerCamera.applyActionZoom();
    if (this.audio) this.audio.playInteract();
    if (t.onActivate) t.onActivate();
  }

  _enterZoneLoop(t) {
    if (!this.player.startLoopAction(t.action)) return;
    this.activeZoneLoop = t;
    t._cycleIndex = -1;
    if (this.playerCamera) this.playerCamera.applyActionZoom();
    if (this.audio) this.audio.playInteract();
    if (t.onActivate) t.onActivate();
  }

  _exitZoneLoop() {
    const t = this.activeZoneLoop;
    this.activeZoneLoop = null;
    this.player.stopLoopAction();
    if (this.playerCamera) this.playerCamera.releaseActionZoom();
    if (t && t.onRelease) t.onRelease();
  }

  _advanceCombat(t) {
    // Direction check — the punch impulse / bag swing both read
    // `player.group.rotation.y`, so a player facing AWAY from the bag would
    // make the bag swing the wrong direction. Refuse entry / punch if the
    // player isn't roughly facing the bag (dot(forward, toBag) > 0.5,
    // i.e. within ±60°). The check is intentionally lenient so a slight
    // mis-aim doesn't feel like the input is broken.
    if (!this.#facing(t.position, 0.5)) {
      this._showBlockedMessage('Face the bag to square up');
      return;
    }
    if (!this.combatState || this.combatState.trigger !== t) {
      const stance = t.stanceAction || 'fightStance';
      const action = this.player.character && this.player.character.actions[stance];
      const clip = action && action.getClip();
      const duration = (clip && clip.duration) || 1.5;
      if (!this.player.performAction(stance, { interruptible: true, then: 'idle' })) {
        return this._commitPunch(t);
      }
      if (this.audio) this.audio.playInteract();
      this.combatState = { trigger: t, ready: true, timer: COMBAT_RESET_SECONDS };
      this.controller.paused = true;
      this.oneShotActive = { trigger: t, untilSec: this._elapsed + duration + 0.1 };
    } else if (this.combatState.ready) {
      this._commitPunch(t);
    }
  }

  /**
   * True when the player's forward (yaw) is within an arc of the target XZ
   * point. `minDot` = cos(half-arc); 0.5 ⇒ ±60°, 0.0 ⇒ ±90°.
   */
  #facing(targetPos, minDot) {
    const px = this.player.position.x;
    const pz = this.player.position.z;
    const dx = targetPos.x - px;
    const dz = targetPos.z - pz;
    const len = Math.hypot(dx, dz);
    if (len < 0.05) return true; // standing on the target
    const yaw = this.player.group.rotation.y;
    // PlayerController emits facing = atan2(intent.x, intent.z) and the
    // character mirrors that — so forward in world space is
    // (sin(yaw), 0, cos(yaw)).
    const fx = Math.sin(yaw);
    const fz = Math.cos(yaw);
    const dot = (fx * dx + fz * dz) / len;
    return dot >= minDot;
  }

  _commitPunch(t) {
    const punch = t.action;
    const action = this.player.character && this.player.character.actions[punch];
    const clip = action && action.getClip();
    const duration = (clip && clip.duration) || 1.5;
    if (!this.player.performAction(punch, { interruptible: false, then: 'idle' })) return;
    this.controller.paused = true;
    this.oneShotActive = { trigger: t, untilSec: this._elapsed + duration + 0.1 };
    if (this.audio) this.audio.playInteract();
    this.combatState = null;
    if (t.onActivate) t.onActivate();
  }
}
