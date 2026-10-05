# Lab 14 — Quiz: Rate Limiting Breach (15 Questions)

1. Token bucket params?
- [ ] A) Capacity (burst) + refill rate
- [ ] B) Window + offset
- [ ] C) Threads + heap
- [ ] D) Partitions + replicas
> Answer: A

2. Correct status for over-quota?
- [ ] A) 429 + Retry-After
- [ ] B) 200 with empty body
- [ ] C) 500 always
- [ ] D) 301 redirect
> Answer: A

3. Fixed-window flaw?
- [ ] A) Boundary spike up to 2N
- [ ] B) Too precise
- [ ] C) No memory use
- [ ] D) Requires Redis
> Answer: A

4. Client on 429 should?
- [ ] A) Back off with jitter honoring Retry-After
- [ ] B) Retry immediately in tight loop
- [ ] C) Spawn 10× threads
- [ ] D) Ignore headers
> Answer: A

5. Distributed limiter needs?
- [ ] A) Central counter (Redis Lua) for global view
- [ ] B) Local-only counters suffice at scale
- [ ] C) No state
- [ ] D) Bigger pods only
> Answer: A

6. 5xx + latency with no 429 means?
- [ ] A) Limit missing/misconfigured — overload passing through
- [ ] B) Limiter working perfectly
- [ ] C) Client bug only
- [ ] D) DNS issue
> Answer: A

7. First triage step?
- [ ] A) Which limit fired + top-K keys/IPs
- [ ] B) Delete the gateway
- [ ] C) Double all quotas blindly
- [ ] D) Restart DB
> Answer: A

8. Noisy neighbor fix?
- [ ] A) Per-key quota + penalty box / block
- [ ] B) Remove all limits
- [ ] C) Bigger timeout
- [ ] D) More logging only
> Answer: A

9. Burst capacity should be?
- [ ] A) Sized to p99 legit burst + headroom
- [ ] B) Infinite
- [ ] C) Zero
- [ ] D) Random
> Answer: A

10. Three-layer limits?
- [ ] A) Per-key + per-IP + global
- [ ] B) Three identical globals
- [ ] C) Client-only
- [ ] D) DNS + TLS + SSH
> Answer: A

11. Retry amplification happens when?
- [ ] A) Clients retry 429 without backoff
- [ ] B) Limits too high
- [ ] C) Cache hit rate high
- [ ] D) Quotas tiered
> Answer: A

12. Header telling when to retry?
- [ ] A) Retry-After
- [ ] B) Content-Type
- [ ] C) ETag always
- [ ] D) Server
> Answer: A

13. Leaked-key response?
- [ ] A) Rotate key; old → 401
- [ ] B) Raise global quota
- [ ] C) Disable auth
- [ ] D) Ignore
> Answer: A

14. Cache helps rate incidents by?
- [ ] A) Cutting origin QPS for repeat GETs
- [ ] B) Raising quotas
- [ ] C) Hiding 429s
- [ ] D) Slowing clients
> Answer: A

15. SLI for limiter health?
- [ ] A) % legit requests not limited (99.9%)
- [ ] B) Total 429 count only
- [ ] C) CPU usage
- [ ] D) Pod restarts
> Answer: A

Scoring: 13–15 excellent, 10–12 good, <10 review THEORY + CODE_DEEP_DIVE.
