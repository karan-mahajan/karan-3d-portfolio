/**
 * Achievements — trackable unlocks across exploration, portfolio
 * engagement, actions, world toggles, mini-games, time milestones, and
 * hidden ones. Each carries a `rarity` (common/rare/epic/legendary) that
 * drives the toast + panel theming and the unlock chime. Persists progress,
 * unlocked IDs, and which unlocks have been *seen* to localStorage so
 * refreshes keep state.
 *
 * Lifecycle:
 *   1. Build once in App ctor.
 *   2. Subscribe AchievementToast (and the audio chime) via onUnlock().
 *   3. App.#tick calls achievements.tick(delta, ctx) every frame.
 *   4. Other modules (Interaction, ActionPrompts, TimeOfDay, Rain,
 *      Thunderstorm, Footprints, Player) call the on*() trigger methods
 *      when their events fire.
 *
 * Sets that need to survive page reloads (visited sections, viewed
 * projects, edges, pushed objects) are mirrored into `this.progress`
 * under reserved `_` keys so the same localStorage blob restores them.
 */

const STORAGE_PROGRESS = 'karan-portfolio:achievements:progress';
const STORAGE_UNLOCKED = 'karan-portfolio:achievements:unlocked';
const STORAGE_SEEN     = 'karan-portfolio:achievements:seen';
const STORAGE_TIME     = 'karan-portfolio:achievements:time';
// Cumulative-time celebrations beyond the last milestone fire every N
// minutes (the user explicitly asked for "every 5 minutes"). Bounded by
// the milestone achievements below — the perpetual party kicks in only
// past the longest milestone.
const PARTY_INTERVAL_SEC = 5 * 60;

