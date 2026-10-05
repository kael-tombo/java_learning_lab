# Lab 14 — Math Foundation: Buckets & Windows

## 1. Token Bucket Equation
- Tokens `T(t) = min(C, T0 + R×t − consumed)`. Sustained rate ≤ R; burst ≤ C.
- Example: C=20, R=5/s. Idle 10s → 20 tokens; 20 rapid reqs pass, 21st → 429 until refill (1 token per 200ms).
- Size C for p99 burst B: `C = B + 2σ`. B=15, σ=2 → C≈20.

## 2. Fixed-Window Spike
- Limit N=100/min. Attacker sends 100 at :59 + 100 at :01 → 200 in 2s = 2× intended rate.
- Sliding window caps this to ~N per any 60s span; cost is storing per-request timestamps or N buckets.
- Choose sliding when downstream breaks at >1.2×N bursts; fixed ok when 2N tolerable.

## 3. Retry Amplification
- Client retries 3× with no backoff on 429: effective load = `orig × (1 + r)` where r≈1 (all fail) → 2× intended.
- With 2 retries across 1000 clients at 10/s: 10k/s → 30k/s offered. Backoff with jitter spreads to ~11k/s.
- Server math: provision `global_limit ≥ Σ tier_quotas × (1 + retry_factor)` or retries alone breach global.

## 4. Distributed Counter Accuracy
- Local buckets on K=5 gateways, each C=100/min → global allows 500/min vs intended 100 (5× error).
- Central Redis: exact but +1–2ms p99. Compromise: local C/K + central audit, or Redis sliding-window Lua.
- Clock skew 1s on 60s window → ~1.7% boundary error; acceptable vs 5× drift of local-only.

## 5. Sizing Global vs Per-Key
- 1000 free keys × 60/min = 60k/min potential; global cap 40k/min protects DB at 35k/min max.
- Per-key ensures fairness; global ensures survival. Both must fire: `allow = perkey_ok ∧ ip_ok ∧ global_ok`.
- Headroom: global = 0.8 × downstream_max_qps. DB 500/s → global 400/s; per-key tiers subdivide.

## 6. Worked Example
- Pro tier 1000/min (16.7/s), burst C=50. Legit p99 burst 30 → pass. Scraper 200/s → 429 after 50; Retry-After: 60.
- Top-K: key X = 70% of 429s, 1% of users → penalty box X, legit p99 unaffected. Data-driven, 5-min decision.
