# Lab 06: Microservices at Scale — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. `ulimit -n` (RLIMIT_NOFILE) exhaustion in a container manifests as?**
- A) `OutOfMemoryError`
- B) `IOException: Too many open files` — and often a second-order effect where connection retries leak sockets until the process dies
- C) GC pauses
- D) `ClassNotFoundException`

**Answer: B** — File descriptors cover sockets, files, pipes, and epoll instances. The default in many container images is 1024, which is often below what a service with 200 worker threads + pools needs.

---

**Q2. Why must `nofile` be raised in both the container limit AND the JVM/shell?**
- A) Only the shell matters
- B) The cgroup/ulimit ceiling caps all FDs; setting it in only one layer leaves the lower of the two in effect
- C) The JVM ignores ulimits
- D) It affects only stdin

**Answer: B** — Effective limit = `min(container ulimit, per-process ulimit)`. Kubernetes `securityContext` and Dockerfile `ulimits` must agree.

---

**Q3. Ephemeral port exhaustion (`connect: cannot assign requested address`) is best prevented by?**
- A) More replicas
- B) Bounded connection pools, keepalive/reuse, `tcp_tw_reuse`, wide ephemeral range, and retry with backoff on connect
- C) Bigger heap
- D) More threads

**Answer: B** — With thousands of outbound connections churning to `TIME_WAIT`, the ~28k default ephemeral range exhausts. Tune `net.ipv4.ip_local_port_range` and pool sizes.

---

**Q4. What is the danger of one JVM service holding thousands of TCP connections?**
- A) Slower GC
- B) Kernel memory (socket buffers, conntrack) and `TIME_WAIT` pressure dominate long before the JVM does; per-connection kernel buffers make it the most expensive tier to scale out
- C) Slower serialization
- D) Nothing significant

**Answer: B** — Each TCP connection costs ~4–10 KB of kernel memory for buffers plus conntrack entry. A service with 50k connections is a kernel problem, not a heap problem.

---

**Q5. `TIME_WAIT` sockets block port reuse by default for ~60s; the fix that actually works at scale is?**
- A) Waiting
- B) Connection pooling/reuse so you do not create new connections per request, plus `tcp_tw_reuse` for outbound and load-balancer tuning for inbound
- C) Increasing heap
- D) Disabling keepalive

**Answer: B** — The real fix is not creating connections. Thousands of clients that open-per-request will exhaust the ephemeral range regardless of `tw_reuse`.

---

**Q6. Why do microservices need a circuit *between* them by default even when each has a client-side timeout?**
- A) Timeouts are unreliable
- B) A single slow dependency holds resources (threads, connections, memory) far past the caller's deadline; the breaker sheds load before that compounds
- C) Breakers are faster
- D) Required by Kubernetes

**Answer: B** — Timeouts bound one call; breakers bound sustained load to a degraded dependency. Both are needed.

---

**Q7. Fan-out amplification: a service calling 5 dependencies, each retrying twice, means?**
- A) 5 calls
- B) Up to `5 × 3 = 15` calls — and if each call also fans out, the multiplication compounds across the request graph
- C) 8 calls
- D) 5 calls plus jitter

**Answer: B** — Request-graph depth multiplies: a 3-level graph with 5 calls and 2 retries per hop is `5^3 × 3^3 = 11,625` calls. This is why you budget retries globally, not per service.

---

**Q8. Why is a synchronous call chain (A→B→C→D) a scalability liability?**
- A) It's slower to write
- B) Availability multiplies: `A_total = Π A_i` (e.g. 0.995^4 ≈ 98%), and latency is the sum, so the slowest hop sets the deadline for everyone
- C) Microservices forbid it
- D) It uses more DNS lookups

**Answer: B** — Every additional synchronous dependency reduces both availability and tail latency. Long call chains are why async/event-driven designs exist.

---

**Q9. Service-to-service `mTLS` at scale mainly costs you?**
- A) Encryption CPU only
- B) Handshake CPU, connection churn (avoid by reusing connections), certificate rotation complexity, and per-mesh config management
- C) Latency on the first byte only
- D) Nothing at scale

**Answer: B** — TLS handshakes are expensive; per-request handshakes at 5k rps will not survive. Session resumption plus connection reuse is mandatory.

---

**Q10. Kubernetes `requests` vs `limits` for a JVM service: the practical consequence of getting it wrong?**
- A) Pods run faster
- B) CPU throttling at `limits` with `requests` too low (latency spikes invisible in averages); or `limits` too low causing constant throttling; memory `requests` too low causing eviction pressure and noisy-neighbor restarts
- C) No effect
- D) Only affects JVM sizing

**Answer: B** — CPU `limits` enforce CFS throttling in 100ms periods. A CPU-hungry JVM gets throttled mid-request even if its average is below the limit.

---

**Q11. What is the recommended `JAVA_TOOL_OPTIONS`-level relationship for a container?**
- A) `-Xmx` = container memory
- B) Heap ≈ 60–75% of the memory limit, leaving explicit headroom for metaspace, code cache, thread stacks, direct buffers, and agent overhead
- C) Heap = 25% of memory
- D) No explicit heap sizing

**Answer: B** — Exceeding the memory limit is an OOM-kill with no JVM error, so the native overhead must be budgeted explicitly (see MATH_FOUNDATION).

---

**Q12. What does a load balancer (e.g. L7 ingress) add that a client-side load balancer does not?**
- A) Nothing
- B) Centralized routing/health/retries/TLS termination — but it also hides per-instance behavior, so you need `X-Request-Id` propagation and per-pod metrics or you cannot debug instance-level issues
- C) Better performance always
- D) Removes the need for health checks

**Answer: B** — Centralization helps operations but destroys end-to-end visibility unless you propagate identity and keep per-instance telemetry.

---

**Q13. Why does "one service per pod, 50 replicas" behave differently from "one service, 4 big pods"?**
- A) Same thing
- B) More replicas means more connection pools to the same downstream (multiplicative connection count), more FD/CPU/memory overhead per node, and slower rollout/rollback — so per-pod count interacts with every downstream pool budget
- C) Fewer replicas are always better
- D) Replicas change semantics

**Answer: B** — Replication multiplies *client-side* resource consumption. Downstream `max_connections` and ephemeral ports are functions of total replica count, not service count.

---

**Q14. What is the practical guard against replica-induced connection storms?**
- A) Smaller pools per pod
- B) Global budgets: `replicas × pool ≤ downstream capacity`, enforced in CI, with pools tuned for the *per-pod* traffic share
- C) More load balancers
- D) Disabling pooling

**Answer: B** — The per-pod share changes with replica count, so a pool sized for 4 pods becomes 10x oversized at 40 pods. Budget globally and re-verify on every scale change.

---

**Q15. The single most common reason a microservice fails to scale linearly is?**
- A) Insufficient CPU
- B) A shared bottleneck — one database, one cache, one queue partition, or one serialized critical section — that caps throughput regardless of added replicas
- C) JVM garbage collection
- D) Container image size

**Answer: B** — Horizontal scaling only helps if the added capacity is actually on the critical path. Identify the shared resource before adding replicas; otherwise you scale cost without capacity.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and the capacity review.
- 12–10: revisit socket/FD/pool budgeting sections and redo EXERCISES 2–5.
- <10: re-read `LINUX_SOCKET_TUNING.md` cold and retake in 48 hours.