// Static metadata for every achievement. `rarity` (common | rare | epic |
// legendary) drives toast/panel theming + the unlock chime; omit it to
// default to 'common'. Targets that key off world state (project count,
// experience sign count) are declared here so the rest of the system can
// stay numeric.
const ACHIEVEMENTS = [
  // === EXPLORATION (9) ===
  { id: 'journey_begins',  name: 'Journey Begins',   description: 'Start your journey',                icon: '🚀', category: 'exploration', target: 1,   secret: false },
  { id: 'first_steps',     name: 'First Steps',      description: 'Move for the first time',           icon: '👟', category: 'exploration', target: 1,   secret: false },
  { id: 'speed_demon',     name: 'Speed Demon',      description: 'Sprint for 5 seconds straight',     icon: '💨', category: 'exploration', target: 1,   secret: false, rarity: 'rare' },
  { id: 'grand_tour',      name: 'The Grand Tour',   description: 'Visit all 4 portfolio sections',    icon: '🗺️', category: 'exploration', target: 4,   secret: false, rarity: 'epic' },
  { id: 'perimeter_walk',  name: 'Perimeter Walk',   description: 'Reach all 4 edges of the island',   icon: '🧭', category: 'exploration', target: 4,   secret: false, rarity: 'epic' },
  { id: 'off_script',      name: 'Going Off Script', description: 'Walk 15m from any path',            icon: '🌿', category: 'exploration', target: 1,   secret: false, rarity: 'rare' },
  { id: 'aquaman',         name: 'Aquaman',          description: 'Wade waist-deep into the ocean',    icon: '🏊', category: 'exploration', target: 1,   secret: false, rarity: 'rare' },
  { id: 'night_swimmer',   name: 'Night Swimmer',    description: 'Enter the water at night',          icon: '🌊', category: 'exploration', target: 1,   secret: false, rarity: 'rare' },
  { id: 'fast_travel',     name: 'Fast Traveler',    description: 'Teleport via the map',              icon: '✈️', category: 'exploration', target: 1,   secret: false, rarity: 'rare' },

  // === PORTFOLIO ENGAGEMENT (6) ===
  { id: 'curious_dev',       name: 'Curious Dev',          description: 'View your first project',       icon: '🔍', category: 'portfolio', target: 1, secret: false },
  { id: 'full_stack_review', name: 'Full Stack Review',    description: 'View all 5 project billboards', icon: '💻', category: 'portfolio', target: 5, secret: false, rarity: 'epic' },
  { id: 'hired',             name: 'Hired!',               description: 'Open the Contact section',      icon: '📞', category: 'portfolio', target: 1, secret: false },
  { id: 'due_diligence',     name: 'Due Diligence',        description: 'View every experience sign',    icon: '📋', category: 'portfolio', target: 5, secret: false, rarity: 'epic' },
  { id: 'skill_scanned',     name: 'Skill Scanned',        description: 'View the skills display',       icon: '⚡', category: 'portfolio', target: 1, secret: false },
  { id: 'complete_package',  name: 'The Complete Package', description: 'View every interactive element',icon: '🏆', category: 'portfolio', target: 1, secret: false, rarity: 'legendary' },

  // === ACTIONS (7) ===
  { id: 'parkour',          name: 'Parkour!',          description: 'Do a backflip',           icon: '🤸', category: 'actions', target: 1,   secret: false },
  { id: 'cirque_du_code',   name: 'Cirque du Code',    description: 'Do a cartwheel',          icon: '🎪', category: 'actions', target: 1,   secret: false },
  { id: 'bully',            name: 'Bully',             description: 'Push an object',          icon: '🫸', category: 'actions', target: 1,   secret: false },
  { id: 'cloud_jumper',     name: 'Cloud Jumper',      description: 'Jump 20 times',           icon: '☁️', category: 'actions', target: 20,  secret: false, rarity: 'rare' },
  { id: 'footprint_artist', name: 'Footprint Artist',  description: 'Leave 40 footprints',     icon: '👣', category: 'actions', target: 40,  secret: false, rarity: 'rare' },
  { id: 'afk',              name: 'AFK',               description: 'Stand still for 30 seconds', icon: '🧘', category: 'actions', target: 1,  secret: false },
  { id: 'marathon_dev',     name: 'Marathon Dev',      description: 'Walk/run 500 total meters', icon: '🏃', category: 'actions', target: 500, secret: false, rarity: 'epic' },

  // === MINI-GAMES (3) ===
  { id: 'painter',        name: 'Splash of Colour', description: 'Paint a sculpture in the Colour Garden', icon: '🎨', category: 'games', target: 1, secret: false, rarity: 'rare' },
  { id: 'master_painter', name: 'Master Painter',   description: 'Paint every sculpture in the garden',    icon: '🌈', category: 'games', target: 1, secret: false, rarity: 'legendary' },
  { id: 'striker',        name: 'Striker',          description: 'Kick the football',                      icon: '⚽', category: 'games', target: 1, secret: false, rarity: 'rare' },

  // === WEATHER & WORLD (6) ===
  { id: 'night_owl',       name: 'Night Owl',       description: 'Switch to night mode',           icon: '🦉', category: 'world', target: 1, secret: false },
  { id: 'early_bird',      name: 'Early Bird',      description: 'Switch back to day mode',        icon: '🐦', category: 'world', target: 1, secret: false },
  { id: 'rain_maker',      name: 'Rain Maker',      description: 'Toggle rain on',                 icon: '🌧️', category: 'world', target: 1, secret: false },
  { id: 'thor_mode',       name: 'Thor Mode',       description: 'Trigger lightning manually',     icon: '⚡', category: 'world', target: 1, secret: false },
  { id: 'storm_survivor',  name: 'Storm Survivor',  description: 'Stand in rain for 60 seconds',   icon: '☔', category: 'world', target: 1, secret: false, rarity: 'rare' },
  { id: 'snow_day',        name: 'Snow Day',        description: 'Witness the first snowfall',      icon: '❄️', category: 'world', target: 1, secret: false, rarity: 'rare' },

  // === SECRET (6) — names hidden until unlocked ===
  { id: 'pushy',             name: 'The Bulldozer', description: 'Push 5 different objects',                  icon: '🚜',  category: 'secret', target: 5, secret: true, rarity: 'epic' },
  { id: 'water_flip',        name: 'Splashdown',    description: 'Do a backflip in the water',                icon: '🐬',  category: 'secret', target: 1, secret: true, rarity: 'epic' },
  { id: 'storm_chaser',      name: 'Storm Chaser',  description: 'Trigger lightning 5 times in one session', icon: '🌩️',  category: 'secret', target: 5, secret: true, rarity: 'epic' },
  { id: 'distance_guesser',  name: 'Eagle Eye',     description: 'Guess an island distance within 10m',       icon: '🏝️',  category: 'secret', target: 1, secret: true, rarity: 'epic' },
  { id: 'distance_master',   name: 'Cartographer',  description: 'Guess an island distance exactly right',    icon: '🎯',  category: 'secret', target: 1, secret: true, rarity: 'legendary' },
  { id: 'lava_death',        name: 'Floor is Lava', description: 'Get WASTED in the molten pool',             icon: '🌋',  category: 'secret', target: 1, secret: true, rarity: 'epic' },

  // === TIME (5) — cumulative time spent in the world, in seconds ===
  // Counter targets are seconds so the progress bar fills smoothly. The
  // displayed description still reads in minutes for readability.
  { id: 'time_5min',  name: 'Tourist',    description: 'Spend 5 minutes exploring',  icon: '⏱️', category: 'time', target: 5  * 60, secret: false },
  { id: 'time_10min', name: 'Sightseer',  description: 'Spend 10 minutes exploring', icon: '🧳', category: 'time', target: 10 * 60, secret: false, rarity: 'rare' },
  { id: 'time_15min', name: 'Wanderer',   description: 'Spend 15 minutes exploring', icon: '🚶', category: 'time', target: 15 * 60, secret: false, rarity: 'rare' },
  { id: 'time_30min', name: 'Local',      description: 'Spend 30 minutes exploring', icon: '🏘️', category: 'time', target: 30 * 60, secret: false, rarity: 'epic' },
  { id: 'time_60min', name: 'Resident',   description: 'Spend 60 minutes exploring', icon: '🏡', category: 'time', target: 60 * 60, secret: false, rarity: 'legendary' },
];

