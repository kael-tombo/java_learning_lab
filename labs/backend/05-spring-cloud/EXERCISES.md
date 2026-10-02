# Exercises: Spring Cloud - Service Registry & Discovery (Lab 05)

**Prerequisites:** Read `LEETCODE_SOLUTION.md` and `MOCK_INTERVIEW.md`  
**Difficulty:** Progressive (Easy → Medium → Hard)

---

## Exercise 1: Basic Registration & Discovery (Easy)

### Task
Extend the `ServiceRegistry` with a method to get all registered services (not just instances).

### Requirements
```java
/**
 * Returns a map of serviceId -> instance count for all registered services.
 * Should be O(1) or O(S) where S = number of services.
 */
public Map<String, Integer> getAllServiceCounts();
```

### Test Case
```java
@Test
void testGetAllServiceCounts() {
    registry.register("user-service", "10.0.0.1", 8081);
    registry.register("user-service", "10.0.0.2", 8081);
    registry.register("order-service", "10.0.0.3", 8082);
    
    Map<String, Integer> counts = registry.getAllServiceCounts();
    assertEquals(2, counts.get("user-service"));
    assertEquals(1, counts.get("order-service"));
    assertEquals(2, counts.size());
}
```

### Hint
The `services` map already has this data. Return a defensive copy.

---

## Exercise 2: Metadata Support (Easy)

### Task
Add metadata filtering to instance discovery. Instances should be registered with arbitrary key-value metadata, and discovery should support filtering by metadata.

### Requirements
```java
// Add metadata parameter to register (already exists in LEETCODE_SOLUTION)
// Add filtered discovery:
public List<ServiceInstance> getInstances(String serviceId, 
                                           Map<String, String> requiredMetadata);
```

### Test Case
```java
@Test
void testMetadataFiltering() {
    registry.register("svc", "10.0.0.1", 8080, "/health", Map.of("version", "v1", "zone", "us-east"));
    registry.register("svc", "10.0.0.2", 8080, "/health", Map.of("version", "v2", "zone", "us-east"));
    registry.register("svc", "10.0.0.3", 8080, "/health", Map.of("version", "v1", "zone", "us-west"));
    
    // Only v1 in us-east
    var filtered = registry.getInstances("svc", Map.of("version", "v1", "zone", "us-east"));
    assertEquals(1, filtered.size());
    assertEquals("v1", filtered.get(0).metadata.get("version"));
}
```

### Hint
Filter the stream in `getInstances()` after the status check.

---

## Exercise 3: Weighted Load Balancing (Medium)

### Task
Implement weighted round-robin load balancing where instances can have a `weight` metadata value (default 1).

### Requirements
```java
/**
 * Returns a healthy instance using weighted round-robin.
 * Weight is read from instance.metadata.get("weight") (Integer, default 1).
 * Higher weight = more likely to be selected.
 */
public Optional<ServiceInstance> getWeightedHealthyInstance(String serviceId);
```

### Test Case
```java
@Test
void testWeightedDistribution() {
    // Register 3 instances: weight 1, 1, 10
    registry.register("svc", "10.0.0.1", 8080, "/h", Map.of("weight", "1"));
    registry.register("svc", "10.0.0.2", 8080, "/h", Map.of("weight", "1"));
    String heavyId = registry.register("svc", "10.0.0.3", 8080, "/h", 
        Map.of("weight", "10")).instanceId;
    
    // Sample 1000 times, heavy should get ~83%
    Map<String, Integer> counts = new HashMap<>();
    for (int i = 0; i < 1000; i++) {
        var opt = registry.getWeightedHealthyInstance("svc");
        counts.merge(opt.get().instanceId, 1, Integer::sum);
    }
    
    int heavyCount = counts.get(heavyId);
    assertTrue(heavyCount > 700 && heavyCount < 950, 
        "Heavy instance got " + heavyCount + " requests");
}
```

### Hint
Build a weighted list or use alias method. For simplicity, expand instances by weight into a selection array.

---

## Exercise 4: Health Check Endpoint Integration (Medium)

### Task
Add an active health check that periodically HTTP GETs each instance's `healthUrl` and marks it DOWN on failure.

