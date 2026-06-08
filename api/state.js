// GET /api/state?v=<visitorId>
// One round-trip the client makes on load: registers this visit (unique-count
// via HyperLogLog) and returns the full social snapshot — total likes, whether
// this visitor already liked, unique-visitor count, and the recent whispers.
import {
  getRedis,
  KEYS,
  sendJson,
  cleanVisitorId,
  getClientIp,
  logAudit,
  VISIT_DEDUP_S,
} from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return sendJson(res, 405, { error: "method_not_allowed" });
  }
  const redis = getRedis();
  // No DB configured (e.g. local `vite` dev without keys) — degrade gracefully.
  if (!redis) {
    return sendJson(res, 200, {
      configured: false,
      likes: 0,
      visitors: 0,
      liked: false,
      whispers: [],
    });
  }

  const vid = cleanVisitorId(req.query?.v);

  try {
    // Count this visitor as a unique explorer (no-op if already seen).
    if (vid) await redis.pfadd(KEYS.visitors, vid);

    // Log the VISIT with its IP — once per visitor per dedup window — so the
    // audit shows who came by even if they never like or leave a note. SET NX EX
    // returns "OK" only the first time inside the window. Private log only.
    if (vid) {
      const fresh = await redis.set(KEYS.seen(vid), "1", {
        nx: true,
        ex: VISIT_DEDUP_S,
      });
      if (fresh === "OK") {
        await logAudit(redis, { t: "visit", visitorId: vid, ip: getClientIp(req) });
      }
    }

    const [likes, liked, visitors, rawWhispers] = await Promise.all([
      redis.get(KEYS.likes),
      vid ? redis.sismember(KEYS.likers, vid) : Promise.resolve(0),
      redis.pfcount(KEYS.visitors),
      redis.lrange(KEYS.whispers, 0, -1),
    ]);

    const whispers = (rawWhispers || [])
      .map((item) => {
        if (item && typeof item === "object") return item;
        try {
          return JSON.parse(item);
        } catch {
          return null;
        }
      })
      .filter(Boolean);

    return sendJson(res, 200, {
      configured: true,
      likes: Number(likes) || 0,
      visitors: Number(visitors) || 0,
      liked: !!liked,
      whispers,
    });
  } catch (err) {
    console.error("[api/state]", err);
    return sendJson(res, 200, {
      configured: true,
      error: "read_failed",
      likes: 0,
      visitors: 0,
      liked: false,
      whispers: [],
    });
  }
}
