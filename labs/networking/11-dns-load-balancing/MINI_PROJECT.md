# DNS & Load Balancing - MINI PROJECT

## Project: ResolverLab — a DNS server, a caching resolver, and a balancer with health checks

Implement a minimal authoritative DNS server, a caching recursive resolver, and two
load-balancing algorithms with health checks. Then measure the caching trade-off directly.

### Architecture

```
  Client ──> Local stub resolver ──> Root (delegation for .com)
                                          │  cache the delegation + its TTL
                                          ▼
                                    TLD (.com) ──> (delegation for example.com)
                                                        │  cache again
                                                        ▼
                                              Authoritative (our server)
                                                 A records with TTLs
                                                 SRV records for ports

  Cache layers, each with its own TTL and each a suspect when answers are stale:
    client OS resolver → recursive resolver (unbound/CoreDNS) → authoritative

  Balancer (application level, where sticky affinity is possible):
    RoundRobin | WeightedRoundRobin | LeastConnections
    + health checker on an interval, with jitter and a ramp-up period
```

### Implementation

A minimal authoritative server answering A, SRV, and SOA queries:

```java
@Component
class AuthoritativeDnsServer {
    private final Map<QName, RecordSet> zone = new ConcurrentHashMap<>();
    private final int defaultTtl = 60;

    void start(int port) throws IOException {
        DatagramSocket socket = new DatagramSocket(port);
        new Thread(() -> serve(socket), "dns-udp").start();
        // TCP is required too: responses larger than 512 bytes, and zone transfers,
        // must use TCP. A UDP-only server is a server that fails on a large answer.
        new Thread(() -> serveTcp(socket.getLocalPort()), "dns-tcp").start();
    }

    void serve(DatagramSocket socket) {
        byte[] buf = new byte[512];
        while (running) {
            DatagramPacket in = new DatagramPacket(buf, buf.length);
            socket.receive(in);
            try {
                Message query = new Message(in.getData());
                Message response = resolve(query);
                byte[] out = response.toWire();
                socket.send(new DatagramPacket(out, out.length, in.getAddress(), in.getPort()));
                metrics.counter("dns.query", "qname", qnameLabel(query), "rcode", response.rcodeName()).increment();
            } catch (Exception e) {
                metrics.counter("dns.error", "cause", e.getClass().getSimpleName()).increment();
            }
        }
    }

    private Message resolve(Message query) {
        Message response = new Message(query.header().id());
        response.header().qr(true).aa(true).rd(query.header().rd()).ra(true);

        if (query.questionCount() != 1) return response.rcode(RCode.FORMERR);
        Question q = query.question(0);
        // Only A and SRV are supported; anything else must be answered with NOTIMP
        // rather than NOERROR and no answer, which clients interpret as "empty".
        if (!SUPPORTED.contains(q.type())) return response.rcode(RCode.NOTIMP);

        RecordSet rs = zone.get(new QName(q.name()));
        if (rs == null) {
            // NXDOMAIN must be distinguishable from NODATA, and both are cacheable.
            // Returning an empty NOERROR for a nonexistent name is a real bug class.
            return zoneHasAnythingUnder(q.name()) ? response.rcode(RCode.NOERROR).withSoa(soa())
                                                  : response.rcode(RCode.NXDOMAIN).withSoa(soa());
        }
        response.answer(rs.records(q.type())).withSoa(soa());   // SOA in every answer for negative caching
        return response;
    }
}
```

The caching resolver, where TTL handling and negative caching actually live:

```java
class CachingResolver {
    private final Cache<String, CachedAnswer> cache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofSeconds(1))      // checked at lookup; entries carry their own TTL
            .maximumSize(100_000)
            .build();

    Message resolve(String qname, int type) {
        CachedAnswer hit = cache.getIfPresent(key(qname, type));
        // Honour the record's TTL, not a global one. A 30s TTL and a 1h TTL are both
        // legitimate, and a fixed cache TTL is either stale-serving or hammering upstream.
        if (hit != null && !hit.isExpired()) {
            metrics.counter("dns.cache.hit");
            return hit.message();
        }
        metrics.counter("dns.cache.miss");
        Message answer = forwardToAuthoritative(qname, type);
        cache.put(key(qname, type), CachedAnswer.of(answer, ttlOf(answer, type)));
        return answer;
    }

    /**
     * Negative caching matters as much as positive caching. Without it, a typo'd domain
     * generates a fresh upstream query for every request, and a nonexistent-name flood
     * becomes a self-inflicted DDoS against your own authoritative servers.
     */
    Duration ttlFor(Message answer, int type) {
        if (answer.rcode() == NXDOMAIN) return Duration.ofSeconds(300);
        if (answer.answerCount() == 0) {
            // RFC 2308: negative TTL is the minimum of the SOA TTL and the SOA minimum field.
            long soaTtl = soaTtlOf(answer);
            long soaMinimum = soaMinimumOf(answer);
            return Duration.ofSeconds(Math.min(soaTtl, soaMinimum));
        }
        return Duration.ofSeconds(ttlOfFirstAnswer(answer, type));
    }
}
```

Balancing algorithms, with the property that matters for each:

