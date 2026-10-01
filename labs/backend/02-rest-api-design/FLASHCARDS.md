# Flashcards: REST API Design

## Q: PUT vs POST idempotency?
**A:** PUT is idempotent (same effect on repeat); POST is not guaranteed idempotent.

## Q: Status code for successful creation?
**A:** `201 Created` + `Location` header with the new resource URI.

## Q: Why Base-62 for short keys?
**A:** URL-safe `[A-Za-z0-9]` alphabet — no `+`, `/`, `=` that need escaping.

## Q: Where do pagination params go?
**A:** Query string: `GET /urls?page=2&size=20`.

## Q: What does the token-bucket limiter track?
**A:** Per-client (IP/API key) request rate: tokens refill over time; requests consume tokens; empty bucket = `429`.

## Q: Status for validation failure vs missing resource?
**A:** Invalid input = `400`; unknown short key = `404`.

## Q: How to handle short-key collisions?
**A:** Regenerate (random key or counter-salted hash) with bounded retries; fail with `409`/`503` if exhausted.

## Q: What header tells a rate-limited client when to retry?
**A:** `Retry-After` with `429 Too Many Requests`.

## Q: Why make `resolve` thread-safe?
**A:** ConcurrentHashMap + atomic counters prevent corruption/double-count under parallel requests.

## Q: Custom alias vs generated key trade-off?
**A:** Custom aliases are memorable but need uniqueness checks and abuse filtering; generated keys are collision-free-ish and opaque.
