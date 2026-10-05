# Lab 14 — Flashcards: Rate Limiting Breach

| # | Front | Back |
|---|-------|------|
| 1 | Token bucket | Capacity C + refill R/s; burst ≤ C |
| 2 | Leaky bucket | Fixed outflow; smooths bursts |
| 3 | Fixed window | N per window; 2N boundary spike |
| 4 | Sliding window | Precise; more memory/state |
| 5 | Status code | 429 Too Many Requests |
| 6 | Retry header | Retry-After: seconds |
| 7 | Quota headers | X-RateLimit-Limit/Remaining/Reset |
| 8 | Client behavior | Jittered backoff honoring Retry-After |
| 9 | Amplification | Tight-loop retry multiplies load |
| 10 | Distributed state | Redis INCR+EXPIRE or Lua |
| 11 | Lua why | Atomic check-and-increment |
| 12 | Three layers | Per-key + per-IP + global |
| 13 | First triage | Which limit + top-K keys/IPs |
| 14 | 429 spike | Limiter working; find who |
| 15 | 5xx no 429 | Limit missing — overload through |
| 16 | Noisy neighbor | One key dominates; box/block it |
| 17 | Scraper shape | Sequential IDs, no UA, one endpoint |
| 18 | Legit growth | Diverse paths, real UAs, rising users |
| 19 | Burst sizing | p99 legit burst + headroom |
| 20 | Penalty box | Temp block after 5× over quota |
| 21 | Key rotation | Old 401, new works, no deploy |
| 22 | Tiered quotas | Free 60/min, pro 1000/min |
| 23 | nginx directive | limit_req zone burst nodelay |
| 24 | Bucket4j | Java token-bucket filter |
| 25 | Gateway vs service | Edge coarse + service business-tier |
| 26 | Cache lever | 60s GET cache cuts origin QPS |
| 27 | ETag | Cuts repeat transfer |
| 28 | GraphQL cost | Points per query, not req count |
| 29 | WS limit | msgs/s per connection |
| 30 | PromQL 429 | rate(http_requests_total{status="429"}[5m]) by key |
| 31 | Top-K query | sort desc volume + 429 share |
| 32 | SLI | % legit not limited 99.9% |
| 33 | Load test | 2× quota → expect 429, flat p99 |
| 34 | Chaos proof | No limiter → 5xx cascade |
| 35 | Status template | "Elevated 429 for free tier, ETA" |
| 36 | Retry-After respect | Must in SDK + docs |
| 37 | Jitter | Avoids thundering retry herd |
| 38 | Default-deny | Unknown keys get lowest tier |
| 39 | Bypass audit | Unprotected path/header = hole |
| 40 | Cost trade | Quota raise vs capacity $ |
| 41 | Mitigation order | Identify → classify → block/raise/shed/cache |
| 42 | Shed load | Drop non-critical endpoints first |
| 43 | Upgrade path | Self-serve tier bump, no deploy |
| 44 | Stale-while-revalidate | Survive 429 with cached data |
| 45 | Alert | 429 rate spike + top-key table |
| 46 | Page vs ticket | Legit-wide 429 = page; single scraper = ticket |
| 47 | Evidence | Headers + top-K + traffic shape |
| 48 | Post-mortem Q | Why did limiter miss / misfire? |
| 49 | Docs must | Quotas + headers + backoff example |
| 50 | SDK must | Built-in backoff + Retry-After parse |
| 51 | Hedges | Cache + coalesce + debounce |
| 52 | Cooldown | Penalty expiry + review |
| 53 | Log fields | api_key hash, ip, path, 429 flag |
| 54 | Privacy | Hash keys in logs, don't leak |
| 55 | Game-day | Replay top-key at 3× |
| 56 | Mitigation target | Classify in <5 min, block in <10 |
| 57 | Verify | 429 for abuser, 200 for legit, p99 flat |
| 58 | On-call habit | Check headers before quotas |
| 59 | 429 is success | Proves limiter held the line |
| 60 | Lesson | Tune by top-K data, not guess |
