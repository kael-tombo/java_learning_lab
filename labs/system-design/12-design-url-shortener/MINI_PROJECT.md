# URL Shortener - MINI PROJECT

## Project: A Shortener That Is Fast, Rotatable, and Abuse-Aware

**Time**: 8-12 hours

**Goal**: Build a shortener that survives a load test on the read path, can
change a destination after the fact, and resists enumeration. Then try to break
it.

### Step 1: Key Generation (2 h)

Implement three schemes and benchmark them:

```java
// (a) Sequential: id = autoincrement, key = base62(id)
//     Enumerable! /abc123, /abc124, ... Anyone can enumerate and mine your
//     database, your total volume, and your customer list.
//     Verdict: keep it in the repository, never expose it.

// (b) Random: key = base62(random 8 chars)
//     No information leak, but 8 chars of base62 is only ~47.6 bits. At 1B URLs
//     the birthday-collision probability is material. Compute it in step 2.

// (c) Pre-generated key pool: a generator produces blocks of keys ahead of time.
//     Write path becomes O(1) with no store round trip for key allocation,
//     at the cost of a pool to replenish.
```

Required: implement (a), (b), and (c) and report the collision rate of (b) at
your test volume. Then choose one and write two sentences defending it.

### Step 2: Keyspace Arithmetic (1 h)

```
base62 alphabet = 62 characters  ->  log2(62) = 5.954 bits per character
birthday collision probability for n keys in space N:
  P(collision) ~= n^2 / (2N)

  8 chars:  62^8 = 2.18e14
           1B URLs -> P(collision) ~= 0.23%     <-- real
           100B    -> P ~= 23%                   <-- unacceptable
  10 chars: 62^10 = 8.4e17
           100B    -> P ~= 0.6%                  <-- acceptable
```
**Required:** compute the key length for your target volume (say 50B links) at
a collision probability below 0.01%, and implement `base62Encode` /
`base62Decode` with round-trip tests over the full range. Assert: the encoder
never emits an out-of-alphabet character and the decoder rejects malformed
input rather than throwing.

### Step 3: Store and the Write Path (1 h)

```sql
CREATE TABLE links (
  short_key   VARCHAR(16) PRIMARY KEY,
  long_url    TEXT        NOT NULL,
  owner_id    BIGINT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ,
  click_count BIGINT      NOT NULL DEFAULT 0,
  is_active   BOOLEAN     NOT NULL DEFAULT TRUE);
CREATE INDEX ON links (owner_id, created_at DESC);
```

Required: a `UNIQUE` constraint on `short_key` (not an application check), and
an idempotency test that a duplicate insert returns the existing row rather
than a `500`.

### Step 4: The Read Path With Cache Tiers (2 h)

```
request -> edge/CDN cache (TTL by redirect status)
        -> app (L1 in-process cache, 60s)
        -> store (authoritative)
```

Implement `resolve(shortKey)` and measure the hit ratio at each tier:

| Tier | Expected hit ratio | Notes |
|------|-------------------|-------|
| Edge | ~92% | depends on redirect status and TTL |
| L1 | ~6% | of remaining |
| Store | ~2% | of remaining |

**Required:** measure actual hit ratios under a Zipfian request distribution
(not uniform). Assert the store's QPS is a small fraction of total QPS — if it
is not, your caching design is wrong and the numbers will tell you so.

### Step 5: Redirect Status and Link Rotation (1 h)

This is the subtle part. Implement all three and measure the consequences:

- `301` — permanently cached. Fastest (most edge hits), but a client that
  cached it will *never* see your change. Test: resolve once with `301`, change
  the destination, resolve again from the same client → stale. Prove it.
- `302` — revalidated every time. Every rotation takes effect immediately, but
  click attribution on the app tier only (no edge-level click data).
- `307`/`308` — method-preserving variants; required if you ever support
  non-GET semantics.

Deliverable: a written decision on which status you use, with the rotation and
attribution consequences stated, and a policy for links that must never change
versus links that must always be current.

### Step 6: Click Counting That Is Not a Hot Key (1 h)

A single popular link becomes a write hotspot — exactly the failure mode from
`MATH_FOUNDATION.md`. Implement:

- Counter in Redis, incremented asynchronously, flushed in batches.
- **Never** increment synchronously in the redirect path.

Required test: drive 10,000 clicks/s at one link and assert the redirect path
p99 stays under 20 ms and the store takes zero writes.

### Step 7: Abuse Controls and Your Own Attack (2 h)

Implement:
- Destination scheme allow-list (`https` only; block `javascript:`, `data:`,
  and `file:`).
- **SSRF-safe** destination validation: resolve the host and reject private,
  loopback, link-local, and cloud metadata ranges (`169.254.169.254`).
- Per-owner creation rate limit.
- Redirect-chain depth limit (a link may point to another short link at most N
  times).
- Newly-registered-domain and reputation flags for human review.

**Required:** write the attacks and show they fail:
1. Enumerate `/a0000000` upward and prove you leak nothing (random keys).
2. Shorten a `169.254.169.254` URL → must be rejected.
3. Create a chain A -> B -> C -> ... 15 deep → must be rejected at the limit.
4. `javascript:alert(1)` → must be rejected.

### Step 8: Observability (1 h)

Metrics: redirect QPS, cache hit ratio per tier, store QPS, key-pool remaining,
p50/p95/p99 redirect latency, 404 rate, link-creation rate, abuse-rejection
counts by reason.

The metric to watch: **404 rate**. A spike means the cache is serving keys that
were deleted or the key pool is exhausted.

### Deliverables

1. Three key-generation schemes with benchmarks and a defended choice.
2. Keyspace calculation for your target volume plus base62 round-trip tests.
3. Schema with a `UNIQUE` constraint and an idempotent insert test.
4. Three-tier cache with measured hit ratios under a Zipfian distribution.
5. `301` vs `302` implementation with a demonstrated staleness test and a
   written rotation policy.
6. Async click counter with a 10k/s hotspot test proving no store writes.
7. Abuse controls plus four attack scripts demonstrating each defence.
8. Metrics dashboard with the 404 alert.

### Stretch

- Add a **custom alias** feature (users pick their own key) and handle the
  resulting contention on popular aliases (this becomes a hot-key problem in
  its own right).
- Add **link expiry** with an edge-cache TTL derived from `expires_at`, and
  prove expired links stop resolving at the edge rather than at the origin.