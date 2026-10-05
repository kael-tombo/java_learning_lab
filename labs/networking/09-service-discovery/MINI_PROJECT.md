# Service Discovery - MINI PROJECT

## Project: RegistryLab — a service registry with heartbeats, health checks, and a client

Build a registry that registers services, evicts dead instances by heartbeat, filters by
health, and serves a client library that caches with a TTL and fails safely when the
registry is unavailable. Then resolve the same problem with Kubernetes DNS.

### Architecture

```
  SERVICE INSTANCES
  ──────────────────
  orders-1 ──register(instanceId, host, port, metadata)──┐
  orders-2 ──register(...)───────────────────────────────┤
  orders-1 ──heartbeat every 10s─────────────────────────┤
  orders-2 ──crashes (no more heartbeats)                │
                                                          ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ Registry                                                     │
  │  /registrations/{service}/instances  (ephemeral, lease-based)│
  │  eviction loop: drop instances whose lease expired            │
  │  /services/{service}/instances?healthy=true                   │
  └──────────────────────────┬────────────────────────────────────┘
                             │  long-poll / watch for changes
                             ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ Client library                                               │
  │  - local cache with TTL (discovery is hot; polling is not)    │
  │  - circuit breaker: registry down -> use last known good      │
  │  - health filter: never route to a known-unhealthy instance   │
  └──────────────────────────┬────────────────────────────────────┘
                             ▼
                    HTTP call to a selected instance

  Kubernetes equivalent: headless Service -> per-pod DNS A records;
  client resolves the service name and gets all ready pod IPs.
```

### Implementation

Registry with lease-based registration, so a crash is a timeout rather than a stale entry forever:

```java
@Service
class ServiceRegistry {
    private final Map<String, Map<String, Instance>> services = new ConcurrentHashMap<>();
    private static final Duration LEASE = Duration.ofSeconds(30);
    private static final Duration HEARTBEAT = Duration.ofSeconds(10);

    /**
     * EPHEMERAL registration: the instance holds a lease and must renew it. A hard crash
     * means the lease expires and the entry is evicted. This is the only reliable way to
     * handle a process dying without deregistering, which is most process deaths.
     */
    Registration register(String service, Instance instance) {
        var leaseId = UUID.randomUUID().toString();
        var record = new Instance(instance, leaseId, Instant.now().plus(LEASE), InstanceStatus.UP);
        services.computeIfAbsent(service, k -> new ConcurrentHashMap<>()).put(instance.id(), record);
        changeNotifier.notifyChange(service, ChangeType.REGISTERED, instance.id());
        return new Registration(service, instance.id(), leaseId);
    }

    @Scheduled(fixedRate = 5_000)
    void renew(Registration registration) {
        var record = instances.get(registration.instanceId());
        if (record == null) {                       // evicted; force re-registration
            throw new RegistrationExpiredException(registration.instanceId());
        }
        if (!record.leaseId().equals(registration.leaseId()))
            throw new LeaseConflictException("another holder has this lease");
        record.leaseExpiresAt(Instant.now().plus(LEASE));
    }

    /** Eviction is the mechanism that makes a crash recoverable. */
    @Scheduled(fixedRate = 5_000)
    void evictExpiredLeases() {
        for (var entry : services.entrySet()) {
            entry.getValue().values().removeIf(record -> {
                if (record.leaseExpiresAt().isBefore(Instant.now())) {
                    metrics.counter("registry.evicted", "service", entry.getKey(), "reason", "lease_expired");
                    changeNotifier.notifyChange(entry.getKey(), ChangeType.EVICTED, record.instance().id());
                    return true;
                }
                return false;
            });
        }
    }
}
```

Health filtering, so a registered but broken instance is not routed to:

