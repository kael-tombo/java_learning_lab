# MATH_FOUNDATION — Cloud Java economics

## 1. Container memory budget

Limit `L`, heap fraction `f` (`MaxRAMPercentage`), non-heap `N`
(metaspace + direct + stacks + code cache):

```
heap = f·L,   need heap + N ≤ L  →  f ≤ 1 − N/L
```

For L=1 GiB, N≈250 MiB → f ≤ 75%. Smaller containers need *lower* f
(N doesn't shrink proportionally) — the #1 OOMKilled cause is copying
f=75% into a 512 MB limit.

## 2. Startup vs billing

Cold-start penalty per scale-from-zero event: JVM `S_j` (2–10 s) vs
native `S_n` (~0.1 s) vs CRaC `S_c` (~0.2 s). With event rate λ and
per-GB-s price p, expected waste ≈ λ·S·mem·p. Native/CRaC win iff
λ·(S_j − S_n)·mem·p > build-complexity cost — i.e. bursty + spiky
workloads, not steady services.

## 3. Thread economics (Little's law, again)

Concurrent requests C = λ·W (arrival × mean latency). Platform threads:
C capped by pool (memory per thread ~1 MB stack). Virtual threads: C
bounded by heap/queues instead — same blocking code sustains 100× C at
comparable memory. Throughput per container rises until CPU or downstream
(not threads) saturates.

## 4. Cloud scorecard math (labs 54–56 input)

Monthly cost ≈ Σ(compute·util·price + mem·price) + data (IOPS, transfer)
+ managed-service premiums. Compare on *your* λ/W profile, not list
prices: egress-heavy APIs punish clouds with steep transfer fees;
spiky workloads reward scale-to-zero + native/CRaC.
