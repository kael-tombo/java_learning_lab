# Flashcards: Spring Cloud - Service Registry & Discovery (Lab 05)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## Core Concepts

| # | Question | Answer |
|---|----------|--------|
| 1 | What problem does a service registry solve in microservices? | Dynamic service instance locations — instances come/go due to scaling, failures, deployments. Registry enables discovery without static config. |
| 2 | What are the 4 fundamental operations of a service registry? | Register, Heartbeat (Renew), Discover, Evict |
| 3 | How does Eureka achieve high availability? | Cluster of peer nodes (3+), async replication, no leader. Clients cache registry locally. AP system (availability over consistency). |
| 4 | What is the client-side caching TTL in Eureka? | 30 seconds default (registry fetch interval) |
| 5 | Why is client-side caching critical? | Even if registry is down, clients can route using last cached copy. |

---

## Registration & Heartbeat

| # | Question | Answer |
|---|----------|--------|
| 6 | What data is stored during service registration? | instanceId (serviceId:host:port), serviceId, host, IP, port, healthCheckUrl, metadata map, status, lastHeartbeat, registrationTime |
| 7 | What is the default heartbeat interval in Eureka? | 30 seconds (`eureka.instance.leaseRenewalIntervalInSeconds`) |
| 8 | What is the default eviction timeout in Eureka? | 90 seconds (`eureka.instance.leaseExpirationDurationInSeconds`) — 3 missed heartbeats |
| 9 | What are the instance status states in Eureka? | STARTING → UP → (DOWN/OUT_OF_SERVICE) → evicted |
| 10 | How does the registry detect a failed instance? | Scheduled health check: `now - lastHeartbeat > heartbeatTimeoutMs` |

---

## Self-Preservation Mode

| # | Question | Answer |
|---|----------|--------|
| 11 | What is self-preservation mode? | Registry stops evicting instances when it detects a network partition (renewal rate drops significantly), assuming instances are still alive but heartbeats aren't arriving. |
| 12 | How is the renewal threshold calculated? | `expectedRenewalsPerMinute = instanceCount * (60 / renewalIntervalSecs) * 0.85`. The 0.85 factor accounts for timing imperfections. |
| 13 | When does self-preservation activate? | When `actualRenewals / expectedRenewals < threshold` (default 0.85) |
| 14 | What is the risk of staying in self-preservation too long? | Dead instances remain in registry → clients route to them → requests fail until client-side retry kicks in. |
| 15 | How does the implementation limit self-preservation eviction? | If `renewalRatio < threshold * 0.5` (critically low), eviction proceeds even in self-preservation. |

---

## Discovery & Load Balancing

| # | Question | Answer |
|---|----------|--------|
| 16 | How does a client discover healthy instances? | GET `/discover/{serviceId}` → returns JSON list of UP instances |
| 17 | What load balancing strategy does `getHealthyInstance()` use? | Round-robin: `index = nanoTime() % healthy.size()` |
| 18 | How does the client handle stale cache (routing to dead instance)? | Retry with next instance from cache → if all fail, refresh from registry → if registry down, fail gracefully |
| 19 | What is the discovery cache refresh interval? | 30 seconds |
| 20 | What metadata can be attached to an instance? | Arbitrary key-value map: version, environment, zone, custom tags |

---

## Implementation Details

| # | Question | Answer |
|---|----------|--------|
| 21 | Why `ConcurrentHashMap` for `instanceById`? | Thread-safe O(1) registration, heartbeat, and lookup under concurrent access. |
| 22 | Why `CopyOnWriteArrayList` for per-service instance lists? | Read-heavy (discovery) — lock-free iteration during `getInstances()` while writes (register/evict) create new copies. |
| 23 | How is optimistic concurrency handled in registration? | Not explicitly — `ConcurrentHashMap.computeIfAbsent` + `CopyOnWriteArrayList.add` are atomic enough for this use case. |
| 24 | What is the time complexity of `getInstances(serviceId)`? | O(k) where k = instances for that service (filtering UP status) |
| 25 | How does the health checker schedule work? | `ScheduledExecutorService` runs `runHealthCheck()` every `healthCheckIntervalMs` (default 10s) |

---

## Configuration & Tuning

| # | Question | Answer |
|---|----------|--------|
| 26 | What are the 4 key config parameters in `HealthCheckConfig`? | `healthCheckIntervalMs`, `heartbeatTimeoutMs`, `expectedRenewalsPerMinute`, `selfPreservationThreshold` |
| 27 | What is a good `healthCheckIntervalMs` for production? | 10-30 seconds (balance detection speed vs CPU) |
| 28 | How should `expectedRenewalsPerMinute` be calculated? | `instanceCount * (60000 / heartbeatIntervalMs) * 0.85` — update dynamically as instances register/deregister |
| 29 | What metrics should you expose from the registry? | Per-service: registered/healthy counts, renewal rate. Global: total instances, self-preservation status, eviction count, avg heartbeat latency. |
| 30 | How do you handle graceful shutdown? | Client calls DELETE `/apps/{serviceId}/{instanceId}` via shutdown hook. For SIGKILL, heartbeat timeout eventually evicts. |

---

## Advanced / Interview Deep-Dive

| # | Question | Answer |
|---|----------|--------|
| 31 | CAP theorem: Is Eureka CP or AP? | AP — prioritizes availability. Clients may have stale data but can still route. |
| 32 | How does peer replication work in Eureka cluster? | Each node replicates writes to all peers asynchronously. Restarting node catches up by replicating from peers. |
| 33 | What happens if two registry nodes have different views? | Clients may get different instance lists from different nodes. Client-side retry handles this. |
| 34 | How would you add zone-aware routing? | Include `zone` in instance metadata. Client prefers instances in same zone (lower latency, fault isolation). |
| 35 | How to implement weighted load balancing? | Add `weight` to metadata. `getHealthyInstance()` picks with probability proportional to weight. |

---

## Quick Reference: Key Methods

| Method | Purpose | Complexity |
|--------|---------|------------|
| `register(serviceId, host, port, ...)` | Add new instance | O(1) |
| `heartbeat(instanceId)` | Renew lease | O(1) |
| `getInstances(serviceId)` | Discover healthy instances | O(k) |
| `getHealthyInstance(serviceId)` | Round-robin pick one | O(k) |
| `deregister(instanceId)` | Graceful removal | O(1) avg |
| `runHealthCheck()` | Evict expired + self-preservation | O(n) |
| `getRenewalRatio()` | Compute health metric | O(1) |
| `isSelfPreservationMode()` | Check safety mode | O(1) |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| No client-side retry | Single point of failure | Implement retry with next instance |
| Too aggressive eviction | False evictions during GC pauses | Increase `heartbeatTimeoutMs` |
| Static `expectedRenewalsPerMinute` | Self-preservation triggers incorrectly | Update dynamically on register/deregister |
| No health check URL | Can't verify app-level health | Require `/actuator/health` or equivalent |
| Single registry node | SPOF | Run 3+ node cluster |

---

## Related Patterns

| Pattern | Relation |
|---------|----------|
| **Circuit Breaker** | Client stops calling consistently failing instances |
| **Client-Side Load Balancing** | Ribbon/Spring Cloud LoadBalancer uses registry data |
| **API Gateway** | Routes via service discovery (e.g., Spring Cloud Gateway) |
| **Config Server** | Centralized config, separate from service discovery |
| **Distributed Tracing** | Trace requests across discovered services (Sleuth/Zipkin) |