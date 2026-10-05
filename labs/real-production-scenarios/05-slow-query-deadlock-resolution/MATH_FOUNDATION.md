# MATH_FOUNDATION — Queries, Locks & Retries

## 1. Total Time Ranking
`total = calls × mean`. A 2ms query × 1M calls (2000s) beats a 500ms × 100 calls (50s). Optimize total, not just mean.

## 2. Index Selectivity
Cost ≈ `pages_fetched ≈ selectivity × table_pages + btree_depth`.
Selectivity 0.001 on 1M rows → ~1000 rows via index wins; 0.5 → seq scan wins. Misestimated selectivity flips plans.

## 3. Little's Law Again
`N_pool = λ × W_query`. W 50ms→5s (100×) under same λ explodes pool need 100×. Query SLO is pool sizing.

## 4. Deadlock Probability
Two txns touching same 2 rows in opposite order: P(collision window) ≈ overlap/holding-time fraction.
Random order + long txns → frequent; fixed order → 0 regardless of load.

## 5. Retry Math (Backoff + Jitter)
Attempt delays 50,100,200ms + jitter ±50%. P(all 3 collide) ≈ p³ for independent p.
p=0.2 → 0.008 (99.2% success). Without jitter, retries synchronize → p stays high.

## 6. Timeout Budget
End-to-end budget B=2s: `B = query + retries×(query+backoff)`.
query p99 400ms, 2 retries → worst ≈ 400+ (400+100)+(400+200)=1.5s fits; 5s query never fits — fix query first.

## 7. Lock Wait Queue (M/M/1)
Row-lock wait ≈ `ρ/(1−ρ) × S` where ρ = contention. At ρ=0.8, wait=4S. Shortening txn (smaller S) beats adding conns.

## 8. Formulas
- `total=calls×mean`, `N=λW`
- `delays=base×2^n + jitter`
- `P_fail≈p^retries`, `wait≈ρS/(1−ρ)`

## 9. Exercises
1. Rank 5 digests by total. 2. Compute pool need before/after index. 3. Size retry budget for B=1s.
