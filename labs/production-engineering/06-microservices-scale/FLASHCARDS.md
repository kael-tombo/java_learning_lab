# Lab 06: Microservices at Scale — Flashcards

~60 cards. Almost every answer here is a number you must budget.

---

## Connections & File Descriptors

Q: What is one file descriptor (FD)?
A: A kernel handle to an open resource: socket, file, pipe, epoll/eventfd, inotify watch. Every TCP connection uses at least one.

Q: Default `ulimit -n` in many container base images?
A: Often 1024 (sometimes 65536). Check, do not assume.

Q: How many FDs does a service need?
A: `sockets + files + pipes + epoll + headroom`. Rule: `≈ 2–3× peak concurrent connections + static overhead`.

Q: Why can FD exhaustion cause a connection *leak* pattern?
A: Failing `accept`/`connect` throws, callers retry, and each retry can leak a half-open socket, so FDs keep climbing after the original error.

Q: Symptom of FD exhaustion?
A: `IOException: Too many open files`, plus `ss -s` showing sockets in `FIN_WAIT`/`CLOSE_WAIT`.

Q: What is `CLOSE_WAIT` telling you?
A: The peer closed, but *your* app has not closed the socket — an application-level leak (missing `close()` on response body/connection). `TIME_WAIT` is normal; `CLOSE_WAIT` is a bug.

Q: `FIN_WAIT_2` accumulation?
A: Peer closed but you haven't — also your side not completing close. Long-lived FIN_WAIT_2 means you are not draining.

Q: Where do you set FD limits in a container?
A: Dockerfile `ulimits` + Kubernetes `securityContext`, and verify with `cat /proc/<pid>/limits`.

Q: How to verify a process's real FD ceiling?
A: `cat /proc/<pid>/limits | grep -i "open files"`.

Q: Count open FDs of a JVM?
A: `ls /proc/<pid>/fd | wc -l` or `ss -tanp | grep <pid> | wc -l`.

---

## Ephemeral Ports & TIME_WAIT

Q: Default Linux ephemeral port range?
A: `32768–60999` ≈ 28,232 ports per (src ip, src port, dst ip, dst port) tuple.

Q: Default `TIME_WAIT` duration?
A: 60s (`net.ipv4.tcp_fin_timeout` is separate — it is *not* the TIME_WAIT timer).

Q: Kernel memory per TCP connection?
A: ~4–10 KB for buffers (send+recv, autotuned) plus a conntrack entry (hundreds of bytes to a few KB).

Q: 50,000 outbound connections, 8 KB each?
A: ~400 MB of kernel memory — comparable to or larger than the JVM heap. Kernel is the scarce tier.

Q: `tcp_tw_reuse`?
A: Allows reusing `TIME_WAIT` sockets for *outbound* connections when safe. Helps, but does not fix open-per-request patterns.

Q: Widen ephemeral range?
A: `net.ipv4.ip_local_port_range = 10000 65535` → ~55k ports. Cheap, but a mitigation, not a fix.

Q: `tcp_fin_timeout`?
A: Controls how long an orphan `FIN_WAIT_2` socket lingers. Lowering it does *not* reduce `TIME_WAIT`.

Q: Best fix for TIME_WAIT pressure?
A: Connection reuse (pooling/keepalive) so you stop creating connections. Everything else is mitigation.

Q: `somaxconn` / `tcp_max_syn_backlog`?
A: Accept-queue sizes. Small values cause connection drops/syn retransmits under connection-rate spikes.

Q: `net.core.somaxconn` vs app listen backlog?
A: Effective backlog = `min(somaxconn, app_backlog)`. Check both.

---

## Pool & Connection Budgets

Q: Total downstream connections = ?
A: `Σ_services (replicas × pool_max)`. Multiply carefully before adding capacity.

Q: Rule for per-pod pool size under autoscaling?
A: Size for the *per-pod* traffic share with headroom, and re-verify at min and max replica counts.

Q: Example: 6 services × 20 replicas × pool 30?
A: 36,000 connections against dependencies that likely cap far lower. This is the classic scaling bug.

Q: Connection budget guard?
A: `replicas × pool_max ≤ downstream_max_connections × 0.7` — enforced in CI, re-checked on every scale change.

Q: Pool `maxLifetime` vs upstream idle kill?
A: Set `maxLifetime` below the LB/DB idle timeout (e.g. 30 s vs 60 s idle kill), with jitter, so you don't hand out dead sockets.

Q: Why jitter `maxLifetime`?
A: Without jitter, all pool connections recycle simultaneously every `maxLifetime` → a periodic connection storm against the dependency.

