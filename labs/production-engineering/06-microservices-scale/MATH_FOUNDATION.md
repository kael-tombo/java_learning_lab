# Lab 06: Microservices at Scale — Math Foundation

Scaling is arithmetic on connections, memory, and timeouts. These are the numbers that decide whether adding a replica helps or hurts.

---

## 1. Connection budget across a fleet

The equation everyone must be able to do in their head:

```
total_connections = Σ_services ( replicas_s × pool_max_s )
```

Example: 6 services, 20 replicas each, pool 30:

```
6 × 20 × 30 = 3,600 outbound connections
```

Against a database with `max_connections = 400`:

```
utilization = 3,600 / 400 = 9× over budget   →  immediate exhaustion
```

Correct budget (target 70% of `max_connections`):

```
pool_max = 0.7 × max_connections / (services × replicas)
        = 0.7 × 400 / (6 × 20) = 2.3   →  not viable
```

That is the arithmetic that **forces an architecture change**, in order of preference:
1. Connection pooler (pgbouncer / service-mesh pooling) — many logical sessions on few physical connections.
2. Read replicas for reporting/exports.
3. Fewer replicas per service or fewer services per dependency.
4. Bigger database.

**Corollary — the scale-down trap.** A pool sized when you ran 4 replicas is 10× oversized at 40 replicas. Always express pool sizes as `pool_max = floor(0.7 × dep_capacity / (replicas × callers))` and recompute at every replica change:

| Replicas | Safe pool (6 services, 400 conns) |
|---|---|
| 4 | 11 |
| 10 | 4 |
| 20 | 2 (→ needs pooler) |
| 40 | 1 (→ must pool or shard) |

---

## 2. File-descriptor budget

```
FDs_needed ≈ C_conn + C_files + C_pipes + C_epoll + overhead
            ≈ k · C_conn + 50        (k = 2–3 for connect/accept churn, DNS, retries)
```

With peak `C_conn = 2,000` outbound + 1,000 inbound:

```
FDs ≈ 3 × 3,000 + 50 ≈ 9,050      → set nofile = 16,384 (or 32,768 for headroom)
```

Symptom math: with `ulimit -n = 1024` and per-pod in-flight of 300 connections, you exhaust FDs at ~30% of intended capacity because each logical connection may transiently need 2–3 descriptors (retry + pending accept).

---

## 3. Ephemeral port exhaustion

```
ports_available ≈ (port_range_high − port_range_low + 1) ≈ 28,232  (default)
```

Connection creation rate `c` (connections/s) with `TIME_WAIT` of 60 s consumes:

```
TIME_WAIT_population = c × 60
```

Steady state is only possible if `c × 60 ≤ 28,232`:

```
c_max ≈ 28,232 / 60 ≈ 470 connections/s per (src_ip → dst_ip:port) pair
```

At 2,000 rps to one downstream with open-per-request, you exhaust in ~14 s and get `cannot assign requested address`. Fixes, in order of effect:

1. **Reuse connections** → `c` drops to roughly `rps / avg_requests_per_connection` (e.g. 2000/100 = 20/s).
2. Widen range → `c_max ≈ 920/s` (10000–65535).
3. `tcp_tw_reuse=1` for outbound.
4. Multiple source IPs per pod.

**Takeaway**: the only fix that scales with traffic is #1.

---

## 4. Kernel memory per connection

```
mem_per_conn ≈ (rmem_max_effective + wmem_effective) + sk_buff_overhead + conntrack
≈ 8 KB (typical autotuned 16 KB total buffers) + ~1–4 KB bookkeeping
```

Budget: `C_conn × mem_per_conn ≤ memory_budget × 0.5` (leave the rest for the JVM).

`C_conn = 50,000`, 10 KB each → **500 MB of kernel memory** — often larger than the JVM heap. This is why connection-heavy services need larger nodes or pooling, and why "just add replicas" fails for connection-oriented workloads.

Tuning math — socket buffer autotuning:
`rmem` grows up to `net.core.rmem_max`. With `rmem_max = 6 MB`, 50k conns could reach 300 GB in theory; `tcp_rmem` defaults (87 KB initial → 6 MB max) bound the typical case. Reduce per-connection buffers for connection-dense, low-throughput services.

---

## 5. Per-pod resource share under autoscaling

```
per_pod_share = total_traffic / replicas        traffic share per pod
pool_max      = λ_per_pod × W_p99 × safety
```

`λ_total = 6,000 rps`, `W_p99 = 80 ms`, safety 1.3:

