# Lab 14 — Exercises: Rate Limiting Breach

## Part A — Understand (1–15)
1. Implement token bucket in 30 lines (Java/Python); test burst C=10, refill 5/s.
2. Show fixed-window boundary spike: 2N in 2s with window 60s/N=100.
3. Implement sliding-window counter; compare memory vs fixed.
4. Redis global limiter: `INCR key + EXPIRE` — race? Fix with Lua script.
5. Parse 429 headers (Limit/Remaining/Reset/Retry-After) from a live API.
6. Write a client honoring Retry-After with jittered backoff; prove load drops 3×.
7. Break a client (tight-loop retry on 429); measure amplification.
8. Top-K analysis: from access log, find top 5 keys by 429 + total volume.
9. Distinguish scraper (sequential IDs, no UA) vs legit growth (diverse paths).
10. Configure nginx `limit_req zone=api burst=20 nodelay` + test with `hey/ab`.
11. Configure Spring `Bucket4j` filter per API key; return 429 + headers.
12. Add three layers: per-key, per-IP, global — show which fires first.
13. Cache `GET /catalog` 60s; measure origin QPS drop.
14. Write PromQL: `rate(http_requests_total{status="429"}[5m]) by (api_key)`.
15. Draft 429 runbook: identify limit → who → legit-or-abuse → mitigate.

## Part B — Harden (16–30)
16. Tiered quotas (free 60/min, pro 1000/min) + upgrade path without deploy.
17. Burst sizing: p99 legit burst 15 → set C=20; justify with data.
18. Penalty box: 5× over quota in 1 min → temp block 10 min + alert.
19. Key rotation drill for leaked key; verify old key 401, new key works.
20. GraphQL cost-based limiting (points per query) for one endpoint.
21. WebSocket/message-rate limit (msgs/s per connection).
22. Load test 2× quota; verify 429 (not 5xx) + p99 latency flat.
23. Chaos: disable limiter in staging; show 5xx cascade vs protected baseline.
24. Client hedge: cache + stale-while-revalidate to survive 429.
25. Status page template for "elevated 429 for free tier."
26. Post-mortem one-pager for scraper-induced breach.
27. SLI: % legit requests not rate-limited; SLO 99.9%.
28. Cost analysis: quota increase vs extra capacity ($).
29. Peer-review limiter config for bypass (missing key header? unprotected path?).
30. Game-day: replay yesterday's top-key traffic at 3×; time mitigation.

Stretch: distributed sliding-window Lua + benchmark vs local bucket drift.