Q: What is a connection storm?
A: Many clients reconnecting at once (after a deploy, failover, or un-jittered lifetime) — can overload the dependency and exhaust its accept queue.

Q: `tcp_keepalive` / HTTP keepalive for outbound?
A: Required to actually reuse connections; some cloud/LB paths kill idle connections silently, so set client keepalive below that.

Q: Inbound vs outbound FD asymmetry?
A: Inbound is bounded by LB config; outbound grows with `replicas × downstream count` and is the one that surprises you.

---

## Container Memory Budget

Q: Container memory composition for a JVM?
A: Heap (touched) + metaspace + code cache + thread stacks + direct/native buffers + GC structures + agent/native libs + JVM overhead.

Q: Recommended heap share of the memory limit?
A: ~60–75%. Start at 66–70% and measure native usage with NMT.

Q: Thread stacks: 300 threads × 1 MB `-Xss`?
A: ~300 MB native. With 500 threads × 512 KB: ~256 MB. Often the largest native consumer.

Q: Direct buffers (Netty/NIO)?
A: Native, outside `-Xmx`. Bound with `-XX:MaxDirectMemorySize` or it surfaces as `OutOfMemoryError: Direct buffer memory`.

Q: CPU `requests` too low consequence?
A: Node overcommit → CPU steal and CFS throttling of neighbors; your p99 spikes while average CPU looks fine.

Q: CPU `limits` consequence?
A: Hard CFS throttling in 100 ms periods — the JVM is paused mid-work at the kernel level, not visible as a Java pause.

Q: How to detect CFS throttling?
A: `container_cpu_cfs_throttled_seconds_total` (cAdvisor) or `cpu.stat` in cgroup v2.

Q: Memory `requests` too low consequence?
A: Burstable QoS: node memory pressure evicts your pod, restart loop, cold caches, and a re-warm storm.

Q: JVM container awareness flag?
A: `-XX:+UseContainerSupport` (default since JDK 10); verify with `jcmd VM.flags` and `Runtime.maxMemory()`.

Q: Exit 137 with no JVM OOME?
A: Kernel OOM-kill — you exceeded the cgroup limit, meaning your native+heap budget was wrong.

---

## JVM Tuning for Containers

Q: CPU-aware GC ergonomics?
A: The JVM sizes GC threads and compiler threads from detected processors (cgroup-aware). Verify with `-XX:+PrintFlagsFinal | grep -i ParallelGCThreads`.

Q: `-XX:MaxRAMPercentage` in a container?
A: Relative to the cgroup memory limit, not host RAM. Safe only if you leave room for native memory.

Q: `-XX:+UseZGC` for latency-critical services?
A: Sub-ms pauses at large heaps, at higher CPU cost. Worth it if p99 GC pauses are your SLO breach.

Q: `-XX:MaxGCPauseMillis` in container?
A: Soft target; G1 sizes young gen to approach it. Verify actual pauses — the target is not a guarantee.

Q: Should you pin `-Xms == -Xmx` in containers?
A: Often yes, to avoid resize pauses and make RSS predictable for the scheduler.

Q: `-XX:+AlwaysPreTouch` in containers?
A: Faster warmup, higher startup RSS, and pages resident from the start (no page-fault cost later). Costs memory.

Q: JVM crash-loop from `ExitOnOutOfMemoryError`?
A: Deterministic restart beats a limping process; ensure readiness gates traffic until warm.

Q: Heap dump path in ephemeral storage?
A: Point it at a mounted volume with room for a live-set-sized file; ephemeral defaults are small and shared.

---

## Call Chains, Retries, Fan-out

Q: Availability of a synchronous chain of 4 hops at 99.5% each?
A: `0.995^4 ≈ 98.0%`. Every hop multiplies.

Q: Latency of a chain?
A: Sum of means plus tail variance. The slowest hop sets everyone's deadline.

Q: Fan-out amplification `d` levels, `f` calls/level, `r` retries?
A: `f^d × (r+1)^d`. With `f=5, d=3, r=2`: `125 × 27 = 3,375`.

Q: Global retry budget?
A: Cap retries as a fraction (≤10%) of total requests across the whole call graph, not per service.

Q: Deadline propagation?
A: Pass an absolute deadline so each hop computes remaining budget from it; prevents inner work outliving the caller.

Q: Idempotency keys for retried writes?
A: Required for at-most-once effect across retries, failovers, and client re-sends.

Q: Async/event-driven instead of deep sync chains?
A: Removes multiplicative availability loss and deadline coupling; adds eventual consistency and operational complexity.

