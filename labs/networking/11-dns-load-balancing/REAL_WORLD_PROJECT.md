# DNS & Load Balancing - REAL WORLD PROJECT

## Project: EdgeRoute — global DNS and traffic management for a multi-region platform

The platform serves users in 12 countries from 4 regions. Requirements conflict: low latency
(so route to the nearest region), regulatory data residency (so some users must reach a
specific region), and a stated failover objective of 5 minutes (so TTLs must be short).
Those three requirements fight each other, and the resolution is the engineering work.

### Architecture

```
  User ──> Local resolver ──> Authoritative DNS (our service)
                                  │
                    policy decision on: resolver location, user, ASN,
                    data-residency rule, current health of each region
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
          eu-west-1           us-east-1          ap-southeast-1
          (primary for EU)    (primary for US)   (primary for APAC)
              │                   │                   │
              └───── health-based failover across regions ─────┘
                                  │
                    Regional load balancer (least-connections)
                                  │
                    Application instances

  TTL policy: 30s for the failover hostname (meet the 5-min objective)
              3600s for the documentation/marketing CDN hostname (cache efficiency)
```

### Implementation

Policy-based resolution, where health and residency override pure geography:

```java
class GeoPolicyEngine {
    /**
     * Pure geolocation is the wrong default for a regulated business. Order of precedence:
     *   1. Residency constraint: a user subject to a data-residency rule MUST be routed
     *      to an approved region, even if it is the slowest one for them. This is a
     *      compliance requirement, not a performance preference.
     *   2. Health: a region that is failing must never receive traffic, regardless of
     *      geography. A user in Frankfurt routed to a dead Frankfurt region is worse off
     *      than one routed to London.
     *   3. Latency: choose the healthy region with the lowest measured latency.
     */
    Resolution resolve(ResolverContext ctx) {
        Set<String> allowed = residencyEngine.allowedRegions(ctx.userCountry(), ctx.userAccount());
        List<String> candidates = allowed.stream().filter(regionHealth::isHealthy).toList();
        if (candidates.isEmpty()) {
            // Every approved region is down. Options: fail closed (compliance-safe but
            // an outage), or fail open to any healthy region (available but a compliance
            // breach). This is an explicit business decision, decided in advance, not
            // something a resolver should improvise.
            emergency.incident("all approved regions unhealthy", ctx);
            return emergencyPolicy.decide(ctx);            // recorded either way
        }
        return candidates.stream()
                .min(comparingDouble(r -> latencyHistory.medianMs(ctx.resolverLocation(), r)))
                .map(Resolution::to)
                .orElseThrow();
    }
}
```

Health-aware answers with weighted preference, so failover is gradual rather than a cliff:

```java
class AuthoritativeService {
    /**
     * Returning every healthy region's A record lets the client pick, which gives the
     * client's resolver the cache benefit but loses the policy decision. Returning one
     * record centralises policy but makes every failover wait for TTL expiry.
     *
     * Compromise: return healthy regions ordered by preference with WEIGHT and TTL, so
     * resolvers prefer the primary but still have working alternatives cached. Failover
     * then degrades gracefully as the primary ages out of caches.
     */
    Message answersFor(String qname, ResolutionContext ctx) {
        var ranked = policyEngine.rank(ctx);
        var records = new ArrayList<ResourceRecord>();
        for (int i = 0; i < ranked.size(); i++) {
            Region r = ranked.get(i);
            if (r.ttlSeconds() < FAILOVER_TTL_SECONDS) continue;   // do not advertise a dying region
            // Primary gets full weight; degraded regions get a small share so that a
            // partial failure shifts load gradually rather than causing a total cliff.
            int weight = r.isPrimary() ? 100 : (r.isDegraded() ? 10 : 60);
            for (IP ip : r.addresses()) records.add(aRecord(qname, ip, r.ttlSeconds(), weight));
        }
        if (records.isEmpty()) throw new AllRegionsDownException(qname);
        return new Message().answers(records).withAuthority(nsRecords()).withAdditional(aaaaRecords(ctx));
    }

    int ttlSecondsFor(String qname) {
        // TTL is a function of the SERVICE's failover requirement, not a global default.
        // A 5-minute failover objective with a 1-hour TTL is an objective you do not have.
        return serviceCatalog.get(qname).failoverObjective().toSeconds();
    }
}
```

The load balancer within a region, where long-lived connections make the algorithm choice matter:

