# URL Shortener - Vision

## Why This Lab Exists
A URL shortener looks trivial and is quietly a distributed systems exercise: it
is write-heavy, read-heavier, serves mostly redirects, must survive link
rotation, and becomes a security problem the moment anyone can shorten a URL for
someone else. This lab exists so the "easy" design is recognised as a set of
specific trade-offs.

## The Mental Model
The workload has an asymmetry that drives every decision:

```
  writes   : low volume, correctness-critical, durable
  reads    : enormous volume, latency-critical, cache-friendly, immutable-ish
  redirect : 301/302 choice is a product decision, not an HTTP detail
```

Nearly all the engineering belongs on the read path, and nearly all the risk
lives on the write path.

## Four Decisions That Define The System

1. **Key generation** — sequential, random, hashed, or pre-generated.
   Sequential is enumerable (an attack); random is safe but non-compressible;
   pre-generated decouples write latency from the store.
2. **Redirect status** — `301` lets clients and CDNs cache forever (fast, but
   you can never change a destination or see clicks); `302` is revalidated
   (observable, correct when links must be rotatable).
3. **Lifespan** — do links expire? Who may create them? Is the destination
   allowed to change?
4. **Trust** — who may shorten a URL? This is the abuse vector: phishing,
   malware distribution, and brand impersonation.

## The Read Path Is a CDN Problem
A short link is a perfect CDN candidate: small responses, high read
multiplier, and effectively immutable content. The correct answer is
overwhelmingly "serve redirects from an edge cache with a long TTL, invalidated
on link edit". Teams routinely build a database-backed read path and wonder why
they are paying database costs for 300-byte rows.

## What You Should Be able To Do
- Choose a key generation scheme and justify it against enumeration,
  compressibility, and collision handling.
- Compute the keyspace: how many base62 characters are needed for N URLs at a
  target collision probability?
- Explain the `301` vs `302` trade-off including click-attribution and link
  rotation consequences.
- Design a cache hierarchy (edge -> app -> store) with explicit TTLs and an
  invalidation trigger on edit.
- Detect abuse: domain reputation, redirect-chain depth, newly registered
  domains — and say which requires a human decision.
- Explain why this workload is a natural fit for a write-scaled key generator
  plus a read-scaled edge, and when that split is not worth it.

## The Anti-Goals
- Not "just a hash and a redirect". That skips every hard part above.
- No sequential IDs on a public shortener.
- No unbounded destination validation — an SSRF in the redirect checker is a
  real vulnerability.

## Success Criteria
You can specify a shortener with: key scheme and keyspace calculation,
redirect status and its consequences, cache layers with TTLs and invalidation,
abuse controls with owners, and read/write capacity projections with the
arithmetic attached.

## How To Use This Lab
1. `THEORY.md` for architecture and patterns.
2. `MATH_FOUNDATION.md` for keyspace, entropy, cache hit ratio, redirect
   semantics.
3. `CODE_DEEP_DIVE.md` for key generation, base62 encoding, cache tiers.
4. `MINI_PROJECT.md` to build and abuse-test a shortener.
5. `REAL_WORLD_PROJECT.md` for a production link-management platform.