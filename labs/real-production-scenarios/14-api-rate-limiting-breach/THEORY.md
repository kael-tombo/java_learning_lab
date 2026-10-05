# Lab 14 — API Rate Limiting Breach — Theory: Mechanics + Detection

## 1. Why Rate Limits Exist
- Protect shared resources (DB, downstream) from overload; enforce fairness/quotas; monetize tiers.
- Without limits: retry storms + scrapers + one noisy tenant → cascading 5xx for everyone.

## 2. Algorithm Mechanics
- **Token bucket**: capacity C, refill R/s. Request takes 1 token; empty → 429. Allows bursts up to C.
- **Leaky bucket**: fixed outflow; smooths bursts, queues excess.
- **Fixed window**: N per minute; boundary spike 2N possible. **Sliding window log/counter**: precise, more memory.
- Distributed: local counters diverge; use Redis `INCR + EXPIRE` or sliding-window Lua for global consistency.

## 3. HTTP Contract
- `429 Too Many Requests` + `Retry-After: <seconds>` + `X-RateLimit-Limit/Remaining/Reset`.
- Client must honor Retry-After with jittered exponential backoff; never tight-loop retry on 429.
- Gateway (nginx/Kong/Envoy) enforces edge; service enforces business-tier logic.

## 4. Detection
| Signal | Meaning |
|--------|---------|
| 429 rate spike | Limit breached (by whom? top API key/IP) |
| 5xx + latency rise with no 429 | Limit missing/misconfigured — overload passing through |
| Single key dominating traffic | Noisy neighbor / scraper / leaked key |
| Retry amplification (client retries ×3) | Backoff absent; effective load 3× intended |

## 5. Triage Order
1. Which limit? (edge vs service, per-key vs global) — check 429 headers.
2. Who? Top-K keys/IPs by 429 + 200 volume.
3. Legit growth vs abuse? Traffic shape, user-agent, endpoint fan-out.
4. Mitigate: raise tier / block key / tighten window / shed load / cache.

## 6. Prevention
- Tiered quotas in code review; load-test at 2× quota; default-deny unknown keys.
- Per-key + per-IP + global three-layer limits; burst (C) sized to p99 legitimate burst.
- Client SDK with backoff +hedging; server `Cache-Control` + ETag to cut repeat calls.

## 7. Takeaway
429 is success — the limiter worked. The incident is 5xx/latency when limits are absent, or wholesale 429 for legit users when tuned wrong. Tune by top-K data, not guess.
