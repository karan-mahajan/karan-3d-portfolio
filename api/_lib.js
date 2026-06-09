// Shared helpers for the social serverless functions (likes / whispers /
// visitor count). Files under /api whose name starts with "_" are NOT routed
// by Vercel, so this is a private module the route handlers import.
//
// Backend: Upstash Redis over its HTTP REST API (purpose-built for serverless —
// no TCP connection pool to leak across cold starts). The Vercel↔Upstash
// marketplace integration injects KV_REST_API_URL / KV_REST_API_TOKEN; a
// stand-alone Upstash project injects UPSTASH_REDIS_REST_URL / ..._TOKEN. We
// accept either naming so the same code works regardless of how the DB was made.

import { Redis } from "@upstash/redis";

let _redis = null;

/**
 * Lazily build the Redis client from whichever env-var pair is present. Returns
 * null when neither is configured (e.g. a local `vite` dev server with no keys)
 * so handlers can degrade gracefully instead of throwing a 500.
 */
export function getRedis() {
  if (_redis) return _redis;
  const url =
    process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || "";
  const token =
    process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || "";
  if (!url || !token) return null;
  _redis = new Redis({ url, token });
  return _redis;
}

// ── Redis keys (single namespace so the DB stays tidy + easy to wipe) ─────────
export const KEYS = {
  likes: "social:likes:total", // integer — total likes
  likers: "social:likes:voters", // set of visitorIds (one like per visitor)
  visitors: "social:visitors:hll", // HyperLogLog — unique explorers
  whispers: "social:whispers", // list of JSON strings, newest first
  rate: (vid) => `social:rate:${vid}`, // per-visitor whisper cooldown
  ipRate: (scope, ip) => `social:rate:ip:${scope}:${keyPart(ip)}`,
  strikeIp: (ip) => `social:strike:ip:${keyPart(ip)}`,
  strikeVisitor: (vid) => `social:strike:visitor:${keyPart(vid)}`,
  banIp: (ip) => `social:ban:ip:${keyPart(ip)}`,
  banVisitor: (vid) => `social:ban:visitor:${keyPart(vid)}`,
  seen: (vid) => `social:seen:${vid}`, // per-visitor visit-audit dedup window
  audit: "social:audit", // PRIVATE log: {t,ip,visitorId,...} — never sent to clients
};

export const VISIT_DEDUP_S = 21600; // 6h — at most one visit-audit row per window
export const RATE_LIMITS = {
  stateIp: { scope: "state", limit: 120, windowS: 60 },
  likeIp: { scope: "like", limit: 30, windowS: 60 },
  whisperIp: { scope: "whisper", limit: 8, windowS: 300 },
};
export const ABUSE_STRIKE_WINDOW_S = 600; // 10m rolling strike bucket
export const ABUSE_STRIKE_LIMIT = 3;
export const SOFT_BAN_S = 3600; // 1h auto-ban after repeated blocked attempts

const AUDIT_MAX = 5000; // most-recent audit rows kept

function keyPart(raw) {
  return Buffer.from(String(raw || "unknown")).toString("base64url").slice(0, 128);
}

/**
 * Best-effort client IP from the proxy headers Vercel sets. The browser can't
 * spoof x-forwarded-for through Vercel's edge; locally it falls back to the
 * socket address. Returns "" if unknown.
 */
export function getClientIp(req) {
  const xff = req.headers?.["x-forwarded-for"];
  if (xff) return String(xff).split(",")[0].trim();
  return (
    req.headers?.["x-real-ip"] ||
    req.socket?.remoteAddress ||
    req.connection?.remoteAddress ||
    ""
  );
}

function normalizeIp(ip) {
  return String(ip || "").replace(/^::ffff:/, "").trim();
}

export function isHardBanned(req) {
  const ip = normalizeIp(getClientIp(req));
  const raw = process.env.SOCIAL_HARD_BANNED_IPS || "";
  if (!ip || !raw) return false;
  return raw
    .split(",")
    .map((v) => normalizeIp(v))
    .filter(Boolean)
    .includes(ip);
}

export async function isSoftBanned(redis, req, visitorId = null) {
  const ip = normalizeIp(getClientIp(req));
  const checks = [];
  if (ip) checks.push(redis.get(KEYS.banIp(ip)));
  if (visitorId) checks.push(redis.get(KEYS.banVisitor(visitorId)));
  if (!checks.length) return false;
  const values = await Promise.all(checks);
  return values.some(Boolean);
}

export async function enforceIpRateLimit(redis, req, limitSpec) {
  const ip = normalizeIp(getClientIp(req));
  if (!ip || !limitSpec) return { limited: false };
  const key = KEYS.ipRate(limitSpec.scope, ip);
  const count = Number(await redis.incr(key)) || 0;
  if (count === 1) await redis.expire(key, limitSpec.windowS);
  return {
    limited: count > limitSpec.limit,
    count,
    retryAfter: limitSpec.windowS,
  };
}

