# MATH FOUNDATION — Lab 07: Breaker / Pool / Retry Math

## 1. Little's Law (Core)
- L = λW. Normal: λ=1000 rps, W=0.1s → L=100 in flight (fits 20 threads × services with multiplexing).
- Incident: W=30s → L=30,000 → 1500x queue vs capacity → exhaustion.
- Fix W=3s → L=3000 (still 150x) → need breaker to cut λ via fail-fast.

## 2. Pool Sizing per Dependency
- Threads ≈ λ × W × (1+headroom). Payment: 50 rps × 0.5s = 25 concurrent → 5-thread bulkhead forces fallback early (by design: degrade, don't queue).
- Inventory: 100×0.1=10 → 5 threads + queue 10. Fraud: 20×0.8=16 → 3 threads + strict fallback.
- Total isolated ≈ 5+5+5+3+2=20 vs shared 20 that one dep can hog.

## 3. Failure-Rate Threshold Math
- Threshold 80%, minCalls 50 → need 40 failures to open. At 10 rps failing, 4s to open (plus timeout delay 30s each → effectively 90s+).
- Threshold 50%, window 20, minCalls 10 → 5 failures → opens in <2s at same rate. 45x faster.

## 4. Retry Amplification
- Retry factor = 1 + r + r²… 2 retries → up to 3x load on sick service. 1000 rps → 3000.
- Backoff: attempt delays 1,2,4s + jitter ±50% desynchronizes; expected added load spread over seconds not instant.
- Skip-if-OPEN cuts factor to ~1x during OPEN (fallback instead).

## 5. SLO / Burn
- 2.1M failed req at 78% peak; SLO 99.9% (43.2 min/mo) blown in 94 min. Burn 0.78/0.001=780x.
- Fallback-served requests count as degraded, not failed, if status contract defines 200+warning header.

## 6. Worked Examples
1. λ=200, W=5s → L=1000; pool 10 → queue 990 → must open breaker.
2. Timeout cut 30→3s trims worst-case hold 10x; L 30,000→3,000.
3. Half-open 10 probes × 3s = 30s re-sick window; 2 probes = 6s. Prefer 2.

## 7. Takeaways
- Short timeouts + low thresholds + small pools = fast fail, fast recover.
- Do retry math before enabling retries on latency-sensitive edges.
