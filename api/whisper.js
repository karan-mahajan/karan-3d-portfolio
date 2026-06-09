// POST /api/whisper   body: { visitorId, text, name? }
// Validates + moderates a message, rate-limits per visitor, then pushes it onto
// the capped recent-whispers list (newest first). Returns the stored whisper.
import { randomUUID } from "node:crypto";
import {
  getRedis,
  KEYS,
  sendJson,
  readJsonBody,
  cleanVisitorId,
  getClientIp,
  isLocalRequest,
  isHardBanned,
  isSoftBanned,
  enforceIpRateLimit,
  registerAbuseStrike,
  logAudit,
  sanitizeText,
  containsProfanity,
  RATE_LIMITS,
  WHISPER_MAX,
  WHISPER_MAXLEN,
  NAME_MAXLEN,
  WHISPER_COOLDOWN_S,
} from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return sendJson(res, 405, { error: "method_not_allowed" });
  }
  if (isLocalRequest(req)) {
    return sendJson(res, 200, { configured: false, error: "local" });
  }
  if (isHardBanned(req)) return sendJson(res, 403, { error: "blocked" });
  const redis = getRedis();
  if (!redis) return sendJson(res, 503, { error: "not_configured" });

  const body = await readJsonBody(req);
  const vid = cleanVisitorId(body.visitorId);
  if (!vid) return sendJson(res, 400, { error: "bad_visitor_id" });
  if (await isSoftBanned(redis, req, vid)) {
    return sendJson(res, 403, { error: "blocked" });
  }

  const ipRate = await enforceIpRateLimit(redis, req, RATE_LIMITS.whisperIp);
  if (ipRate.limited) {
    await registerAbuseStrike(redis, req, vid, "whisper_ip_rate");
    return sendJson(res, 429, {
      error: "rate_limited",
      retryAfter: ipRate.retryAfter,
    });
  }

  const text = sanitizeText(body.text, WHISPER_MAXLEN);
  const name = sanitizeText(body.name, NAME_MAXLEN);
  if (!text) return sendJson(res, 400, { error: "empty" });
  if (containsProfanity(text) || (name && containsProfanity(name))) {
    await registerAbuseStrike(redis, req, vid, "profanity");
    return sendJson(res, 422, { error: "blocked" });
  }

  try {
    // Per-visitor cooldown: SET NX EX. If the key already exists the write is
    // rejected — one whisper per visitor per WHISPER_COOLDOWN_S seconds.
    const ok = await redis.set(KEYS.rate(vid), "1", {
      nx: true,
      ex: WHISPER_COOLDOWN_S,
    });
    if (ok !== "OK") {
      return sendJson(res, 429, { error: "rate_limited", retryAfter: WHISPER_COOLDOWN_S });
    }

    const whisper = {
      id: randomUUID(),
      text,
      name: name || null,
      ts: Date.now(),
    };
    await redis.lpush(KEYS.whispers, JSON.stringify(whisper));
    await redis.ltrim(KEYS.whispers, 0, WHISPER_MAX - 1);

    // Private audit row (IP + text) for moderation — never sent to clients. The
    // public whisper object stored above deliberately carries NO IP.
    await logAudit(redis, {
      t: "whisper",
      id: whisper.id,
      visitorId: vid,
      ip: getClientIp(req),
      text,
    });

    return sendJson(res, 200, { configured: true, whisper });
  } catch (err) {
    console.error("[api/whisper]", err);
    return sendJson(res, 500, { error: "write_failed" });
  }
}
