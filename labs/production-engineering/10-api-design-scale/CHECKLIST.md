# CHECKLIST: API Production Readiness
## Lab 10 | Production Engineering Academy

---

## 1. Pagination & Data Volume
- [ ] No unbounded collection queries in endpoints (mandatory `limit` parameter, max 100).
- [ ] Keyset/Cursor-based pagination implemented for tables $> 10,000$ rows.
- [ ] Composite database index exists covering cursor fields: `(created_at DESC, id DESC)`.
- [ ] Total count (`COUNT(*)`) omitted from paginated responses on large datasets.

## 2. Rate Limiting & Abuse Prevention
- [ ] Rate limits configured per client API key / IP address.
- [ ] `429 Too Many Requests` returned with `Retry-After` header when limit exceeded.
- [ ] Request body size capped (e.g. max 2 MB) to prevent memory exhaustion attacks.

## 3. Contract Safety & Evolution
- [ ] OpenAPI / Swagger contract generated and validated in CI.
- [ ] Jackson configured with `FAIL_ON_UNKNOWN_PROPERTIES = false` to guarantee forward compatibility.
- [ ] Protobuf field numbers strictly frozen and never reused.
- [ ] Deprecated endpoints return `Sunset` and `Deprecation` RFC headers.
