# Service Discovery - REAL WORLD PROJECT

## Project: ServiceMap — one service inventory for 200 services across three platforms

Services run on Kubernetes (new), on VMs in a data centre (legacy, migrating), and on
bare metal for low-latency trading components. There is no single platform to ask, so the
company has no single answer to "where is service X and is it healthy?" — which means
on-call engineers guess during incidents.

### Architecture

```
  Kubernetes (150 services)  ──▶ kube-dns / API ──┐
  VM estate (40 services)    ──▶ file-based registration ──┤
  Bare metal (10 services)  ──▶ agent registration ───────┤
                                                             ▼
  ┌──────────────────── ServiceMap (unified registry) ─────────────────────┐
  │  registration: k8s informer (no per-pod polling), agent gRPC, file      │
  │  model: service -> versions -> endpoints (host, port, zone, platform)  │
  │  health: readiness for k8s; active probe for VM/bare metal             │
  │  metadata: owner team, tier, SLO, on-call rota, dependencies           │
  └──────────┬─────────────────────────────┬──────────────────────────────┘
             │                             │
             ▼                             ▼
     Service clients (SDK)        Ops: dependency graph, impact analysis,
     (discovery + failover)       ownership lookup during an incident
```

### Implementation

Registration adapters per platform, producing one normalised model:

```java
interface RegistrationSource {
    Stream<ServiceInstance> instances();
    Flux<ServiceInstance> changes();      // push where possible; poll only where necessary
}

/** Kubernetes: an informer gives a watch stream, so we do not poll the API server per pod. */
@Component
class KubernetesRegistrationSource implements RegistrationSource {
    private final SharedIndexInformer endpointInformer;
    private final EndpointsListerWatcher watcher;   // Endpoints objects already track readiness

    @Override public Stream<ServiceInstance> instances() {
        return endpointInformer.getStore().values().stream().map(this::toServiceInstance);
    }

    @Override public Flux<ServiceInstance> changes() {
        // Endpoints objects are exactly the right primitive: Kubernetes already filtered
        // out pods that are not ready. Re-deriving health ourselves would duplicate and
        // eventually disagree with the platform.
        return Flux.create(sink -> watcher.addEventHandler(new ResourceEventHandler<Endpoints>() {
            @Override public void onAdd(Endpoints obj) { sink.next(toServiceInstance(obj)); }
            @Override public void onUpdate(Endpoints old, Endpoints now) { sink.next(toServiceInstance(now)); }
            @Override public void onDelete(Endpoints obj, boolean deletedFinalStateUnknown) { sink.next(removed(obj)); }
        }));
    }

    private ServiceInstance toServiceInstance(Endpoints ep) {
        return new ServiceInstance(
                name: ep.getMetadata().getName(),
                endpoint: firstAddressPort(ep),
                zone: nodeZoneOf(ep),
                platform: Platform.KUBERNETES,
                // Metadata that makes the registry useful during an incident: without an
                // owner, discovery answers "where" but not "who do I call about it".
                ownerTeam: annotationOf(ep, "ops.example.com/owner"),
                tier: annotationOf(ep, "ops.example.com/tier"),
                onCall: onCallRota.lookup(ep.getMetadata().getName()));
    }
}
```

Active health checking for the platforms that lack a readiness concept:

```java
@Component
class ActiveHealthChecker {
    /**
     * Kubernetes needs none of this (readiness gates traffic). VM and bare metal services
     * do, so we probe them. The probe must exercise a real dependency, not a static health
     * endpoint that returns OK while the service cannot reach its database - a health check
     * that lies is worse than no health check, because it creates false confidence.
     */
    @Scheduled(fixedDelay = 10_000)
    void probeNonKubernetesInstances() {
        for (ServiceInstance i : registry.instancesOn(Platform.VM, Platform.BARE_METAL)) {
            long jitter = ThreadLocalRandom.current().nextLong(0, 2000);
            scheduler.schedule(() -> {
                ProbeResult r = prober.probeDeep(i, timeout: Duration.ofSeconds(2));
                if (!r.healthy()) {
                    i.consecutiveFailures().incrementAndGet();
                    if (i.consecutiveFailures().get() >= 3) {   // 3 in a row, not 1
                        registry.markOutOfService(i, r.failureDetail());
                        // A probe failure on 5+ instances of one service is an incident,
                        // not 5 independent health problems. Aggregate before alerting.
                        if (registry.failingInstancesOf(i.service()).size() >= 5)
                            incidents.open("SERVICE_WIDE_HEALTH_FAILURE", i.service(), r.failureDetail());
                    }
                } else {
                    i.consecutiveFailures().set(0);
                    registry.markServing(i);
                }
            }, jitter, MILLISECONDS);
        }
    }
}
```

The client SDK, the piece every internal team actually consumes:

