# MATH_FOUNDATION — Memory Leak Debugging

## 1. Growth-Rate Model
Leaked heap over time: `H(t) = H0 + r * t` where `r` = bytes/sec retained.
Time-to-OOM: `T_oom = (Hmax - Hnow) / r`.
Example: Hmax=2G, Hnow=1.2G, r=50MB/hour → T=16h. This sets your mitigation window.

## 2. GC Overhead (Thrashing)
GC CPU fraction: `g = T_gc / T_total`.
`GC overhead limit exceeded` fires near g>0.98 with <2% reclaimed.
Throughput: `T_app = 1 - g`. At g=0.2, app loses 20% CPU — latency cliff before OOM.

## 3. Little's Law for Retention
`L = λ * W`: retained objects = allocation rate × held time.
Leak inflates W→∞ for some class. Fix = bound W (TTL) or cut λ (cache admission).

## 4. Old-Gen Trend Regression
Fit `H_old_after_FullGC(t) = a + b*t`. Leak if `b > 0` with p<0.05 over ≥6 points.
Rule: alert when `b * 24h > 0.2 * Hmax` (fills 20% of heap per day).

## 5. Pause-Time Budget
Availability loss from STW: `A_loss = Σ pause_i / window`.
Example: 3× 4s Full GC per 10min → 12/600 = 2% error-budget burn from pauses alone.

## 6. Heap Sizing Math
Container: `heap_max ≈ 0.65–0.75 × container_limit` leaving room for metaspace + direct + threads.
Threads: `RSS ≈ heap + metaspace + N_threads × stack(1MB) + direct`.
Size from measured `r`: need `Hmax > r × desired_uptime_between_restarts`.

## 7. Sampling Confidence
`jmap -histo` is a census; JFR allocation sampling is statistical.
Standard error of top-class share `p`: `SE = sqrt(p(1-p)/n)`. With n=100k samples, p=0.3 → SE≈0.14% — enough to confirm dominator.

## 8. Worked Example
Histo t0: `OrderDTO` 200MB; t0+2h: 320MB; t0+4h: 440MB → r=60MB/h.
Hmax−Hnow=600MB → T_oom=10h. Decision: restart now + ship bounded cache, not just restart.

## 9. Key Formulas Cheat Sheet
- `T_oom = (Hmax − Hnow)/r`
- `g = T_gc/T_total`, `T_app = 1 − g`
- `L = λW`
- `RSS ≈ heap + metaspace + threads×stack + direct`
- `b = ΔH_old/Δt` after Full GC

## 10. Exercises
1. Given 3 dumps compute r and T_oom. 2. Convert GC log pause sum to g. 3. Size heap for 512Mi container with 100 threads.