```java
/** RoundRobin: fair over connections, unfair over requests. One slow client gets 1/N. */
class RoundRobinBalancer implements Balancer {
    private final AtomicInteger cursor = new AtomicInteger();
    public Backend select(List<Backend> healthy) {
        int i = Math.floorMod(cursor.getAndIncrement(), healthy.size());
        return healthy.get(i);
    }
}

/** WeightedRoundRobin: supports heterogeneous capacity and canary rollouts. 5% to the canary. */
class WeightedRoundRobinBalancer implements Balancer {
    private final SmoothWeightedRR scheduler = new SmoothWeightedRR();
    public Backend select(List<Backend> healthy) {
        // Smooth WRR avoids bursts: a large weight still spreads its share over time,
        // so a single client never lands on the canary several times in a row.
        return scheduler.next(healthy);
    }
}

/** LeastConnections: the right default when request cost varies wildly (a report endpoint
 *  next to a health check). Round robin sends the expensive request to an overloaded node. */
class LeastConnectionsBalancer implements Balancer {
    public Backend select(List<Backend> healthy) {
        return healthy.stream().min(comparingInt(Backend::activeConnections)).orElseThrow();
    }
}
```

Health checking that does not create an outage on recovery:

```java
@Component
class HealthChecker {
    /**
     * Three failure modes this design avoids:
     *  1. Synchronised checks -> a thundering herd. Fixed interval: solved with jitter.
     *  2. Aggressive eject -> a slow node is removed, then re-added, flapping. Needs a
     *     small failure threshold before ejection, and a RAMP-UP period before the node
     *     is trusted with full traffic.
     *  3. Check path that lies -> a /health that returns OK while the service is useless.
     *     The check must exercise a real dependency (a DB round trip), not a static file.
     */
    @Scheduled(fixedDelayString = "${health.interval:5000}")
    void check() {
        long jitter = ThreadLocalRandom.current().nextLong(0, JITTER_MS);   // desynchronise
        scheduler.schedule(() -> backends.forEach(this::probe), jitter, MILLISECONDS);
    }

    private void probe(Backend b) {
        boolean up = probeRealDependency(b);     // e.g. SELECT 1 plus a cache read
        if (up) {
            b.consecutiveFailures().set(0);
            // Ramp-up: a recovered node is admitted at a fraction of traffic and promoted
            // gradually, so a node that is not actually ready is not sent all the traffic.
            if (b.state() == State.RECOVERING) {
                b.weightPercent(b.weightPercent() + RAMP_STEP);
                if (b.weightPercent() >= 100) b.state(State.HEALTHY);
            }
        } else {
            int failures = b.consecutiveFailures().incrementAndGet();
            if (failures >= FAILURE_THRESHOLD) {           // 3 consecutive, not 1
                if (b.state() == State.HEALTHY) metrics.counter("balancer.ejected", "backend", b.id());
                b.state(State.UNHEALTHY);
                balancer.removeFromRotation(b);
            }
        }
    }
}
```

### Test It

```java
@Test void servesARecordsWithTheConfiguredTtl() {
    var response = queryAuthoritative("api.example.com", Type.A);
    assertThat(response.rcode()).isEqualTo(NOERROR);
    assertThat(response.answerCount()).isEqualTo(2);
    assertThat(ttlOfFirstAnswer(response)).isEqualTo(30);
}

@Test void distinguishesNxdomainFromNodata() {
    assertThat(queryAuthoritative("nope.example.com", Type.A).rcode()).isEqualTo(NXDOMAIN);
    assertThat(queryAuthoritative("api.example.com", Type.TXT).rcode()).isEqualTo(NOERROR);  // name exists, no TXT
}

@Test void negativeCachingPreventsUpstreamFlood() {
    // A nonexistent name must not cause a fresh upstream query on every request.
    repeat(100, () -> resolver.resolve("typo.example.com", Type.A));
    assertThat(metrics.counter("dns.upstream.query", "qname", "typo.example.com").count()).isEqualTo(1);
}

@Test void cacheHonoursEachRecordsOwnTtl() {
    queryAuthoritative("short.example.com", Type.A);   // TTL 5
    queryAuthoritative("long.example.com", Type.A);    // TTL 3600
    resolver.resolve("short.example.com", Type.A);
    resolver.resolve("long.example.com", Type.A);
    assertThat(metrics.counter("dns.cache.hit", "qname", "long.example.com").count()).isEqualTo(1);
    assertThat(metrics.counter("dns.cache.hit", "qname", "short.example.com").count()).isZero();
}

@Test void leastConnectionsPrefersTheIdleNode() {
    var busy   = backend(activeConnections: 50, state: HEALTHY);
    var idle   = backend(activeConnections: 2,  state: HEALTHY);
    assertThat(leastConnections.select(List.of(busy, idle))).isEqualTo(idle);
}

@Test void recoveredNodeRampsUpBeforeFullTraffic() {
    var b = backend(state: RECOVERING, weightPercent: 20);
    repeat(20, () -> healthChecker.probe(b));
    assertThat(b.state()).isEqualTo(HEALTHY);
    assertThat(b.weightPercent()).isEqualTo(100);
}
```

## Deliverables

- [ ] Authoritative DNS server over both UDP and TCP, answering A, SRV, and SOA
- [ ] Correct NXDOMAIN vs NODATA distinction with SOA in every response
- [ ] Caching resolver honouring per-record TTLs, with RFC 2308 negative caching
- [ ] A test proving negative caching prevents an upstream query flood
- [ ] Three balancing algorithms: round robin, smooth weighted, least connections
- [ ] Health checker with jitter, a failure threshold, and a ramp-up period
- [ ] A check that exercises a real dependency, documented as a deliberate choice
- [ ] Benchmarks: balancing distribution fairness and cache hit rate under load
- [ ] A DNS TTL policy doc tying TTL values to a stated failover objective
