# Lab 10: API Design & Evolution at Scale — Flashcards

~60 cards. Most answers are a status code, a rule, or a number.

---

## Resource modelling & naming

Q: Resource = noun, plural?
A: Yes. `/orders`, `/orders/{id}`, `/orders/{id}/items`. Verbs in the path (`/createOrder`) mean RPC over HTTP and forfeit caching, content negotiation, and standard status codes.

Q: Nesting depth?
A: Two levels max (`/orders/{id}/items`). Deeper nesting means the child does not need the parent identity — make it a top-level resource (`/items?orderId=`).

Q: Singular vs plural for non-collection resources?
A: Singular for singleton resources (`/profile`, `/settings`). Plural for collections.

Q: `PUT` vs `PATCH`?
A: `PUT` = full replacement (send the whole resource; omitted fields are removed/reset). `PATCH` = partial; you must define the merge semantics (JSON Merge Patch, JSON Patch/RFC 6902, or a custom format) and reject unknown/immutable fields.

Q: Which HTTP methods?
A: `GET` safe+idempotent, `HEAD` safe, `POST` neither, `PUT`/`DELETE` idempotent, `OPTIONS` safe. Use the semantics; proxies and clients rely on them.

Q: `POST` for creation — 201 + `Location`?
A: 201 with a `Location` header pointing at the created resource. The client should not have to construct the URI.

Q: Should a body be returned on 204?
A: No. 204 means no content; a body is ignored and confuses clients.

Q: Idempotent `DELETE` that deletes an already-deleted resource?
A: Return 204 (idempotent success) or 404. Pick one and document it; both are defensible, inconsistency is not.

---

## Status codes

Q: Which codes do you actually need?
A: 200, 201 (+Location), 202 (+a status resource), 204, 400, 401, 403, 404, 409, 412, 415, 422, 429 (+Retry-After), 500, 503.

Q: 400 vs 422?
A: 400 = malformed/parse failure. 422 = syntactically valid but semantically unprocessable (well-formed body, failed business rule). Verify current RFC guidance for 422 before citing it as normative.

Q: 401 vs 403?
A: 401 = not authenticated (send `WWW-Authenticate`). 403 = authenticated, not authorized.

Q: 404 vs 403 for "exists but not yours"?
A: 404, to avoid confirming the resource's existence. Leaking existence is an information disclosure.

Q: 409 vs 412?
A: 409 = semantic conflict with current state (duplicate key, illegal transition). 412 = precondition failed, used with `If-Match`/ETag for optimistic concurrency.

Q: 429 vs 503?
A: 429 = the client exceeded its quota (send `Retry-After`). 503 = your capacity is unavailable; you are shedding.

Q: 202 + polling resource?
A: For long operations return 202 with a `Location` to a status resource the client polls or subscribes to. Never hold the connection open for minutes.

Q: 207 Multi-Status?
A: Valid for batch responses; a per-item array with per-item status is often clearer. Confirm current status-code registry semantics before standardizing.

Q: Never return 200 with `{"success": false}`?
A: Right — it breaks every generic client, every cache, and every monitoring rule that keys on status. Errors are status codes plus a problem body.

---

## Error format

Q: Standard problem shape?
A: RFC 9457 `application/problem+json`: `type` (stable URI), `title`, `status`, `detail`, `instance`, plus extensions like `code` and `errors[]` for field problems.

Q: Why a stable `type` URI rather than a code string?
A: A URI can carry a documentation page and be extended with new members without breaking parsers. Keep an additional `code` enum for programmatic branching.

Q: Per-field validation errors?
A: `errors: [{ field, code, message }]` so a form can highlight fields. Never leak stack traces, SQL, or internal class names in `detail`.

Q: Is the `detail` message stable?
A: No. Treat it as human-readable and unstable; clients must branch on `type`/`code`, never on message text.

Q: What must never appear in an error response?
A: Stack traces, SQL statements, internal hostnames, class names, or field names from other tenants.

---

## Versioning & compatibility

Q: Backward vs forward compatibility?
A: Backward = new server + old client. Forward = old server + new client. You need backward; forward is a bonus you buy deliberately.

Q: What breaks clients?
A: Renaming a field, changing a type or nullability, removing a field, tightening validation, changing enum values, changing error codes, changing default sort/limit semantics.

Q: Is adding an optional field safe?
A: Usually, unless clients reject unknown properties or match exhaustively. Test against real clients.

Q: Adding a *new required* field to a request?
A: Breaking. Make it optional with a server-side default, or use a new version.

Q: Adding a new enum value to a response?
A: Breaking for exhaustive-match clients. Document that clients must tolerate unknown values, and test that they do.

Q: Tolerant reader / tolerant writer?
A: Consumers must ignore unknown fields; producers must never assume consumers persist fields they do not understand. Design rule, not a feature flag.

Q: URI vs header vs media-type versioning?
A: URI = visible, cache-friendly, forks the surface. Header/media type = cleaner resource space, invisible in logs/browsers, harder to test manually. Choose once and be consistent.

Q: Sunsetting properly?
A: `Deprecation: true` (RFC 9745) + `Sunset: <HTTP-date>` + per-client usage logging of the deprecated endpoint + a published replacement + refusing new clients after the date.

Q: 410 vs 404 after sunset?
A: 410 Gone states permanence; 404 hides the deprecation. Prefer 410 with a `Link` to the replacement.

Q: When is a v2 genuinely warranted?
A: A breaking semantic change that cannot be expressed additively, a materially different contract shape, or a change of business meaning for the same field. Not for bug fixes.