Q: When is a sync call chain actually right?
A: When the caller genuinely needs the immediate answer (validation, authorization, price) — but keep depth ≤ 2–3 and budgeted.

---

## Deployment & Traffic

Q: `X-Request-Id` / trace propagation rule?
A: Gateway generates or honors it and *every* hop forwards it; logs and spans keyed on it. Without it, distributed debugging is guesswork.

Q: Readiness vs liveness probe semantics?
A: Readiness = "should I receive traffic" (can serve). Liveness = "should I be restarted" (is wedged). Never make liveness depend on a downstream.

Q: Why does liveness depending on a dependency cause an outage?
A: A slow dependency fails every liveness probe → every pod restarts simultaneously → no pod can recover → cascade.

Q: Rolling update and connection draining?
A: PreStop hook + `terminationGracePeriodSeconds` long enough to drain in-flight requests; SIGTERM handling that stops accepting and finishes work.

Q: Rollback speed as an availability feature?
A: Rollback (not fix-forward) is the primary mitigation. Measure time-to-rollback and alert on it.

Q: Blue/green vs rolling for a 40-replica service?
A: Rolling spreads risk over minutes and requires old/new coexistence; blue/green is instant but doubles capacity briefly. Choose per service risk.

Q: Kubernetes startup probe for a slow JVM?
A: Startup probe prevents liveness from killing a JVM that is still warming (class loading, JIT, cache fill).

Q: Graceful shutdown requirement?
A: On SIGTERM: stop accepting, finish or fail in-flight quickly, flush telemetry, close DB connections, exit. Under 30 s or the grace period kills you.

---

## Shared Bottlenecks

Q: Why doesn't adding replicas always help?
A: A shared resource (single DB writer, one cache shard, one queue partition, a global lock) caps throughput.

Q: Symptoms of a shared bottleneck?
A: Latency flat but throughput plateaus; per-instance CPU drops as replicas rise; a single resource shows 100% utilization.

Q: Diagnosing the bottleneck resource?
A: Correlate per-service CPU with per-dependency saturation; check queue depth/partition skew; look for lock contention.

Q: Stateless service sharing a stateful DB?
A: Adds DB connection pressure (`replicas × pool`) with no throughput gain past the DB's ceiling.

Q: Service mesh sidecar overhead?
A: Extra CPU/latency per hop and per node proxy config. Measure, and prefer mTLS+retry at the app for latency-critical paths.

Q: Kafka partition skew?
A: A hot key pins traffic to one partition, so consumer parallelism is irrelevant. Fix keying or add parallelism downstream.

---

## Diagnosis at Scale

Q: Command to see socket states in aggregate?
A: `ss -tan | awk '{print $1}' | sort | uniq -c` or `ss -s`.

Q: Per-pod error/latency without an L7 proxy?
A: Keep `X-Request-Id` + instance labels on metrics and logs; scatter-gather logs by request id when needed.

Q: "Only one pod is slow" — check?
A: That pod's node, its cgroup throttling, its local disk/cache state, its connection pool, and whether it received a bad traffic shard.

Q: "All pods slow after a deploy"?
A: New version behavior, cold caches/JIT, new schema, and connection storm from `maxLifetime` resync.

Q: How to attribute a latency spike to DNS?
A: JVM DNS cache TTL (`networkaddress.cache.ttl`) and `CacheLoader`; DNS lookups per request scale with QPS and can dominate tail.

Q: DNS as a microservice scaling hazard?
A: Resolver overload and per-pod caching misses during scale events; keep TTLs sane and cache aggressively.

Q: Load balancer health check interval vs readiness?
A: Health checks remove unhealthy pods; readiness gates traffic. Both need to be fast enough to matter and slow enough to avoid flapping.

---

## Numbers to memorize

Q: Default ephemeral ports available?
A: ~28,232 (`32768–60999`). Widen to ~55k if needed — but reuse connections first.

Q: `TIME_WAIT` default?
A: 60s.

Q: Kernel memory per connection?
A: ~4–10 KB (buffers) + conntrack entry.

Q: Recommended heap share of container limit?
A: 60–75% (66–70% is a good default with NMT verification).

Q: Recommended thread stack?
A: 512 KB for I/O services; watch total `threads × stack`.

Q: FD headroom?
A: 2–3× peak concurrent connections.

Q: Global retry budget?
A: ≤10% of total request volume.

Q: Sync chain depth to keep?
A: ≤2–3 hops.

Q: `somaxconn` default?
A: 4096 on modern Linux; verify `tcp_max_syn_backlog` too.
