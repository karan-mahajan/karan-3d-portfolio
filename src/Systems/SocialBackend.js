/**
 * Client data layer for the persisted social features (likes / whispers /
 * visitor count). Talks to the Vercel serverless functions under /api over
 * plain fetch — the database credentials live server-side, never in this
 * bundle. All methods degrade gracefully: a network error or an unconfigured
 * backend resolves to a safe value instead of throwing, so the 3D world keeps
 * running even when the API is unreachable (e.g. a bare `vite` dev server).
 *
 * State is intentionally tiny + observable: consumers (SocialHud, GuestbookTree)
 * subscribe via onChange and re-read the public fields after each call.
 */
const VISITOR_KEY = "karan-portfolio:visitor-id";
const LIKED_KEY = "karan-portfolio:liked";

export class SocialBackend {
  constructor() {
    this.visitorId = this.#loadVisitorId();

    // Public, read-only-ish snapshot. Updated in place; call onChange listeners
    // after each mutation.
    this.likes = 0;
    this.visitors = 0;
    this.liked = localStorage.getItem(LIKED_KEY) === "1";
    this.whispers = [];
    this.configured = true; // flipped false if the API reports no DB
    this.ready = false; // true after the first successful loadState

    this._listeners = new Set();
    this._likeInFlight = false;
  }

  // ── Subscription ───────────────────────────────────────────────────────────
  onChange(fn) {
    this._listeners.add(fn);
    return () => this._listeners.delete(fn);
  }
  #emit() {
    for (const fn of this._listeners) {
      try {
        fn(this);
      } catch (err) {
        console.warn("[SocialBackend] listener error:", err);
      }
    }
  }

  // ── Visitor identity (anonymous, per-browser) ──────────────────────────────
  #loadVisitorId() {
    let id = null;
    try {
      id = localStorage.getItem(VISITOR_KEY);
    } catch {
      /* private mode — fall through to an ephemeral id */
    }
    if (!id) {
      id =
        (globalThis.crypto?.randomUUID?.() ??
          `v-${Math.random().toString(36).slice(2)}-${Math.random()
            .toString(36)
            .slice(2)}`).slice(0, 64);
      try {
        localStorage.setItem(VISITOR_KEY, id);
      } catch {
        /* ignore */
      }
    }
    return id;
  }

  // ── Network ─────────────────────────────────────────────────────────────────
  /**
   * Fetch the full snapshot + register this visit. Retries a few times on a
   * transient failure (e.g. the page loaded a beat before the dev API was ready)
   * so a single early blip doesn't leave the features stuck "offline" until a
   * manual reload. `configured` is driven ONLY by the server's explicit answer —
   * a network error never brands the backend unconfigured.
   */
  async loadState(attempt = 0) {
    try {
      const res = await fetch(
        `/api/state?v=${encodeURIComponent(this.visitorId)}`,
        { headers: { accept: "application/json" } },
      );
      if (!res.ok) throw new Error(`state ${res.status}`);
      const data = await res.json();
      this.configured = data.configured !== false;
      this.likes = data.likes ?? 0;
      this.visitors = data.visitors ?? 0;
      this.liked = !!data.liked || this.liked;
      this.whispers = Array.isArray(data.whispers) ? data.whispers : [];
      this.ready = true;
      if (this.liked) {
        try {
          localStorage.setItem(LIKED_KEY, "1");
        } catch {
          /* ignore */
        }
      }
    } catch (err) {
      console.warn(
        `[SocialBackend] loadState failed (attempt ${attempt + 1}):`,
        err,
      );
      if (attempt < 3) {
        // Back off and retry — don't emit a failure state while a retry pends.
        setTimeout(() => this.loadState(attempt + 1), 1500 * (attempt + 1));
        return this;
      }
      this.ready = false; // give up for now; leave `configured` optimistic
    }
    this.#emit();
    return this;
  }

  /** Send a like (one per visitor). Optimistically flips local state. */
  async like() {
    if (this.liked || this._likeInFlight) return false;
    this._likeInFlight = true;
    // Optimistic — the swarm + HUD react instantly; reconcile from the response.
    this.liked = true;
    this.likes += 1;
    try {
      localStorage.setItem(LIKED_KEY, "1");
    } catch {
      /* ignore */
    }
    this.#emit();
    try {
      const res = await fetch("/api/like", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ visitorId: this.visitorId }),
      });
      if (res.ok) {
        const data = await res.json();
        if (typeof data.likes === "number") this.likes = data.likes;
      }
    } catch (err) {
      console.warn("[SocialBackend] like failed:", err);
      // Leave the optimistic state — the localStorage flag keeps it sticky and
      // the next loadState reconciles the true count.
    } finally {
      this._likeInFlight = false;
      this.#emit();
    }
    return true;
  }

  /**
   * Post a whisper. Returns { ok, whisper?, error? } so the compose UI can show
   * the right feedback (blocked / rate-limited / saved). On success the new
   * whisper is prepended to the local list.
   */
  async sendWhisper(text, name = "") {
    try {
      const res = await fetch("/api/whisper", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ visitorId: this.visitorId, text, name }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.whisper) {
        this.whispers.unshift(data.whisper);
        this.#emit();
        return { ok: true, whisper: data.whisper };
      }
      return { ok: false, status: res.status, error: data.error || "failed" };
    } catch (err) {
      console.warn("[SocialBackend] sendWhisper failed:", err);
      return { ok: false, error: "network" };
    }
  }
}