---

## Pagination

Q: Offset/limit problems?
A: Deep pages are O(offset) in the DB, total count is O(n), and concurrent writes cause skips/duplicates. Index-backed offset on a narrow window is acceptable; beyond that, keyset.

Q: Keyset/cursor pagination form?
A: `?limit=100&after=<opaque cursor>`; response includes `next` cursor and `hasMore`.

Q: Cursor contents?
A: The tie-break key values of the last row (e.g. `(createdAt, id)`) plus a version/filter fingerprint, **signed** so the client cannot tamper with the sort field.

Q: Deterministic ordering requirement?
A: Always sort by a unique tiebreaker (`ORDER BY created_at DESC, id DESC`), otherwise keyset pagination skips or repeats rows.

Q: Cap `limit` server-side?
A: Yes — hard cap (e.g. 100 or 500). A client-supplied unbounded limit is a data-exfiltration and DoS vector.

Q: Cap `offset`?
A: Yes. Reject beyond a threshold (400/422) rather than doing an expensive deep scan.

Q: Transparent cursor vs page numbers?
A: Cursors break "jump to page 200" and complicate analytics UIs. For internal/batch APIs, page numbers are fine; for external and large datasets, cursors.

Q: `total_count`?
A: Omit it on large collections, or make it an opt-in `?includeTotal=true` served from a cached/precomputed value.

---

## Bulk & batch operations

Q: Batch endpoint pattern?
A: `POST /orders/bulk` with `{"items":[...], "atomic":false}`; response is a per-item array of `{index, id, status, error}`.

Q: Cap batch size?
A: Yes (e.g. 100). Also cap total body size. A 100,000-item batch is an outage vector.

Q: Partial failure policy?
A: `atomic` flag where the domain supports it; otherwise always partial-success with explicit per-item status. Never silently drop items.

Q: Idempotency for a whole batch?
A: One `Idempotency-Key` per batch, plus per-item client keys if partial retries are needed.

Q: Async bulk?
A: Above a size threshold, return 202 with a job resource; results retrievable for a retention window.

---

## Idempotency, retries, rate limits

Q: `Idempotency-Key` scope?
A: Per client identity + endpoint + key. Store the first response; replay it verbatim (same status, same body) for a retention window ≥ the client's retry window.

Q: Mismatched payload with the same key?
A: Reject with 409/422 — the key was used with a different request body.

Q: Concurrent requests with the same key?
A: Return 409 (in progress) or block on the first result. Both are defensible; document it.

Q: Client retry policy?
A: Exponential backoff with full jitter, a cap on attempts (3), and a global retry budget ≤10% of volume. Retrying a 4xx (except 429) is pointless.

Q: `Retry-After`?
A: Mandatory on 429 and 503. Seconds or an HTTP-date.

Q: Rate limit headers?
A: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` (or the `X-` variants for older clients). Verify the header registry status for your target clients.

Q: Rate limit key?
A: Tenant/API key first, IP second. Per-key limits with a global backstop at the edge (edge ≤ C/3).

---

## Contracts & governance

Q: OpenAPI vs AsyncAPI?
A: OpenAPI = HTTP request/response. AsyncAPI = channels/messages, publish-subscribe bindings, acknowledgement semantics.

Q: Provider vs consumer contract tests?
A: Provider tests assert the implementation matches the schema; consumer-driven tests assert the provider still satisfies the consumer's expectations. Both catch different drift.

Q: Record/replay testing?
A: Record real responses as fixtures; replay them on every build to detect unintended changes to status codes, headers, and nullability.

Q: `additionalProperties: false` in a schema?
A: Only appropriate for closed, fully-owned contracts. For an open evolution model, omit it (tolerant reader) unless you control every client.

Q: Lint what?
A: Operation ids, consistent tag/operation naming, examples present, required fields documented, no undocumented status codes, no untyped `object`, deprecation markers honoured.

Q: Governance gates worth having?
A: Contract tests in CI; a deprecation registry; a required-review checklist for breaking changes; a published changelog; per-client usage metrics for every deprecated endpoint.

Q: What is "API first" worth doing for?
A: Cross-team contracts, generated clients/servers, and evolution safety. Monolith-internal APIs can skip it if they share a codebase.

Q: Documentation that stays true?
A: Generate it from the schema, and generate the schema from validated types (or vice versa) so drift is impossible. Hand-written examples rot.

Q: What's the breaking-change detector?
A: `openapi-diff`/`oasdiff` in CI: fail when a change is breaking by the spec's own rules, so the decision to break becomes explicit and reviewed rather than accidental.

---

## Numbers and defaults to memorize

Q: Max page size default?
A: 100 (some APIs 500). Hard cap, server-enforced.

Q: Max batch size default?
A: 100 items per bulk request; larger goes async (202).

Q: `Idempotency-Key` retention?
A: At least the maximum client retry window — commonly 24 h for money-moving operations.

Q: Retry attempts cap?
A: 3, exponential backoff, full jitter, retry budget ≤10% of request volume.

Q: Cursor size?
A: Keep it under ~200 bytes; sign it and version the payload for future changes.

Q: Error `type` URI?
A: A stable, versioned URI under your domain (`https://errors.example.com/order/insufficient-stock`), documented and append-only.

Q: `Sunset` header format?
A: HTTP-date (IMF-fixdate), not a relative duration.

Q: Long-poll timeout for async status?
A: Return 202 + poll interval hint; typical first poll 1–2 s, backoff to 30 s, expire the job resource after a documented TTL.
