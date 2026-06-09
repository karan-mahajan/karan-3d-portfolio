// POST /api/like   body: { visitorId }
// One like per visitor. The visitorId is added to a Redis set; the total only
// increments when the set actually grew (sadd returns 1), so repeat taps from
// the same visitor are idempotent and can't inflate the count.
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
  RATE_LIMITS,
} from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return sendJson(res, 405, { error: "method_not_allowed" });
  }
  if (isLocalRequest(req)) {
    return sendJson(res, 200, { configured: false, likes: 0, liked: false });
  }
  if (isHardBanned(req)) return sendJson(res, 403, { error: "blocked" });
  const redis = getRedis();
  if (!redis) return sendJson(res, 200, { configured: false, likes: 0, liked: false });

  const body = await readJsonBody(req);
  const vid = cleanVisitorId(body.visitorId);
  if (!vid) return sendJson(res, 400, { error: "bad_visitor_id" });
  if (await isSoftBanned(redis, req, vid)) {
    return sendJson(res, 403, { error: "blocked" });
  }

  const ipRate = await enforceIpRateLimit(redis, req, RATE_LIMITS.likeIp);
  if (ipRate.limited) {
    await registerAbuseStrike(redis, req, vid, "like_ip_rate");
    return sendJson(res, 429, {
      error: "rate_limited",
      retryAfter: ipRate.retryAfter,
    });
  }

  try {
    const added = await redis.sadd(KEYS.likers, vid);
    let likes;
    if (added === 1) {
      likes = await redis.incr(KEYS.likes);
    } else {
      likes = Number(await redis.get(KEYS.likes)) || 0;
    }
    // Private audit row (IP) for abuse review — only when a like was counted.
    if (added === 1) {
      await logAudit(redis, { t: "like", visitorId: vid, ip: getClientIp(req) });
    }
    return sendJson(res, 200, {
      configured: true,
      likes: Number(likes) || 0,
      liked: true,
      counted: added === 1,
    });
  } catch (err) {
    console.error("[api/like]", err);
    return sendJson(res, 500, { error: "write_failed" });
  }
}
