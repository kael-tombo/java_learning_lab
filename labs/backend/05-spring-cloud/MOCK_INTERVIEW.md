# Mock Interview: Service Registry with Health Checking (Lab 05)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Service Registry Fundamentals (5 min)

**Interviewer:** What is a service registry and why do we need one?

**Candidate:** A service registry is a database of available service instances and their network locations. In monolithic architectures services are at fixed addresses. In microservices instances come and go dynamically due to scaling, failures, and deployments. The registry provides a central place where services register and consumers discover them. Without a registry, clients would need static configuration or DNS-based resolution which cannot handle dynamic registration, health-based filtering, or load balancing across instances.

**Interviewer:** What are the key operations a service registry must support?

**Candidate:** Four fundamental operations: (1) Register an instance announces its existence. (2) Heartbeat (renew) the instance periodically proves it is alive. (3) Discover a consumer queries for all healthy instances. (4) Evict the registry removes instances that fail to renew. Beyond these, the registry should support metadata, deregistration for graceful shutdown, and self-preservation for network partition tolerance.

**Interviewer:** How does Eureka client-server architecture work at a high level?

**Candidate:** Two components: Eureka Server (the registry) and Eureka Clients (services and consumers). On startup the client registers with the server. Every 30 seconds it sends a heartbeat. If the server does not receive a heartbeat for 90 seconds it evicts the instance. Clients cache the registry locally and refresh every 30 seconds. This caching is critical even if the server is down, clients can route based on their last cached copy.

---

## Round 2: Medium Registration and Heartbeat (10 min)

**Interviewer:** Walk me through the registration flow in detail.

**Candidate:** The instance sends a POST to /apps/{serviceId} with InstanceInfo payload. The registry assigns an instance ID (serviceId:host:port). Stored data includes: service ID, hostname, IP, port, health check URL, metadata map (version, environment, zone), status (UP/DOWN/STARTING/OUT_OF_SERVICE), last-heartbeat timestamp, and registration timestamp.

**Interviewer:** How does the heartbeat renewal state machine work?

**Candidate:** After registration the instance is in STARTING. It sends its first heartbeat to transition to UP. Heartbeats continue every renewalIntervalInSecs (default 30s). If a heartbeat is missed, the registry waits leaseExpirationDurationInSecs (default 90s) before evicting. The instance can also transition to OUT_OF_SERVICE for maintenance or DOWN for health check failures. Lifecycle: STARTING to UP (heartbeat), UP to (missed heartbeat timeout) to eviction.

**Interviewer:** How does your implementation handle heartbeat timing?

**Candidate:** A ScheduledExecutorService runs every healthCheckIntervalMs. It iterates through all instances and checks now - lastHeartbeat > heartbeatTimeoutMs. The heartbeat method updates lastHeartbeat to System.currentTimeMillis(). The eviction check runs on a fixed schedule if heartbeat timeout is 30s and check runs every 10s, we detect failures within 10-40 seconds.

---

## Round 3: Medium-Hard Self-Preservation (15 min)

**Interviewer:** Explain self-preservation mode. Why is it so important?

**Candidate:** Self-preservation is Eureka mechanism to handle network partitions. If a transient network issue prevents heartbeats from 90% of instances, without self-preservation the registry would evict almost all instances taking down the entire system. With self-preservation the registry stops evicting when it detects the renewal rate has dropped significantly. It assumes the network is the problem, not the instances. Clients continue routing to potentially-down instances and handle failures with retry and circuit breakers.

**Interviewer:** What is the renewal threshold calculation?

**Candidate:** Expected renewals per minute = (number of instances) * (60 / renewalIntervalInSecs) * 0.85. With 100 instances and 30s interval expected = 100 * 2 * 0.85 = 170. The 0.85 factor accounts for imperfect timing. If actual / expected < threshold (default 0.85), self-preservation activates.

**Interviewer:** What is the risk of staying in self-preservation too long?

**Candidate:** If instances are genuinely dead, self-preservation keeps dead instances in the registry. Clients discover them and requests fail. To mitigate I use a lower threshold for eviction during self-preservation if the ratio drops below 0.5 times threshold, eviction proceeds. Also clients must implement retry try instance A fail then try instance B.

**Interviewer:** How did you implement self-preservation in code?

**Candidate:** The runHealthCheck method computes renewalRatio = actualRenewals / expectedRenewals. When below threshold, enterSelfPreservationMode sets a boolean flag. In self-preservation mode eviction stops unless the ratio drops below threshold * 0.5 (critically low). Expected renewals come from configured expectedRenewalsPerMinute. Actual renewals are tracked by AtomicLong reset each check cycle.

---

## Round 4: Hard Discovery, Caching and Production (15 min)

**Interviewer:** How does the discovery API work?

**Candidate:** The client queries GET /discover/{serviceId} and receives a JSON list of healthy InstanceInfo objects. The client caches this locally with a 30-second refresh. On each outgoing request the client picks an instance using round-robin: int idx = (int)(nanotime % healthy.size()). More sophisticated strategies include weighted response time or zone-aware routing.

**Interviewer:** How do you handle stale client cache routing to dead instances?

**Candidate:** This is expected. The client should: (1) Attempt the request. (2) If it fails, mark the instance suspect and retry the next from cache. (3) If all cached instances fail, refresh from registry and retry. (4) If registry is unavailable, fail gracefully. This is exactly how Spring Cloud Netflix Ribbon works caching plus retry. The registry is eventually consistent and clients must be resilient to stale data.

**Interviewer:** How would you make the service registry itself highly available?

**Candidate:** Run a cluster of 3+ nodes. Each node is a peer no leader. Writes to one node replicate to all peers asynchronously. If a node fails, clients switch to another. The restarting node catches up by replicating from peers. Eureka peer awareness works via eureka.client.serviceUrl.defaultZone listing peers. The weak consistency model prioritizes availability over consistency (AP in CAP theorem).

**Interviewer:** What metrics would you expose from the service registry?

**Candidate:** Per-service: registered instances, healthy instances, renewal count. Global: total instances, self-preservation status, eviction count, average heartbeat latency. These are critical for operations if renewal rate drops below 90% of expected it is a warning. I would also expose per-instance information: last heartbeat, status, uptime.

**Interviewer:** How do you handle graceful shutdown?

**Candidate:** The instance calls DELETE /apps/{serviceId}/{instanceId} before shutting down. The JVM adds a shutdown hook Runtime.getRuntime().addShutdownHook(() -> registryClient.deregister()). For SIGKILL where the hook does not run, the heartbeat timeout eventually evicts. For Kubernetes, preStop hooks call deregister and wait for a drain period before SIGTERM.

---

## Round 5: Summary (5 min)

**Interviewer:** What is the most important architectural lesson from designing a service registry?

**Candidate:** A service registry must prioritize availability over consistency (AP over CP). Service discovery is liveness-critical if instances cannot be discovered the entire system fails. Eureka design (client caching, self-preservation, peer replication with async replication) is explicitly AP. The trade-off is clients may have stale data and route to dead instances, but client-side retry handles this. Trying to make the registry strongly consistent would make it fragile under network partitions which is exactly when you need it most.