```java
/** One artifact for all three platforms, so teams do not write discovery code per environment. */
public final class ServiceClient {
    public <T> T call(String service, String path, Class<T> responseType) {
        return call(service, path, responseType, Duration.ofSeconds(2));
    }

    public <T> T call(String service, String path, Class<T> responseType, Duration budget) {
        var attempts = 0;
        var endpointList = discovery.instancesOf(service);
        while (attempts < maxAttempts(service)) {
            var endpoint = pick(endpointList, attempts);          // least-connections aware
            var remaining = budget.minus(elapsed());             // deadline propagates
            if (remaining.isNegative()) break;
            try {
                return http.get(endpoint, path, remaining, responseType);
            } catch (RetryableException e) {
                attempts++;
                if (e instanceof TimeoutException) {
                    // A timeout may be the instance being slow OR the network. Marking it
                    // out of service on a single timeout is wrong: one slow response during
                    // a GC pause would evict a healthy instance fleet-wide.
                    discovery.reportSlow(endpoint, e.elapsed());
                } else {
                    discovery.reportUnhealthy(endpoint, e);       // connection refused: definite
                }
            }
        }
        throw new ServiceUnavailableException(service, attempts);
    }

    /** Cross-region fallback for the handful of services with an explicit DR dependency. */
    List<Endpoint> withCrossRegionFallback(String service) {
        var local = discovery.instancesOf(service, currentZone());
        if (!local.isEmpty() && discovery.healthyRatio(service, currentZone()) > MIN_RATIO) return local;
        var remote = discovery.instancesOf(service).stream().filter(e -> !e.zone().equals(currentZone())).toList();
        return remote.isEmpty() ? local : remote;                // higher latency, but serving
    }
}
```

The dependency graph, which is what turns a registry into an incident tool:

```java
/**
 * During an incident the question is not "is the service up" but "what breaks if it is
 * not". The graph is built from observed traffic (not configuration), because configured
 * dependencies are always out of date and missing the runtime-only ones.
 */
@Component
class DependencyGraph {
    @Scheduled(fixedDelay = 60_000)
    void rebuildFromObservations() {
        var observed = telemetry.clientCallAggregates(Duration.ofMinutes(5), minCalls: 100);
        for (var edge : observed)
            graph.addEdge(edge.caller(), edge.callee(), new EdgeMetadata(
                    callCountPerMinute: edge.rate(),
                    isCritical: criticalityRegistry.isCritical(edge.caller(), edge.callee()),
                    observedSince: edge.firstSeen()));
        // Edges that stopped being observed are removed: a dependency that no longer
        // happens is not a dependency, however confident the design document is.
        graph.pruneUnobserved(Duration.ofHours(1));
    }

    /** "What is the blast radius if this service is down?" - answered in one query. */
    ImpactReport impactOf(String service) {
        var dependents = graph.reverseEdgesOf(service);
        return new ImpactReport(service,
                transitiveDependents: graph.transitiveDependents(service, maxDepth: 3),
                byCriticality: groupBy(dependents, Edge::isCritical),
                owners: distinctOwnersOf(dependents),
                onCall: onCallRota.forServices(dependents),
                // Undocumented edges are a real finding: something calls this service that
                // the owning team did not know about.
                undocumented: dependents.stream().filter(e -> !cmdb.knows(e.caller(), e.callee())).toList());
    }
}
```

### Non-functional requirements

- **Registry availability**: 99.95%. The SDK's stale-fallback path means a registry outage
  degrades discovery rather than cascading it into a platform outage — this is the single
  most important reliability property of the design.
- **Convergence**: a scale-up or scale-down is reflected in discovery within 15 seconds.
  Kubernetes is event-driven (sub-second); VM estates are polled on a 10 s interval, which
  is an accepted, documented trade-off.
- **Health accuracy**: Kubernetes uses readiness (authoritative); VM/bare metal uses deep
  probes with a 3-failure threshold. A single timeout never evicts an instance.
- **Coverage**: 200/200 services registered, with owner, tier, SLO, and on-call rota for
  100% of them. A registration missing ownership metadata is rejected at write time,
  because a registry entry nobody owns is an incident dead end.
- **Client cost**: discovery adds under 0.5 ms at p99 from cache. No per-request registry
  call, ever.
- **Accuracy**: false ejection under 0.1% of instances per day. Measured by comparing
  ejections against actual service availability.
- **Impact analysis**: transitive dependents to depth 3 in under 200 ms, which is what makes
  it usable on a call.
- **Migration**: the VM estate moves to Kubernetes service by service; the unified model
  means no client code changes during migration, which is the whole point of the adapter.
- **Governance**: dependency edges from observation are reviewed monthly, and a
  "call something you do not own" report drives architecture cleanup.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes Endpoints objects (and EndpointSlices) expose the ready addresses for a
  Service, which is the authoritative source used by the informer-based adapter above.
  https://kubernetes.io/docs/concepts/services-networking/service/
- Kubernetes DNS for Services and Pods documents headless services and per-pod DNS names,
  which cover most discovery needs without a custom registry.
  https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
- Spring Cloud reference documents the `DiscoveryClient` abstraction and the composite
  client that backs the unified SDK, including its caching and order-of-preference behaviour.
  https://docs.spring.io/spring-cloud/reference/

## Deliverables

- [x] Unified instance model with registration adapters for Kubernetes, VM, and bare metal
- [x] Event-driven Kubernetes adapter with no per-pod API polling
- [x] Deep active health probes for non-Kubernetes platforms with a 3-failure threshold
- [x] Registration rejected at write time when owner/tier/on-call metadata is missing
- [x] Client SDK with least-connections selection, deadline propagation, and fast failover
- [x] Cross-region fallback for services with an explicit DR dependency
- [x] Stale-fallback on registry outage so a registry failure does not become a platform failure
- [x] Observation-based dependency graph with impact analysis, ownership, and drift findings