```java
@Service
class InstanceResolver {
    /**
     * Distinguish REGISTERED (present in the registry) from HEALTHY (actually serving).
     * A process that is up but returning 500s must not receive traffic. Kubernetes solves
     * this with readiness probes; a hand-rolled registry must do it explicitly.
     */
    List<Endpoint> resolve(String service) {
        return instances.of(service).stream()
                .filter(Instance::isUp)
                .filter(i -> i.status() == InstanceStatus.UP)
                .map(Instance::endpoint)
                .sorted(comparingInt(Instance::activeConnections))    // least-connections hint
                .toList();
    }

    /** A failing instance is marked OUT_OF_SERVICE, not removed: removing hides a
     *  systemic problem, while retaining it lets the registry report a cluster of failures. */
    void markOutOfService(String service, String instanceId, HealthFailure failure) {
        instances.mark(service, instanceId, InstanceStatus.OUT_OF_SERVICE, failure);
        changeNotifier.notifyChange(service, ChangeType.STATUS_CHANGED, instanceId);
    }
}
```

The client library, where the interesting failure modes live:

```java
class DiscoveryClient {
    private final Map<String, CachedInstances> cache = new ConcurrentHashMap<>();
    private static final Duration CACHE_TTL = Duration.ofSeconds(10);
    private final CircuitBreaker registryBreaker = CircuitBreaker.of("registry");

    List<Endpoint> instancesOf(String service) {
        var cached = cache.get(service);
        if (cached != null && !cached.isExpired()) return cached.endpoints();

        return registryBreaker.executeSupplier(() -> {
            var fresh = registryClient.fetch(service, healthyOnly: true);
            cache.put(service, CachedInstances.of(fresh, Instant.now().plus(CACHE_TTL)));
            metrics.counter("discovery.fetch", "result", "fresh");
            return fresh;
        }, fallback -> {
            // FALLBACK, not failure. If the registry is down but our cache is warm, the
            // platform should keep working - degraded, not down. The cached list may point
            // at dead instances, which the circuit breaker on the CALL will absorb.
            var stale = cache.get(service);
            if (stale == null) throw new NoDiscoveryAvailableException(service);
            metrics.counter("discovery.fetch", "result", "stale_fallback");
            log.warn("registry unavailable, using stale endpoints for {} (age {})", service, stale.age());
            return stale.endpoints();       // may contain dead endpoints; caller must tolerate failures
        });
    }

    /** Long-poll keeps the cache warm without polling, and pushes changes rather than
     *  making every instance discover changes on its own schedule. */
    void watch(String service, Consumer<List<Endpoint>> onChange) {
        while (running) {
            try {
                var update = registryClient.watch(service, timeoutSeconds: 30);
                cache.put(service, CachedInstances.of(update.endpoints(), Instant.now().plus(CACHE_TTL)));
                onChange.accept(update.endpoints());
            } catch (RegistryUnavailableException e) {
                sleepWithBackoff();           // reconnect with exponential backoff + jitter
            }
        }
    }
}
```

A resilient HTTP caller on top, since a discovered endpoint may be dead:

```java
/**
 * Discovery tells you where an instance WAS. It does not tell you it is alive now. So the
 * caller needs its own resilience: retry the next endpoint, and report the instance as dead
 * to the registry so everyone else stops routing to it.
 */
class ResilientServiceCaller {
    byte[] get(String service, String path) {
        var endpoints = discovery.instancesOf(service);
        for (int attempt = 0; attempt < Math.min(3, endpoints.size()); attempt++) {
            Endpoint e = endpoints.get((startIndex.getAndIncrement()) % endpoints.size());
            try {
                return httpClient.send(e, path, timeout(Duration.ofMillis(800)));
            } catch (ConnectException | SocketTimeoutException ex) {
                // Fast-fail: skip to the next endpoint immediately rather than waiting for
                // the timeout. A 800ms timeout per attempt is a 2.4s worst case otherwise.
                discovery.markOutOfService(service, e.instanceId(), ex);
                metrics.counter("caller.instance_failed", "service", service, "cause", ex.getClass().getSimpleName());
            }
        }
        throw new AllInstancesFailedException(service, endpoints.size());
    }
}
```

Kubernetes DNS-based discovery, showing why you may not need to write the registry at all:

```yaml
# A headless Service (clusterIP: None) returns ALL ready pod IPs in DNS. This IS
# service discovery, provided by the platform, with health already integrated.
apiVersion: v1
kind: Service
metadata:
  name: orders-headless
spec:
  clusterIP: None
  selector: { app: orders }
  publishNotReadyAddresses: false   # only ready pods get DNS entries - readiness IS the health check
---
# A StatefulSet gives each pod a stable DNS name: orders-0.orders-headless.
# Required when the peer identity matters (sharding, leader election, a broker member id).
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: orders
spec:
  serviceName: orders-headless
  replicas: 3
  selector: { matchLabels: { app: orders } }
```

