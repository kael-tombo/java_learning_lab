# Quiz: Spring Cloud - Service Registry & Discovery (Lab 05)

**Topic:** Service Registry with Health Checking (Eureka-like implementation)  
**Difficulty:** Medium  
**Time Limit:** 15 minutes

---

## Questions

### 1. Core Concept
What is the primary purpose of a service registry in a microservices architecture?
- A) To store application configuration
- B) To provide a dynamic directory of service instances and their network locations
- C) To authenticate service-to-service requests
- D) To balance load across service instances

### 2. Heartbeat Mechanism
In the provided `ServiceRegistry` implementation, what triggers the `selfPreservationMode` to activate?
- A) When a single instance misses one heartbeat
- B) When the `renewalRatio` falls below `config.selfPreservationThreshold()`
- C) When more than 50% of instances are DOWN
- D) When the health checker thread dies

### 3. Concurrency
The `instanceById` map uses `ConcurrentHashMap`. Why is `CopyOnWriteArrayList` used for the per-service instance lists in the `services` map?
- A) To allow concurrent iteration during discovery without locking
- B) To reduce memory overhead
- C) To maintain insertion order
- D) To support atomic compare-and-swap operations

### 4. Eviction Logic
During `runHealthCheck()`, when does eviction occur while in self-preservation mode?
- A) Never — eviction is completely disabled
- B) Only when `renewalRatio < config.selfPreservationThreshold() * 0.5`
- C) Only for instances that have been DOWN for more than 5 minutes
- D) Only when a new instance registers

### 5. Load Balancing
The `getHealthyInstance()` method uses `System.nanoTime() % healthy.size()` for selection. What load balancing strategy does this implement?
- A) Weighted round-robin
- B) Least connections
- C) Simple round-robin (approximate)
- D) Random selection

### 6. Configuration
What is the default `heartbeatTimeoutMs` in `HealthCheckConfig.defaults()`?
- A) 10,000 ms
- B) 30,000 ms
- C) 90,000 ms
- D) 60,000 ms

### 7. Instance Status
Which of the following is NOT a valid `InstanceStatus` in the implementation?
- A) UP
- B) DOWN
- C) STARTING
- D) OUT_OF_SERVICE

### 8. Self-Preservation Calculation
The `getRenewalRatio()` method computes: `actual / expected`. What happens to `heartbeatCount` after each calculation?
- A) It increments by 1
- B) It is reset to 0 via `getAndSet(0)`
- C) It is decremented by the expected value
- D) It remains unchanged

### 9. Registration
When a new instance registers, which two maps are updated?
- A) `services` and `instanceById`
- B) `services` and `snapshots`
- C) `instanceById` and `versionMap`
- D) `services` and `versionMap`

### 10. Shutdown
What does the `shutdown()` method do?
- A) Deregisters all instances and clears maps
- B) Shuts down the `healthChecker` scheduled executor
- C) Sets `selfPreservationMode` to true
- D) Both A and B

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | A service registry is a dynamic directory that allows services to discover each other's network locations without static configuration. |
| 2 | **B** | Self-preservation activates when the renewal ratio (actual heartbeats / expected heartbeats) drops below the configured threshold (default 0.85), indicating a potential network partition. |
| 3 | **A** | `CopyOnWriteArrayList` allows safe iteration during `getInstances()` without blocking writes (registration/heartbeat), critical for read-heavy discovery operations. |
| 4 | **B** | In self-preservation, eviction only proceeds if the renewal ratio drops critically low (< 50% of threshold), meaning the issue is likely real failures not just a network glitch. |
| 5 | **C** | Using nanoTime modulo size approximates round-robin distribution across healthy instances. |
| 6 | **B** | `HealthCheckConfig.defaults()` sets `heartbeatTimeoutMs = 30_000` (30 seconds). |
| 7 | **C** | The `InstanceStatus` enum only defines `UP`, `DOWN`, and `OUT_OF_SERVICE`. `STARTING` is not included (unlike Eureka's full state machine). |
| 8 | **B** | `heartbeatCount.getAndSet(0)` atomically returns the current count and resets to 0 for the next measurement window. |
| 9 | **A** | `instanceById` maps instanceId → instance; `services` maps serviceId → list of instances. Both are updated in `register()`. |
| 10 | **B** | `shutdown()` only stops the health checker executor. It does not deregister instances (they expire naturally via missed heartbeats). |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Ready for Spring Cloud production systems |
| 7-8 | Proficient — Solid understanding of service discovery |
| 5-6 | Developing — Review heartbeat and self-preservation logic |
| <5 | Beginner — Re-read the LEETCODE_SOLUTION and MOCK_INTERVIEW files |

---

## Further Study

- Read `MOCK_INTERVIEW.md` for deep-dive interview Q&A
- Study Netflix Eureka source code for production-grade implementation
- Explore Spring Cloud Consul and Zookeeper alternatives
- Practice: Add zone-aware routing and weighted instances