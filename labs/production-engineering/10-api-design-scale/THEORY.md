# THEORY: API Design for Scale, Resilience & Evolution
## Lab 10 | Production Engineering Academy

---

## 1. The Physics of Pagination: Offset vs Cursor-Based

### Offset Pagination (`LIMIT x OFFSET y`)
The common pattern: `SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 500000;`
- **Performance Collapse ($O(N)$ Complexity)**: The database engine cannot jump straight to row 500,000. It must scan and sort all 500,020 rows, discard the first 500,000 rows in memory, and return the last 20 rows!
- **Data Inconsistency (The Drifting Window Bug)**: If a new order is inserted while the user is paging, every record shifts down by one position. The user sees duplicate records on the next page.

### Cursor-Based / Keyset Pagination
Instead of an arbitrary offset, use the indexed sort key of the last item seen:
`SELECT * FROM orders WHERE created_at < :last_seen_timestamp AND id < :last_seen_id ORDER BY created_at DESC, id DESC LIMIT 20;`
- **Performance ($O(\log N)$ Complexity)**: Uses B-tree index direct seek. Fetching page 1 takes 2ms; fetching page 1,000,000 takes 2ms.
- **Stable Pagination**: New insertions do not shift previous cursor positions.

---

## 2. Token Bucket vs Leaky Bucket Rate Limiting

1. **Token Bucket**:
   - A bucket has capacity $C$ and refills with tokens at rate $r$ per second.
   - When a request arrives, it attempts to consume 1 token.
   - Allows bursts up to capacity $C$, then strictly throttles to rate $r$.
   - Implemented at scale in Redis via atomic Lua scripts using `timestamp` and remaining tokens.
2. **Leaky Bucket**:
   - Requests enter a queue and are processed at a constant smooth rate $r$.
   - Bursts are smoothed out into a constant steady stream.

---

## 3. API Versioning & Protobuf Compatibility Rules

### REST Versioning Strategies
1. **URI Path** (`/v1/orders` vs `/v2/orders`): Most transparent, easy to route at API Gateway; causes code duplication if overused.
2. **Accept Header** (`Accept: application/vnd.company.v2+json`): Pure REST/HATEOAS; difficult to test in browsers and CDN caching is complex.

### Protobuf Backward / Forward Compatibility Rules (Strict Invariants)
1. **Never change the numeric tag of any existing field**.
2. **Never change the type of an existing field** (e.g. changing `int32` to `string` breaks wire format).
3. If a field is deprecated: mark it `reserved 4, 8, 15;` and `reserved "old_field_name";` so future developers do not reuse the field tag.
4. Old clients reading new data ignore unknown fields. New clients reading old data populate missing fields with default zero values.
