# Math Foundation — Version Evolution

## 1. Upgrade ROI
`ROI = (perf_gain + maint_save − mig_cost)/mig_cost`.
21 virtual threads: 10× concurrency at same memory → high ROI for IO-bound.

## 2. Memory: Compact Strings (9)
Latin-1 1B vs UTF-16 2B: `save ≈ 50%` string heap. 1GB strings → ~500MB.

## 3. G1 vs ZGC Pause
G1 p99 ~10–50ms; ZGC p99 ~1ms. `pause_ratio = p99_old/p99_new ≈ 20×`.

## 4. Startup (AppCDS/Leyden)
CDS archive cuts startup `20–40%`. `T_new = 0.7·T_old`.

## 5. Throughput: Streams vs Loops
Streams +2–5% overhead; negligible vs IO. Don't gate upgrade on it.

## 6. Thread Memory (Loom)
Platform 1MB stack × 10k = 10GB; virtual ~KBs → ~100MB. `save ≈ 100×`.

## 7. GC Scaling
Pause vs heap: Parallel O(heap), ZGC O(roots). 100GB heap: Parallel seconds, ZGC ms.

## Recap
```
ROI = (gain−cost)/cost
save_strings ≈ 50%
T_cds = 0.7·T
mem_vt ≈ N·KBs
```
Drill: 5k threads memory before/after Loom; CDS on 10s startup.
