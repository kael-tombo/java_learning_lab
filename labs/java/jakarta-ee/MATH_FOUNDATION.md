# Math Foundation — Jakarta EE Sizing

## 1. Throughput (Little)
`concurrent = λ × W`. 500rps × 100ms = 50 threads/inflight.

## 2. Pool Sizing
DB pool ≈ `cores × 2 + disks`. 4 cores → ~10 conns; more ≠ faster.

## 3. p99 Budget
`p99 = svc + GC + JIT + net`. Keep svc < 50ms for 100ms SLO.

## 4. Connection Churn
`T_handshake ≈ 1–3 RTT`. Pool reuse saves ms per req.

## 5. N+1 Cost
`Q = 1 + N`. N=100 orders → 101 queries; JOIN FETCH → 1.

## 6. Retry Amplification
Retries r=3, fail f=10% → `load ×= 1+f+f² ≈ 1.11`. Circuit-break at 50%.

## 7. Heap per Request
`heap_rate = λ × bytes_req`. 500 × 50KB = 25MB/s → young GC cadence.

## Recap
```
C = λ·W
pool ≈ 2·cores
Q_n1 = 1+N
load_retry = 1+f+f²
```
Drill: 1krps×80ms threads? Pool for 8 cores?
