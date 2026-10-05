# Lab 14 — Real-World Project: Rate-Limit War Room

## Incident Timeline (Scraper Breach)
| Time | Event |
|------|-------|
| T+0 | p99 latency 200ms→2s; DB pool saturation; no 429 in prior 5m (gap on `/v1/export`) |
| T+3m | Top-K: key `free-xyz` 45% of traffic, pages 1..4000 sequential, no UA |
| T+5m | SEV-2 declared; `/v1/export` throttled to 5/s per-key + IP block candidate identified |
| T+8m | Penalty box `free-xyz` (10 min) + edge `limit_req` tightened; origin QPS halves |
| T+12m | DB recovers; legit p99 back <300ms; 429 only for abuser |
| T+20m | Key owner contacted (leaked key in public scraper repo); rotation issued |
| T+30m | Resolved; cache (60s) added to `/v1/export` as follow-up |
| T+2d | Post-mortem: tier review + bypass audit + SDK backoff docs |

## War-Room Runbook
1. **Headers**: reproduce with curl; which limit (or none) fires?
2. **Top-K**: top keys/IPs by volume + 429 share in 2 min.
3. **Classify**: scraper (sequential, no UA) vs legit growth (diverse) vs leaked key (impossible geo/rate).
4. **Mitigate**: box/block abuser; raise tier for legit; shed non-critical; cache repeat GETs.
5. **Verify**: abuser 429/blocked, legit 200, p99 flat, DB pool healthy 10 min.
6. **Follow-up**: rotate key, bill/upsell or permanent block, close bypass.

## Metrics That Matter
- TTD: top-K classification <5 min. TTM: origin QPS halved <10 min.
- SLI: legit non-limited % (99.9%); 429-for-abuser % (~100%).
- DB pool wait, origin QPS, edge-vs-origin ratio, cache hit %.
- Retry amplification factor (offered vs admitted).

## Prevention Backlog
- [ ] Three layers on every endpoint; bypass audit in CI.
- [ ] Burst from p99 data; tier review quarterly.
- [ ] SDK backoff + Retry-After docs; sample code.
- [ ] 60s+ cache on hot GETs; cost-based GraphQL limits.
- [ ] Scraper replay game-day; penalty-box automation.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- HTTP 429 / rate-limit headers (Retry-After semantics): https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429
- Redis rate-limiting patterns (counters, sliding window): https://redis.io/docs/ (search rate limiting)
- AWS API Gateway throttling/quotas model: https://aws.amazon.com/api-gateway/ (throttling docs)