| Replicas | λ/pod | pool_max = λ·W·1.3 |
|---|---|---|
| 6 | 1,000 | 104 |
| 12 | 500 | 52 |
| 30 | 200 | 21 |
| 60 | 100 | 10 |

Notice: **per-pod pool size should shrink as replicas grow**, because each pod carries a smaller share. Teams typically set the pool once (for 6 replicas) and then scale to 30, creating 104 × 30 = 3,120 connections where 20 × 30 = 600 would do. This is the single most common autoscaling-related connection incident.

---

## 6. CPU throttling math

CFS quota is enforced in periods of `100 ms`:

```
quota_per_period = limits_cpu × 0.1 s
throttle iff used_cpu_time_in_period > quota_per_period
```

With `limits.cpu = 2`, a burst of 250 ms CPU in one 100 ms period is throttled for the remainder — a **150 ms involuntary stall with no JVM-level pause**. Combined with Little's Law:

```
L = λ × W        → a 150 ms throttle adds 150 ms to W for everything in flight
```

`λ = 1,000/s`: `ΔL = 1,000 × 0.15 = 150` extra concurrent requests per throttle event — a self-amplifying spike. Recommendation: set CPU `requests == limits` for latency-critical services so the scheduler reserves rather than throttles, and verify `container_cpu_cfs_throttled_seconds_total` stays flat.

---

## 7. Container memory budget

```
memory_limit = heap + metaspace + code_cache + thread_stacks + direct + GC_struct + native_overhead
```

With `heap = 4 GB`, `metaspace = 256 MB`, `code cache = 250 MB`, `threads = 400 × 512 KB = 200 MB`, `direct = 512 MB`, GC/JVM/native ≈ 500 MB:

```
total ≈ 5.72 GB   → set container limit = 8 GB, requests = 8 GB
heap_share = 4/8 = 50%   (conservative; can be tuned up after NMT measurement)
```

Heap from percentage: `-XX:MaxRAMPercentage=50` on an 8 GB limit gives 4 GB. Verify actual RSS with `cat /sys/fs/cgroup/memory.current` (v2) and NMT.

Rule of thumb table:

| Service type | heap share | notes |
|---|---|---|
| I/O-bound REST | 50–60% | large native (netty/direct) share |
| CPU-bound batch | 70–75% | little native |
| JVM with agents/APM | 45–55% | agent overhead is significant |

---

## 8. Availability and latency multiplication across hops

```
A_chain = Π A_i           latency = Σ μ_i + tail variance
```

Four hops at 99.5%:

```
0.995^4 = 0.9801   → 1.99% downtime/year just from chaining
```

To hit 99.95% with 4 hops, each hop needs:

```
A_i = 0.9995^(1/4) = 0.999875   → 99.9875% per hop
```

Latency budget for a 250 ms end-to-end SLO across 3 hops:

```
per_hop_budget = (250 ms − local_overhead 40 ms) / 3 ≈ 70 ms at the mean,
and p99.9 of each hop must fit: 3 × p99.9 ≤ 250 − 40  →  p99.9 ≤ 70 ms
```

If a downstream's p99.9 is 300 ms, you cannot meet the SLO with a synchronous design — you must go async, degrade, or change the SLO. **That is a design conclusion derived from arithmetic.**

---

## 9. Retry amplification across the call graph

```
amp = f^d × (r+1)^d       f = calls per level, d = depth, r = retries per hop
```

| f | d | r | amp |
|---|---|---|---|
| 3 | 2 | 2 | 9 × 9 = 81 |
| 5 | 3 | 2 | 125 × 27 = 3,375 |
| 5 | 3 | 3 | 125 × 64 = 8,000 |

Global retry budget: cap retries at fraction `β` of total volume so that during a partial outage:

```
effective_load = λ · (1 + β) ≤ available_capacity
```

With 50% capacity loss and `β = 0.1`: `0.5 × 1.1 = 0.55` of healthy load → survivable. With `amp = 9`: `0.5 × 9 = 4.5×` healthy load → certain collapse. Retry policy is an architectural decision with a numeric cost.

---

## 10. Connection storm recovery time

After a deploy, if pool connections are recycled without jitter:

```
storm_period  = maxLifetime (all connections expire in the same window)
new_conn_rate = replicas × pool_max / storm_period
```

`60 pods × 20 pool = 1,200` connections, `maxLifetime = 30 min` un-jittered: within a few seconds the service opens 1,200 connections against a dependency whose accept queue is `tcp_max_syn_backlog = 4096` and whose pool is 400 → immediate refusal storm.

