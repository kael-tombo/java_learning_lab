# Math Foundation — IO / NIO

## 1. Throughput
`T = bytes / seconds`. Target disk ~500MB/s SSD, net ~125MB/s per GbE.
Example: 5GB / 10s = 500MB/s.

## 2. Latency (Little's Law)
`L = λ × W` (concurrency = arrival_rate × wait).
If λ=1000 req/s, W=0.05s → L_concurrent=50.

## 3. Buffer Sizing
Optimal buf ≈ `BDP = bandwidth × RTT`.
1Gbps × 1ms = 125KB → use 128KB buffers.

## 4. Copy Cost
Classic copy syscalls ≈ `2 × read + 2 × write` crossings.
Zero-copy ≈ `1 sendfile`. Saving ≈ 50–70% CPU.

## 5. Selector Scaling
Threads_classic = N_conns. Threads_selector ≈ N_cores.
Memory saved = `(N - cores) × stack (1MB)`.

## 6. Queue Bound (Backpressure)
`Q_max = throughput × max_pause`. 100MB/s × 2s = 200MB cap.

## 7. Direct Memory Budget
`direct_used + heap_used < container_limit`.
Set `-XX:MaxDirectMemorySize = 25% heap`.

## 8. File Scan Time
`T = size / min(disk_bw, decode_bw)`.
1GB / 500MB/s = 2s lower bound.

## 9. Tail Latency (p99)
p99 ≈ `mean + 3σ` (normal approx). Measure with HDR histogram.

## 10. Open FD Growth
`fds(t) = opened - closed`. Leak if slope > 0 over steady load.

## 11. Page Cache Hit Ratio
`hit% = cached_reads / total_reads`. Miss cost ~1000×.

## 12. Amortized Flush
`cost_per_byte = syscall_cost / buf_size`. 2µs/4KB=0.5ns/B; 2µs/128KB≈0.016ns/B.

## Formulas Recap
```
T = bytes/sec
L = λ·W
buf = bw·RTT
threads_saved = N − cores
direct ≤ 0.25·heap
T_scan = size/min(bw)
```
Practice: compute BDP for 10Gbps×0.5ms; size queue for 200MB/s×1s pause.