```java
/** DNS returns multiple A records; Java's InetAddress gives you all of them, and
 *  the ordering is rotated by the resolver so a simple round-robin happens naturally. */
List<Endpoint> discoverViaDns(String headlessService) {
    try {
        return Arrays.stream(InetAddress.getAllByName(headlessService))
                .map(addr -> new Endpoint(addr.getHostAddress(), 8080, headlessService))
                .toList();
    } catch (UnknownHostException e) {
        // No records = no ready pods, or the headless service is misconfigured. Both are
        // operational states worth distinguishing in the error, not a generic failure.
        throw new DiscoveryFailedException(headlessService, e);
    }
}
```

### Test It

```java
@Test void crashedInstanceIsEvictedAfterLeaseExpiry() {
    register("orders", instance("i-1"));
    // no heartbeats: simulate a hard crash
    clock.advance(Duration.ofSeconds(31));
    registry.evictExpiredLeases();
    assertThat(registry.resolve("orders")).isEmpty();
    assertThat(metrics.counter("registry.evicted", "reason", "lease_expired").count()).isEqualTo(1);
}

@Test void heartbeatingInstanceIsNotEvicted() {
    register("orders", instance("i-1"));
    repeat(6, () -> { clock.advance(Duration.ofSeconds(10)); registry.renew(registration); });
    registry.evictExpiredLeases();
    assertThat(registry.resolve("orders")).hasSize(1);
}

@Test void outOfServiceInstanceIsExcludedFromResolution() {
    register("orders", instance("i-1")); register("orders", instance("i-2"));
    registry.markOutOfService("orders", "i-1", new HealthFailure("readiness probe failed"));
    assertThat(registry.resolve("orders")).extracting(Endpoint::instanceId).containsExactly("i-2");
}

@Test void staleCacheIsUsedWhenRegistryIsDown() {
    discovery.instancesOf("orders");                      // warm the cache
    registry.goDown();
    // The platform keeps working. It may hit a dead endpoint, which the caller absorbs.
    assertThat(discovery.instancesOf("orders")).hasSize(2);
    assertThat(metrics.counter("discovery.fetch", "result", "stale_fallback").count()).isEqualTo(1);
}

@Test void callerFailsOverToAnotherInstanceOnConnectionRefused() {
    register("orders", deadInstance()); register("orders", liveInstance());
    assertThat(call("orders", "/api/orders")).isNotNull();       // succeeds via the live one
    assertThat(metrics.counter("caller.instance_failed").count()).isEqualTo(1);
}

@Test void allInstancesDownProducesAClearError() {
    register("orders", instance("i-1"));
    killAll();
    assertThatThrownBy(() -> call("orders", "/api/orders"))
        .isInstanceOf(AllInstancesFailedException.class)
        .hasMessageContaining("orders");
}

@Test void headlessServiceDnsReturnsOnlyReadyPods() {
    // in a kind cluster
    var endpoints = discoverViaDns("orders-headless.orders.svc.cluster.local");
    assertThat(endpoints).hasSize(3);
    // A pod that fails readiness is removed from DNS automatically.
    kubectl.exec("orders-1", "sh", "-c", "touch /tmp/not-ready");
    await().atMost(Duration.ofSeconds(30), () -> assertThat(discoverViaDns("orders-headless...")).hasSize(2));
}
```

## Deliverables

- [ ] Registry with ephemeral, lease-based registration and heartbeat renewal
- [ ] Eviction of expired leases, with a metric and a change notification
- [ ] Health filtering distinguishing registered from actually serving instances
- [ ] `OUT_OF_SERVICE` status distinct from removal, so cluster-wide failures stay visible
- [ ] Client library with a TTL cache, long-poll watch, and stale fallback on registry outage
- [ ] Circuit breaker on the registry call, falling back to the last known good list
- [ ] Resilient caller that fails over fast and reports dead instances back to the registry
- [ ] Kubernetes headless Service and StatefulSet manifests with a DNS resolution test
- [ ] A decision doc on when to use platform discovery versus your own registry