export async function registerAbuseStrike(redis, req, visitorId, reason) {
  const ip = normalizeIp(getClientIp(req));
  const writes = [];
  if (ip) writes.push(incrWithExpiry(redis, KEYS.strikeIp(ip), ABUSE_STRIKE_WINDOW_S));
  if (visitorId) {
    writes.push(
      incrWithExpiry(redis, KEYS.strikeVisitor(visitorId), ABUSE_STRIKE_WINDOW_S),
    );
  }
  const counts = await Promise.all(writes);
  const strikeCount = Math.max(0, ...counts);
  await logAudit(redis, {
    t: "abuse_strike",
    visitorId,
    ip,
    reason,
    strikeCount,
  });
  if (strikeCount >= ABUSE_STRIKE_LIMIT) {
    const bans = [];
    if (ip) bans.push(redis.set(KEYS.banIp(ip), reason, { ex: SOFT_BAN_S }));
    if (visitorId) {
      bans.push(redis.set(KEYS.banVisitor(visitorId), reason, { ex: SOFT_BAN_S }));
    }
    await Promise.all(bans);
    await logAudit(redis, {
      t: "soft_ban",
      visitorId,
      ip,
      reason,
      seconds: SOFT_BAN_S,
    });
  }
  return strikeCount;
}

async function incrWithExpiry(redis, key, seconds) {
  const count = Number(await redis.incr(key)) || 0;
  if (count === 1) await redis.expire(key, seconds);
  return count;
}

const PRIVATE_HOST = /^(localhost|127\.0\.0\.1|\[?::1\]?|0\.0\.0\.0|192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\.)/;

/**
 * True when the request comes from local development (so we never pollute the
 * real counts with localhost/incognito testing). Signals, any of:
 *  - the dev Vite plugin tags requests with `x-social-dev: 1`
 *  - the Host header is localhost / a private-LAN address (covers `vercel dev`
 *    and previewing on a phone via the Network URL)
 *  - the client IP is loopback / private
 */
export function isLocalRequest(req) {
  if (req.headers?.["x-social-dev"] === "1") return true;
  const host = String(req.headers?.host || "").toLowerCase();
  if (PRIVATE_HOST.test(host)) return true;
  const ip = getClientIp(req).replace(/^::ffff:/, "");
  return ip === "" || ip === "::1" || PRIVATE_HOST.test(ip);
}

/**
 * Append a row to the PRIVATE audit log (likes + notes, with IP). This is never
 * returned by any read endpoint — inspect it via the Upstash console. Failures
 * are swallowed so auditing never blocks the user-facing write.
 */
export async function logAudit(redis, entry) {
  try {
    await redis.lpush(KEYS.audit, JSON.stringify({ ...entry, ts: Date.now() }));
    await redis.ltrim(KEYS.audit, 0, AUDIT_MAX - 1);
  } catch (err) {
    console.error("[audit]", err);
  }
}

export const WHISPER_MAX = 120; // most-recent N kept on the tree
export const WHISPER_MAXLEN = 140; // characters per message
export const NAME_MAXLEN = 24; // optional signature
export const WHISPER_COOLDOWN_S = 30; // seconds between whispers per visitor

// ── Small JSON response helpers ───────────────────────────────────────────────
export function sendJson(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  // Counts change constantly — never let a CDN/proxy cache a stale snapshot.
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(body));
}

/** Parse a JSON request body whether Vercel pre-parsed it or handed us a stream. */
export async function readJsonBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string") {
    try {
      return JSON.parse(req.body);
    } catch {
      return {};
    }
  }
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  if (!chunks.length) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    return {};
  }
}

// ── Visitor id ────────────────────────────────────────────────────────────────
/** Accept only a sane client-generated id (a UUID-ish token) to use as a key. */
export function cleanVisitorId(raw) {
  if (typeof raw !== "string") return null;
  const v = raw.trim();
  if (v.length < 8 || v.length > 64) return null;
  if (!/^[A-Za-z0-9._-]+$/.test(v)) return null;
  return v;
}

// ── Moderation ────────────────────────────────────────────────────────────────
// Public, unmoderated user text on a personal site — so the write path filters
// before anything is stored. This is a pragmatic guard (length + control-char
// strip + a leetspeak-aware blocklist), not a perfect filter; pair it with the
// ability to delete a message from the Upstash console / an admin call.
const BLOCKLIST = [
  "fuck", "shit", "bitch", "cunt", "asshole", "dick", "pussy", "bastard",
  "slut", "whore", "nigger", "nigga", "faggot", "fag", "retard", "rape",
  "cum", "cock", "twat", "wank", "jerkoff", "dildo", "porn", "nazi",
];

function normalizeForMatch(s) {
  return s
    .toLowerCase()
    .replace(/[@4]/g, "a")
    .replace(/[$5]/g, "s")
    .replace(/[0]/g, "o")
    .replace(/[1!|]/g, "i")
    .replace(/[3]/g, "e")
    .replace(/[7]/g, "t")
    .replace(/[^a-z]/g, ""); // collapse spacing/punctuation so "f.u.c.k" trips
}

export function containsProfanity(text) {
  const flat = normalizeForMatch(text);
  return BLOCKLIST.some((word) => flat.includes(word));
}

// ASCII control characters (NUL..US plus DEL) — stripped from stored text.
const CONTROL_CHARS = new RegExp("[\u0000-\u001F\u007F]", "g");

/**
 * Sanitize a free-text field: strip control chars, collapse runs of whitespace,
 * trim, and cap length. Returns "" if nothing usable remains.
 */
export function sanitizeText(raw, maxLen) {
  if (typeof raw !== "string") return "";
  let s = raw.replace(CONTROL_CHARS, " ");
  s = s.replace(/\s+/g, " ").trim();
  if (s.length > maxLen) s = s.slice(0, maxLen).trim();
  return s;
}