### Requirements
```java
public class ActiveHealthChecker {
    private final ServiceRegistry registry;
    private final HttpClient httpClient;
    private final ScheduledExecutorService scheduler;
    
    public ActiveHealthChecker(ServiceRegistry registry, long intervalMs) { ... }
    
    // On each check: for each UP instance, GET healthUrl
    // If 2xx -> keep UP
    // If 5xx/timeout -> mark DOWN
    // If 404 -> mark OUT_OF_SERVICE
}
```

### Test Case
```java
@Test
void testActiveHealthCheck() throws Exception {
    // Use a mock HTTP server (e.g., MockWebServer)
    // Register instance with healthUrl pointing to mock
    // Mock returns 200 -> instance stays UP
    // Mock returns 503 -> instance becomes DOWN
    // Mock returns 404 -> instance becomes OUT_OF_SERVICE
}
```

### Hint
Use `java.net.http.HttpClient` (Java 11+). Run checks in parallel with `CompletableFuture.allOf()`.

---

## Exercise 5: Zone-Aware Discovery (Medium)

### Task
Implement zone-aware instance selection. Clients should prefer instances in their own zone.

### Requirements
```java
/**
 * Client provides its zone. Returns healthy instance preferring same zone.
 * Falls back to other zones if no healthy instance in preferred zone.
 */
public Optional<ServiceInstance> getZoneAwareInstance(String serviceId, String clientZone);
```

### Test Case
```java
@Test
void testZoneAwareSelection() {
    registry.register("svc", "10.0.0.1", 8080, "/h", Map.of("zone", "us-east-1a"));
    registry.register("svc", "10.0.0.2", 8080, "/h", Map.of("zone", "us-east-1b"));
    registry.register("svc", "10.0.0.3", 8080, "/h", Map.of("zone", "us-east-1a"));
    
    // Client in us-east-1a should get us-east-1a instances
    var inst = registry.getZoneAwareInstance("svc", "us-east-1a").get();
    assertEquals("us-east-1a", inst.metadata.get("zone"));
    
    // Mark us-east-1a instances DOWN
    registry.getInstance("svc:10.0.0.1:8080").status = InstanceStatus.DOWN;
    registry.getInstance("svc:10.0.0.3:8080").status = InstanceStatus.DOWN;
    
    // Should fall back to us-east-1b
    var fallback = registry.getZoneAwareInstance("svc", "us-east-1a").get();
    assertEquals("us-east-1b", fallback.metadata.get("zone"));
}
```

### Hint
Filter healthy instances by zone first. If empty, fall back to all healthy instances.

---

## Exercise 6: Self-Preservation Metrics Endpoint (Medium)

### Task
Add a metrics endpoint that exposes self-preservation state and renewal rates for monitoring.

### Requirements
```java
public record RegistryMetrics(
    int totalInstances,
    int healthyInstances,
    Map<String, Integer> instancesPerService,
    boolean selfPreservationMode,
    double renewalRatio,
    long expectedRenewalsPerMinute,
    long actualRenewalsLastMinute,
    long evictionCount,
    long lastEvictionTimestamp
) {}

public RegistryMetrics getMetrics();
```

### Test Case
```java
@Test
void testMetrics() {
    registry.register("svc", "10.0.0.1", 8080);
    registry.register("svc", "10.0.0.2", 8080);
    
    // Simulate heartbeats
    registry.heartbeat("svc:10.0.0.1:8080");
    registry.heartbeat("svc:10.0.0.2:8080");
    
    var metrics = registry.getMetrics();
    assertEquals(2, metrics.totalInstances());
    assertEquals(2, metrics.healthyInstances());
    assertFalse(metrics.selfPreservationMode());
    assertEquals(2, metrics.instancesPerService().get("svc"));
}
```

### Hint
Add counters for evictions and track `lastEvictionTimestamp` in `deregister()` and `runHealthCheck()`.

---

## Exercise 7: Graceful Shutdown Hook (Medium)

### Task
Implement a shutdown hook that automatically deregisters the instance and waits for cache expiry on clients.