```java
/**
 * DNS-level balancing gives roughly even distribution of NEW connections, which is nearly
 * useless for a platform with 30%-minute-long WebSocket and gRPC connections: one client
 * can pin a node's connection count for its whole session. So the real balancing is in
 * the regional balancer, which sees actual connection state.
 */
class RegionalBalancer {
    private final Map<Region, BalancerPool> pools = new ConcurrentHashMap<>();

    public Endpoint select(Region region, RequestContext ctx) {
        var pool = pools.computeIfAbsent(region, r -> new BalancerPool(
                backendsOf(r).stream().filter(Backend::isHealthy).toList(),
                BalancerAlgorithm.LEAST_CONNECTIONS));

        // Connection draining matters more than selection: a node being deployed must stop
        // receiving NEW connections while existing ones are honoured, or deploys cause drops.
        Endpoint e = pool.select();
        if (e.draining() && pool.hasAlternative(e)) return pool.selectExcluding(e);
        return e;
    }

    /** Graceful drain: stop advertising, wait for connections to finish or idle out. */
    void drain(Backend b, Duration gracePeriod) {
        b.draining(true);
        health.markUnhealthy(b);                    // excluded from selection immediately
        // Existing connections continue; websockets are held to a max lifetime, not killed.
        scheduler.schedule(() -> b.close(), gracePeriod.toMillis(), MILLISECONDS);
    }
}
```

Propagation reality, measured rather than assumed, feeding the failover objective:

```java
class PropagationMonitor {
    /**
     * The 5-minute objective is only credible if you measure how long stale answers
     * actually persist. This probes the authoritative server and several public resolvers
     * from multiple vantage points after a change, and reports the real distribution.
     */
    PropagationReport measureAfterChange(String qname, String previousPrimary) {
        var samples = new ArrayList<Instant>();
        for (int i = 0; i < 60; i++) {
            var answer = probePublicResolvers(qname);          // 8 resolvers, 3 regions
            if (!answer.contains(previousPrimary)) { samples.add(Instant.now()); break; }
            sleep(Duration.ofSeconds(5));
        }
        if (samples.isEmpty()) return PropagationReport.FAILED(qname, previousPrimary);
        return new PropagationReport(qname, samples.get(0),
                p50, p95, p99, slowResolvers);        // p99, not the best case, is the SLO number
    }
}
```

### Non-functional requirements

- **Resolution availability**: 99.99% for the authoritative service, anycast via multiple
  providers, with a secondary provider able to take over a zone.
- **Failover objective**: region failure detected within 30 s, traffic restored within
  5 minutes at p99, measured by the propagation monitor — not asserted.
- **Latency**: end-user TTFB p50 within 40 ms of the nearest healthy region, with the
  residency penalty (a latency-preferring user routed to their residency region) documented
  as an accepted, quantified trade-off.
- **TTL policy**: derived per service from the failover objective, reviewed quarterly. No
  service may have a TTL longer than its objective permits.
- **Health accuracy**: false-positive ejection is the more damaging error, so checks require
  consecutive failures and recovered regions ramp up gradually.
- **Residency compliance**: rules enforced in DNS so a violation is impossible at the
  routing layer, with an explicit, logged decision for the all-approved-regions-down case.
- **Capacity**: registration storms (a viral event, a failover) must not exhaust authoritative
  capacity. Anycast plus a provider with proven scale headroom.
- **Observability**: resolution latency per region, ejection events, propagation percentiles
  after every change, and per-region traffic distribution versus expected share.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 1034/1035 define the DNS namespace, record types, and the caching behaviour that
  determines how long a TTL change takes to take effect.
  https://www.rfc-editor.org/info/rfc1035/
- RFC 2181 clarifies DNS caching and TTL semantics, including the guidance that cached data
  must be bounded by the record TTL, which underpins the TTL policy derived from the
  failover objective.
  https://www.rfc-editor.org/info/rfc2181/
- RFC 2308 defines negative caching and the derivation of the negative TTL from the SOA
  minimum field, which the caching resolver uses to stop a nonexistent-name flood.
  https://www.rfc-editor.org/info/rfc2308/
- MDN's DNS documentation describes recursive resolution, record types, and the caching
  layer that determines how long a TTL change takes to reach clients.
  https://developer.mozilla.org/en-US/docs/Glossary/DNS

## Deliverables

- [x] Policy engine with residency constraint taking precedence over latency
- [x] Health-based exclusion before latency-based ranking
- [x] Explicit, logged decision path for the all-approved-regions-down case
- [x] Weighted answers with graceful degradation instead of a failover cliff
- [x] Per-service TTL derived from each service's stated failover objective
- [x] Least-connections balancing with connection draining for deployments
- [x] Ramp-up admission for recovered regions to avoid repeat failure
- [x] Propagation monitor reporting p50/p95/p99 from multiple public resolver vantage points