const TIME_MILESTONES = [
  { id: 'time_5min',  seconds: 5  * 60 },
  { id: 'time_10min', seconds: 10 * 60 },
  { id: 'time_15min', seconds: 15 * 60 },
  { id: 'time_30min', seconds: 30 * 60 },
  { id: 'time_60min', seconds: 60 * 60 },
];
// After the last achievement-tracked milestone, a generic "🎉 X minutes
// here!" toast fires every 5 minutes (PARTY_INTERVAL_SEC). Each toast goes
// through the same Achievements.onUnlock listener pipe via a synthetic
// achievement-shaped object.
const PARTY_THRESHOLD_SEC = TIME_MILESTONES[TIME_MILESTONES.length - 1].seconds;

export class Achievements {
  constructor() {
    this.achievements = ACHIEVEMENTS;
    this.progress = this.#loadProgress();
    this.unlocked = new Set(this.#loadUnlocked());
    // IDs whose unlock the user has already seen in the panel. Anything
    // unlocked-but-unseen drives the "NEW" badge on the trophy button.
    // First run after this feature shipped: no seen-store exists yet, so seed
    // it with everything already unlocked — otherwise old earned achievements
    // would all flash a spurious "NEW".
    let seenInit = this.#loadSeen();
    if (seenInit === null) {
      seenInit = Array.from(this.unlocked);
      this.seen = new Set(seenInit);
      this.#saveSeen();
    } else {
      this.seen = new Set(seenInit);
    }
    this.listeners = [];

    // Counter mirrors. Persisted via `progress[id]` for the numeric ones;
    // the set-valued ones are mirrored to `progress._*` keys so the rebuild
    // path on next load is the same blob.
    this._sessionLightning = 0; // session-only; never restored
    this._sprintTimer = 0;
    this._idleTimer = 0;
    this._rainTimer = 0;
    this._totalDistance = this.progress.marathon_dev || 0;
    this._jumpCount = this.progress.cloud_jumper || 0;
    this._footprintCount = this.progress.footprint_artist || 0;
    this._visitedSections = new Set(this.progress._visitedSections || []);
    this._visitedEdges    = new Set(this.progress._visitedEdges    || []);
    this._viewedProjects  = new Set(this.progress._viewedProjects  || []);
    this._viewedExperience = new Set(this.progress._viewedExperience || []);
    this._pushedObjects   = new Set(this.progress._pushedObjects   || []);
    this._lastPosition = null;

    // ── Cumulative time tracking ─────────────────────────────────────────
    // Stored as seconds (integer) across sessions. Restored on construction
    // so the milestones survive a reload. _lastPartyAt is the cumulative
    // second-count at which the most recent "🎉 X minutes" toast fired —
    // also persisted so reloads don't re-trigger past parties.
    const timeBlob = this.#loadTime();
    this._timeSeconds = timeBlob.seconds || 0;
    this._lastPartyAt = timeBlob.lastPartyAt || 0;
    // Re-seed milestone progress in case storage was wiped after unlock.
    for (const m of TIME_MILESTONES) {
      if (!this.unlocked.has(m.id)) {
        this.progress[m.id] = Math.min(this._timeSeconds, m.seconds);
      }
    }
  }

  /** Subscribe to unlock events. Callback receives the achievement object. */
  onUnlock(callback) {
    this.listeners.push(callback);
  }

  /** Increment progress on an achievement; auto-unlocks at target. */
  increment(id, amount = 1) {
    if (this.unlocked.has(id)) return;
    const a = this.achievements.find((x) => x.id === id);
    if (!a) return;
    this.progress[id] = (this.progress[id] || 0) + amount;
    if (this.progress[id] >= a.target) this.#unlock(a);
    this.#saveProgress();
  }

  /** Direct one-shot unlock. */
  trigger(id) {
    if (this.unlocked.has(id)) return;
    const a = this.achievements.find((x) => x.id === id);
    if (!a) return;
    this.progress[id] = a.target;
    this.#unlock(a);
  }

  /** Replace numeric progress; auto-unlocks if it crosses the target. */
  setProgress(id, value) {
    if (this.unlocked.has(id)) return;
    const a = this.achievements.find((x) => x.id === id);
    if (!a) return;
    const cur = this.progress[id] || 0;
    if (value === cur) return; // no-op; avoids a localStorage write per frame
    this.progress[id] = value;
    if (value >= a.target) this.#unlock(a);
    this.#saveProgress();
  }

  /**
   * Per-frame driver. `ctx` carries the live world state App.js already
   * computes — distance from spawn, water state, day/night, rain.
   *
   * Time-based achievements (Speed Demon, AFK, Storm Survivor) accumulate
   * timers here; per-edge / per-section state lives in the sets above.
   */
  tick(delta, ctx) {
    const { playerPos, moving, running, inWater, waterDepth, isNight, isRaining, isSnowing } = ctx;

    if (isSnowing) this.trigger('snow_day');

    // Cumulative time on site — even during idle. Persisted every ~5s
    // (not every frame) so the localStorage write doesn't get hammered.
    this._timeSeconds += delta;
    this._timeWriteTimer = (this._timeWriteTimer || 0) + delta;
    if (this._timeWriteTimer >= 5) {
      this._timeWriteTimer = 0;
      this.#saveTime();
    }
    this.#tickTimeMilestones();

    if (moving) this.trigger('first_steps');

    if (running && moving) {
      this._sprintTimer += delta;
      if (this._sprintTimer >= 5) this.trigger('speed_demon');
    } else {
      this._sprintTimer = 0;
    }

    if (!moving) {
      this._idleTimer += delta;
      if (this._idleTimer >= 30) this.trigger('afk');
    } else {
      this._idleTimer = 0;
    }

    if (isRaining) {
      this._rainTimer += delta;
      if (this._rainTimer >= 60) this.trigger('storm_survivor');
    } else {
      this._rainTimer = 0;
    }

    // Marathon Dev — accumulate XZ distance. Cap per-tick to drop teleports
    // (respawn at origin, soft-clamp at radius 52, etc.) without losing real
    // travel.
    if (this._lastPosition && moving) {
      const dx = playerPos.x - this._lastPosition.x;
      const dz = playerPos.z - this._lastPosition.z;
      const dist = Math.sqrt(dx * dx + dz * dz);
      if (dist < 5) {
        this._totalDistance += dist;
        this.setProgress('marathon_dev', Math.floor(this._totalDistance));
      }
    }
    this._lastPosition = { x: playerPos.x, z: playerPos.z };

    if (inWater && waterDepth > 0.6) this.trigger('aquaman');
    if (inWater && isNight) this.trigger('night_swimmer');

    // Perimeter Walk — only update at radius > 35 so we don't keep poking
    // the set/localStorage every frame near spawn.
    const r = Math.sqrt(playerPos.x ** 2 + playerPos.z ** 2);
    if (r > 35) {
      let changed = false;
      if (playerPos.x >  30 && !this._visitedEdges.has('east'))  { this._visitedEdges.add('east');  changed = true; }
      if (playerPos.x < -30 && !this._visitedEdges.has('west'))  { this._visitedEdges.add('west');  changed = true; }
      if (playerPos.z >  30 && !this._visitedEdges.has('north')) { this._visitedEdges.add('north'); changed = true; }
      if (playerPos.z < -30 && !this._visitedEdges.has('south')) { this._visitedEdges.add('south'); changed = true; }
      if (changed) {
        this.progress._visitedEdges = Array.from(this._visitedEdges);
        this.setProgress('perimeter_walk', this._visitedEdges.size);
      }
    }

    // Grand Tour is updated whenever a new section is visited via
    // onSectionVisited; reflect the current size here too in case state was
    // restored from storage at boot.
    this.setProgress('grand_tour', this._visitedSections.size);

    // Complete Package — fires once all five named portfolio unlocks land.
    if (!this.unlocked.has('complete_package')) {
      const portfolioIds = ['curious_dev', 'full_stack_review', 'hired', 'due_diligence', 'skill_scanned'];
      if (portfolioIds.every((id) => this.unlocked.has(id))) this.trigger('complete_package');
    }
  }

  // ── External trigger methods ────────────────────────────────────────────

  onProjectViewed(projectName) {
    if (!projectName) return;
    if (!this._viewedProjects.has(projectName)) {
      this._viewedProjects.add(projectName);
      this.progress._viewedProjects = Array.from(this._viewedProjects);
      this.trigger('curious_dev');
      this.setProgress('full_stack_review', this._viewedProjects.size);
    }
  }

  /** Player walked into one of the cardinal sections. */
  onSectionVisited(section) {
    if (!section || this._visitedSections.has(section)) return;
    this._visitedSections.add(section);
    this.progress._visitedSections = Array.from(this._visitedSections);
    if (section === 'contact') this.trigger('hired');
    if (section === 'skills') this.trigger('skill_scanned');
    this.setProgress('grand_tour', this._visitedSections.size);
  }

  /** Player walked up to a specific experience sign (idx 0..n-1). */
  onExperienceSignViewed(idx) {
    if (idx == null) return;
    const key = String(idx);
    if (this._viewedExperience.has(key)) return;
    this._viewedExperience.add(key);
    this.progress._viewedExperience = Array.from(this._viewedExperience);
    this.setProgress('due_diligence', this._viewedExperience.size);
  }

  onBackflip(inWater = false) {
    this.trigger('parkour');
    if (inWater) this.trigger('water_flip');
  }

  onCartwheel() { this.trigger('cirque_du_code'); }

  onPush(objectId) {
    this.trigger('bully');
    if (objectId == null) return;
    const key = String(objectId);
    if (!this._pushedObjects.has(key)) {
      this._pushedObjects.add(key);
      this.progress._pushedObjects = Array.from(this._pushedObjects);
      this.setProgress('pushy', this._pushedObjects.size);
    }
  }

  onJump() {
    this._jumpCount++;
    this.setProgress('cloud_jumper', this._jumpCount);
  }

  onFootprint() {
    this._footprintCount++;
    this.setProgress('footprint_artist', this._footprintCount);
  }

  onToggleNight() { this.trigger('night_owl'); }
  onToggleDay()   { this.trigger('early_bird'); }
  onToggleRain()  { this.trigger('rain_maker'); }

  onLightning() {
    this.trigger('thor_mode');
    this._sessionLightning++;
    this.setProgress('storm_chaser', this._sessionLightning);
  }

  onOffPath() { this.trigger('off_script'); }

  /** Player used a map marker to fast-travel between sections. */
  onFastTravel() { this.trigger('fast_travel'); }

  /** Player kicked the football. */
  onFootballKick() { this.trigger('striker'); }

  /** Player sank in the lava and got the WASTED card. */
  onWasted() { this.trigger('lava_death'); }

  /** A Colour Garden sculpture was painted. `allPainted` is true once every
   *  sculpture in the field has colour. */
  onStatuePainted(allPainted = false) {
    this.trigger('painter');
    if (allPainted) this.trigger('master_painter');
  }

  /** User clicked "Start your journey" on the welcome overlay. Also fires
   *  on subsequent reloads if the user never completed it before. */
  onJourneyBegin() { this.trigger('journey_begins'); }

  // ── Cumulative time + perpetual party toasts ────────────────────────

  /** Walk every time milestone and unlock any whose target the cumulative
   *  counter has crossed. Past the last milestone, fire a generic "🎉 X
   *  minutes here!" toast every PARTY_INTERVAL_SEC. */
  #tickTimeMilestones() {
    for (const m of TIME_MILESTONES) {
      if (this.unlocked.has(m.id)) continue;
      // Live progress so the bar fills smoothly inside the panel.
      const before = this.progress[m.id] || 0;
      const target = Math.min(this._timeSeconds, m.seconds);
      if (target > before) this.setProgress(m.id, Math.floor(target));
    }
    // Perpetual celebration past the longest milestone — fires once per
    // 5-min mark and persists `_lastPartyAt` so reload doesn't re-spam.
    if (this._timeSeconds >= PARTY_THRESHOLD_SEC + PARTY_INTERVAL_SEC) {
      const intervalsSinceThreshold = Math.floor(
        (this._timeSeconds - PARTY_THRESHOLD_SEC) / PARTY_INTERVAL_SEC,
      );
      const partyAt = PARTY_THRESHOLD_SEC + intervalsSinceThreshold * PARTY_INTERVAL_SEC;
      if (partyAt > this._lastPartyAt) {
        this._lastPartyAt = partyAt;
        this.#saveTime();
        this.#emitParty(Math.floor(partyAt / 60));
      }
    }
  }

