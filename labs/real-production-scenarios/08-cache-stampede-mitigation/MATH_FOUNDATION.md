# MATH FOUNDATION — Lab 08: Stampede / TTL / Retry Math

## 1. Stampede Multiplier
- Hot key 5000 rps, TTL expiry instant: 5000 simultaneous misses → 5000 DB queries in 1s.
- DB pool 100 → overload 50x; queue explodes per L=λW (W 0.05→5s → L 250→25,000).
- Singleflight: 5000→1 (5000x reduction). Semaphore 10: caps to 10 concurrent.

## 2. Jitter Spread
- 10k keys TTL 300s fixed → all expire same second. Jitter ±15% → spread over 90s window (255–345s).
- Expiry rate: 10,000/1s → 10,000/90 ≈ 111/s (90x smoother).

## 3. Hit-Ratio and Miss Load
- Hit 98% at 10k rps → 200 misses/s (fits DB). Hit 40% → 6000 misses/s (30x, collapses DB).
- Miss budget: DB 500 qps → max tolerable hit = 1 − 500/10000 = 95%.

## 4. Early-Refresh Cost
- Beta refresh adds ~5–10% extra loads but avoids 30x spike. Net win when hot-key skew high.

## 5. Retry Math
- 6000 misses × 3 attempts = 18,000 DB hits. Disabling retry on miss path cuts 3x instantly.

## 6. SLO / Error Budget
- Stampede errors (timeouts) 20% for 10 min on 99.9% SLO (43.2 min/mo): burn 0.2/0.001=200x; budget spent ≈ 10 min of 43.2.

## 7. Worked Examples
1. 5000 rps, W 5s → L=25,000 queued; pool 100 → 99.6% must wait/fail.
2. Split key 8 ways: 5000/8=625 rps each; per-key expiry desyncs further.
3. Negative cache: 2000 rps missing-key × 45s = 90k queries avoided per window.

## 8. Takeaways
- Quantify miss-rate headroom; size fill-concurrency, not just cache RAM.