Jittered lifetime (`30 min ± 10 min`) spreads arrivals:
```
arrival_rate ≈ 1,200 / 1,200 s ≈ 1 connection/s    → negligible
```

**Always jitter pool `maxLifetime`.** It is the cheapest availability fix in this lab.

---

## 11. Queue-based services: partitions and throughput

```
throughput = min( producers, partitions, consumer_parallelism )
```

With 3 partitions, 12 consumers, and a hot key pinned to one partition: effective parallelism = 1, so `throughput = 1/12` of expectation. Partition count is a hard concurrency ceiling that can only be raised by re-keying (which requires an ordered-consumer or two-phase approach).

Consumer lag memory: `lag_messages × avg_bytes` must fit RAM. With `lag = 10M` and 1 KB messages: **10 GB** — an OOM risk that appears only during incidents.

---

## 12. Time to drain and rollback

Graceful shutdown window:

```
drain_time = max( in_flight_requests / throughput , longest_request_time )
```

`in_flight = 2,000`, `throughput = 500/s` → 4 s to drain at steady rate, but the *tail* requests may take longer; set `terminationGracePeriodSeconds ≥ p99.9 request time + drain estimate` (e.g. 60 s). Too short → SIGKILL mid-request → user-visible 502s on every deploy.

Rollback time budget: if `rollback = detect (2 min) + decide (5 min) + roll (5 min) = 12 min`, then any incident whose fix is longer than 12 min should default to rollback first, investigate after. Make this explicit: **rollback is the SLO for incident response.**

---

## 13. Capacity model for one service

Inputs: `λ_peak`, `W_cpu`, `W_io`, `mem_per_conn`, `heap`, `target_utilization`.

```
CPU_cores  = λ_peak × (W_cpu + W_io) / U_target
mem_pod    = heap + native + λ_per_pod × W_io × mem_per_conn
replicas   = ceil( λ_peak / (cores_per_pod × U_target / (W_cpu+W_io)) )
```

Worked example: `λ_peak = 6,000/s`, `W_cpu = 4 ms`, `W_io = 20 ms`, `U = 0.6`, 4-core pods, heap 4 GB, 12 KB/conn:

```
CPU per pod  = 6,000 × 0.024 / 0.6 / 4 = 60 pods   (CPU-bound)
mem per pod  = 4 GB + 0.3 + (6,000/R) × 0.020 × 12 KB
              → at R = 60: 4.0 GB + 24 MB ≈ 4.3 GB  → 8 GB limit
```

Both CPU and memory constraints must be satisfied; take the max of the two required replica counts, then verify dependency budgets again.

---

## 14. Quick drills

1. 6 services × 20 replicas × pool 30 vs `max_connections = 400` → over/under? **Answer: 3,600 vs 400 = 9× over. Needs pooler.**
2. Default ephemeral ports, 2,000 conn/s, 60 s TIME_WAIT → sustainable? **Answer: needs 120,000 slots vs 28,232 → no. Fix = connection reuse.**
3. 300 threads × 1 MB `-Xss` → native memory? **Answer: ~300 MB. Set 512 KB stacks → 150 MB.**
4. `λ = 1,000/s`, a 150 ms CFS throttle → extra concurrent load? **Answer: 150.**
5. 3-hop chain, each 99.5% → availability? **Answer: 98.5%.**
6. 60 pods, pool 20, `maxLifetime = 30 min` un-jittered → storm rate? **Answer: 1,200 conns in one window. Jitter it.**

---

## 15. Formulas worth memorizing

| Formula | Use |
|---|---|
| `Σ replicas × pool ≤ 0.7 × max_conn` | connection budget; forces pooler/replicas/DB decisions |
| `FDs ≈ 2–3 × C_conn + 50` | `nofile` sizing |
| `c_max ≈ ports / TIME_WAIT` | max connection-creation rate |
| `mem_per_conn ≈ 8–10 KB` | kernel budget for connection-heavy services |
| `pool_max = λ_per_pod × W_p99` | per-pod pool under autoscaling |
| `ΔL = λ × ΔW_throttle` | amplification from CFS throttling |
| `heap ≈ 0.5–0.75 × memory_limit` | container memory budget |
| `A = Π A_i` | availability across sync hops |
| `amp = f^d(r+1)^d` | retry amplification across call graphs |
| jitter `maxLifetime` | prevent deploy-time connection storms |