  /** Fire a synthetic achievement-shaped event so the toast + chime
   *  pipeline shows a per-5-minutes celebration without polluting the
   *  panel's achievement list. */
  #emitParty(minutes) {
    const synthetic = {
      id: `party_${minutes}min`,
      name: `${minutes} Minutes Here!`,
      description: 'Thanks for sticking around — enjoy the world.',
      icon: '🎉',
      category: 'time',
      target: minutes,
      rarity: 'rare',
      _synthetic: true,
    };
    for (const cb of this.listeners) {
      try { cb(synthetic); } catch (err) { console.warn('[Achievements] party listener error:', err); }
    }
  }

  #loadTime() {
    try { return JSON.parse(localStorage.getItem(STORAGE_TIME)) || {}; }
    catch { return {}; }
  }

  #saveTime() {
    try {
      localStorage.setItem(STORAGE_TIME, JSON.stringify({
        seconds: Math.floor(this._timeSeconds),
        lastPartyAt: Math.floor(this._lastPartyAt),
      }));
    } catch (err) { console.warn('[Achievements] time save failed:', err); }
  }

  /** Total seconds the user has spent on the site across all sessions. */
  getCumulativeSeconds() { return this._timeSeconds; }

  // ── Internal ────────────────────────────────────────────────────────────

  #unlock(a) {
    if (this.unlocked.has(a.id)) return;
    this.unlocked.add(a.id);
    this.#saveUnlocked();
    this.#saveProgress();
    for (const cb of this.listeners) {
      try { cb(a); } catch (err) { console.warn('[Achievements] listener error:', err); }
    }
  }

  #loadProgress() {
    try { return JSON.parse(localStorage.getItem(STORAGE_PROGRESS)) || {}; }
    catch { return {}; }
  }

  #saveProgress() {
    try { localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(this.progress)); }
    catch (err) { console.warn('[Achievements] progress save failed:', err); }
  }

  #loadUnlocked() {
    try { return JSON.parse(localStorage.getItem(STORAGE_UNLOCKED)) || []; }
    catch { return []; }
  }

  #saveUnlocked() {
    try { localStorage.setItem(STORAGE_UNLOCKED, JSON.stringify(Array.from(this.unlocked))); }
    catch (err) { console.warn('[Achievements] unlocked save failed:', err); }
  }

  /** Returns the stored array, or null when the seen-store has never been
   *  written (so the constructor can seed it from already-unlocked IDs). */
  #loadSeen() {
    try {
      const raw = localStorage.getItem(STORAGE_SEEN);
      return raw === null ? null : (JSON.parse(raw) || []);
    } catch { return null; }
  }

  #saveSeen() {
    try { localStorage.setItem(STORAGE_SEEN, JSON.stringify(Array.from(this.seen))); }
    catch (err) { console.warn('[Achievements] seen save failed:', err); }
  }

  /** Mark every currently-unlocked achievement as seen (called when the panel
   *  opens) so the trophy "NEW" badge clears. */
  markAllSeen() {
    let changed = false;
    for (const id of this.unlocked) if (!this.seen.has(id)) { this.seen.add(id); changed = true; }
    if (changed) this.#saveSeen();
    return changed;
  }

  /** Count of unlocked achievements the user hasn't opened the panel to see. */
  getUnseenCount() {
    let n = 0;
    for (const id of this.unlocked) if (!this.seen.has(id)) n++;
    return n;
  }

  /** Read-only view for the panel UI. Secret achievements stay obscured
   *  until they unlock. */
  getAll() {
    return this.achievements.map((a) => {
      const unlocked = this.unlocked.has(a.id);
      const obscured = a.secret && !unlocked;
      return {
        ...a,
        rarity: a.rarity || 'common',
        unlocked,
        seen: this.seen.has(a.id),
        current: this.progress[a.id] || 0,
        displayName: obscured ? '???' : a.name,
        displayDescription: obscured ? 'Keep exploring to find out…' : a.description,
        displayIcon: obscured ? '🔒' : a.icon,
      };
    });
  }

  getUnlockedCount() { return this.unlocked.size; }
  getTotalCount()    { return this.achievements.length; }
  /** True once every achievement is unlocked — drives the 100% celebration. */
  isAllComplete()    { return this.unlocked.size >= this.achievements.length; }

  /** Per-category {unlocked,total} tallies for the panel tab badges. */
  getCategoryStats() {
    const stats = {};
    for (const a of this.achievements) {
      const s = (stats[a.category] ||= { unlocked: 0, total: 0 });
      s.total++;
      if (this.unlocked.has(a.id)) s.unlocked++;
    }
    return stats;
  }
}