### Requirements
```java
public class GracefulShutdownManager {
    private final ServiceRegistry registry;
    private final String instanceId;
    private final long drainTimeoutMs;
    
    public GracefulShutdownManager(ServiceRegistry registry, String instanceId, 
                                    long drainTimeoutMs) {
        this.registry = registry;
        this.instanceId = instanceId;
        this.drainTimeoutMs = drainTimeoutMs;
        installShutdownHook();
    }
    
    private void installShutdownHook() {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            // 1. Set status to OUT_OF_SERVICE (stop receiving new traffic)
            // 2. Wait drainTimeoutMs for in-flight requests to complete
            // 3. Deregister from registry
            // 4. Shutdown registry health checker
        }));
    }
}
```

### Test Case
```java
@Test
void testGracefulShutdown() throws Exception {
    // Use a separate JVM process or simulate shutdown hook execution
    // Verify sequence: OUT_OF_SERVICE -> wait -> deregister
}
```

### Hint
The instance needs a reference to its own `instanceId`. Use `volatile` for status visibility.

---

## Exercise 8: Distributed Registry with Raft (Hard)

### Task
Implement a clustered registry using Raft consensus for the `instanceById` map. Use a Raft library (e.g., Copycat/Atomix or implement minimal Raft).

### Requirements
- 3-node cluster
- Leader handles writes (register, heartbeat, deregister)
- Followers replicate log
- Reads can be served by leader (strong consistency) or followers (stale reads)
- Automatic leader election on failure

### Test Case
```java
@Test
void testClusterFailover() throws Exception {
    // Start 3 nodes
    // Register via leader
    // Kill leader
    // Verify new leader elected
    // Verify registration still works
    // Verify data consistency
}
```

### Hint
This is a significant project. Start with Atomix/Copycat for the Raft implementation. Focus on the state machine applying registry operations.

---

## Exercise 9: Registry Federation (Hard)

### Task
Implement registry federation — multiple independent registry clusters (e.g., per data center) that replicate a subset of data to each other for cross-region discovery.

### Requirements
```java
public class FederatedRegistry {
    // Local registry (this cluster)
    // Remote registries (other clusters)
    // Replicate only "global" services (opt-in via metadata)
    // Merge view for discovery: local + remote healthy instances
}
```

### Test Case
```java
@Test
void testFederation() {
    // Cluster A registers "global-service" with metadata.global=true
    // Cluster B discovers "global-service" including Cluster A's instances
    // Cluster A's "local-service" (no global metadata) NOT visible to B
}
```

### Hint
Use async replication with conflict resolution (last-write-wins on metadata, merge instance lists).

---

## Exercise 10: Chaos Testing (Hard)

### Task
Write a chaos test suite that validates registry behavior under adverse conditions.

### Scenarios to Test
1. **Network partition**: Split registry from clients → verify self-preservation activates
2. **GC pause**: Stop registry for 60s → verify clients survive on cache, instances not evicted
3. **Burst registration**: 1000 instances register in 1s → verify no OOM, no lock contention
4. **Heartbeat storm**: 5000 heartbeats/sec → verify throughput
5. **Split brain**: Two registry clusters think they're primary → verify data reconciliation

### Framework Suggestion
Use Chaos Mesh, Jepsen-style testing, or custom fault injection.

---

## Solutions

See `SOLUTIONS.md` (to be created) for reference implementations.

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 5 | Correct implementation, defensive copy |
| 2 | 10 | Metadata filtering works, handles missing keys |
| 3 | 15 | Weighted distribution statistically correct |
| 4 | 20 | Active checks run, status updates correctly |
| 5 | 15 | Zone preference + fallback works |
| 6 | 10 | All metrics accurate, thread-safe |
| 7 | 15 | Shutdown hook executes in order |
| 8 | 50 | Cluster forms, survives leader failure, consistent |
| 9 | 50 | Federation replicates global services only |
| 10 | 50 | All chaos scenarios pass |

**Total: 240 points**

---

## Next Steps

After completing exercises:
1. Run `mvn test` (if pom.xml exists)
2. Review `MOCK_INTERVIEW.md` for interview preparation
3. Study production systems: Netflix Eureka, Consul, etcd, Zookeeper
4. Explore Spring Cloud LoadBalancer integration