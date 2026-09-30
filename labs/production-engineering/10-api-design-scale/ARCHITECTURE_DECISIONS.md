# ARCHITECTURE DECISIONS: API Evolution & Governance Standards
## Lab 10 | Production Engineering Academy

---

## ADR-01: API Versioning, Pagination & Rate Limiting Policy

### Status: ACCEPTED

### Context
Public and internal APIs experienced breaking changes, database resource exhaustion from unbounded queries, and crawler abuse.

### Decisions
1. **Pagination Mandate**:
   - Offset pagination (`?page=`) is strictly prohibited on datasets projected to exceed 10,000 rows.
   - Keyset/Cursor-based pagination is mandatory for all high-volume transaction and audit logs.
   - All collection endpoints must default to `limit = 20` and enforce `max_limit = 100`.
2. **Breaking Change Protocol**:
   - Deleting a field or renaming an existing field in an active API is strictly forbidden.
   - New fields must always be optional/nullable.
   - Deprecated fields must be supported for a minimum of 180 days accompanied by `Deprecation` and `Sunset` HTTP headers (RFC 8594).
3. **Rate Limiting Standard**:
   - All inbound traffic must pass through Token Bucket rate limiters at API Gateway.
   - Authenticated tiers: Standard (100 req/s, burst 200), Enterprise (1,000 req/s, burst 2,000).
   - Return standard headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

### Consequences
- Eliminates database CPU spikes caused by deep offset scans.
- Ensures backward compatibility across mobile apps and third-party integrations.
