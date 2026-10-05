# DNS & Load Balancing - CODE DEEP DIVE

## 1. The message codec — why a hand-rolled parser is instructive

A DNS message is length-prefixed TLV records, which makes encoding and decoding
deceptively short. The instructive parts are the **compression rules**, because they are
where implementations break.

```java
final class DnsName {
    /**
     * DNS names are a sequence of length-prefixed labels, terminated by a zero byte.
     * Message compression replaces a repeated suffix with a two-byte POINTER whose top
     * two bits are 11. This is why a naive decoder that treats the pointer as an offset
     * either loops forever (following a self-reference) or reads garbage.
     */
    static void writeTo(ByteBuffer out, String name, Map<String, Integer> compression) {
        String[] labels = name.split("\\.");
        for (int i = 0; i < labels.length; i++) {
            byte[] label = labels[i].getBytes(US_ASCII);
            if (label.length > 63) throw new IllegalArgumentException("label too long: " + labels[i]);
            String suffix = joinFrom(labels, i);
            Integer pointer = compression.get(suffix);
            if (pointer != null && pointer < 0x4000) {
                // Write the pointer instead of the remaining labels.
                out.putShort((short) (0xC000 | pointer));
                return;
            }
            compression.putIfAbsent(suffix, out.position());
            out.put((byte) label.length);
            out.put(label);
        }
        out.put((byte) 0);      // root label: names are fully qualified, always with this terminator
    }

    /**
     * Decompression requires a jump budget. Without one, a malicious response containing
     * a pointer to itself is an infinite loop and a trivial denial of service against
     * your resolver - which is exactly what makes this a security-relevant decoder.
     */
    static String readFrom(ByteBuffer in, int msgStart) {
        var labels = new ArrayList<String>();
        int budget = MAX_POINTER_JUMPS;         // e.g. 32
        int pos = in.position();
        boolean jumped = false;
        while (budget-- > 0) {
            int len = in.get() & 0xFF;
            if (len == 0) { in.position(pos); break; }
            if ((len & 0xC0) == 0xC0) {          // pointer
                int offset = ((len & 0x3F) << 8) | (in.get() & 0xFF);
                if (!jumped) { pos = in.position(); jumped = true; }
                // A pointer must point BACKWARD. A forward pointer permits loops.
                if (offset >= in.position() && offset != msgStart) throw new MalformedNameException("forward pointer");
                in.position(offset);
                continue;
            }
            if (len > 63) throw new MalformedNameException("label length out of range");
            byte[] label = new byte[len];
            in.get(label);
            labels.add(new String(label, US_ASCII));
        }
        if (budget <= 0) throw new MalformedNameException("pointer jump budget exhausted");
        return String.join(".", labels);
    }
}
```

## 2. Cache correctness — the part that is easy to get subtly wrong

```java
final class CachedAnswer {
    private final Message message;
    private final Instant expiresAt;

    /**
     * EXPIRY IS PER ANSWER, NOT PER CACHE. A single fixed cache TTL is either
     *   - too long for the 30s record, so you serve stale answers and your failover
     *     objectively is fiction, or
     *   - too short for the 3600s record, so you re-query authoritative servers 120x more
     *     often than necessary and turn your own popularity into self-inflicted load.
     */
    boolean isValidAt(Instant now) {
        return now.isBefore(expiresAt);
    }
}
```

The negative-caching derivation, where a single wrong `min` produces a real bug:

```java
/**
 * RFC 2308: the negative TTL is the MINIMUM of the SOA record's own TTL and the SOA
 * MINIMUM field. Using only one of the two is the classic mistake - and the direction of
 * the error matters. Too long a negative TTL means a newly created name is invisible to
 * clients for longer than the zone owner intended, which breaks a launch.
 */
Duration negativeTtl(Message response) {
    Soa soa = response.authority().stream()
            .filter(r -> r.type() == Type.SOA)
            .map(Soa::from)
            .findFirst()
                            // No SOA in authority means NO negative caching is possible.
                            // Return zero, not a default: a fabricated default is a policy
                            // decision hidden in a parsing routine.
            .orElse(Duration.ZERO);
    return Duration.ofSeconds(Math.min(soa.ttl(), soa.minimum()));
}
```

## 3. The eviction loop — a scheduling bug with an operational signature

```java
@Scheduled(fixedRate = 5_000)
void evictExpiredLeases() {
    for (var entry : services.entrySet()) {
        entry.getValue().values().removeIf(record -> {
            if (record.leaseExpiresAt().isBefore(clock.instant())) {
                changeNotifier.notifyChange(entry.getKey(), ChangeType.EVICTED, record.instance().id());
                return true;
            }
            return false;
        });
    }
}
```

Two things a reviewer should notice here, both of which appear in production:

1. **Order of operations.** The notification fires *inside* `removeIf`, so a notifier that
   is slow or throws can prevent the removal — leaving a dead instance in rotation
   indefinitely. Remove first, notify second.
2. **Clock source.** `record.leaseExpiresAt().isBefore(clock.instant())` is correct only if
   every write and comparison uses the same clock. Mixing `Instant.now()` and an injected
   test clock produces an eviction test that passes for the wrong reason.

## 4. Balancing under skew — reading the numbers correctly

```java
final class LeastConnectionsBalancer implements Balancer {
    Backend select(List<Backend> healthy) {
        /**
         * Ties and the "least loaded is the target of everyone" problem: a strict
         * min() makes all clients converge on the same idle backend, then it becomes the
         * hot one, then they all move. Adding the selection itself to the load, plus a
         * randomised tie-break, removes the convergence without the cost of full
         * power-of-two-choices sampling.
         */
        var min = healthy.stream().mapToInt(Backend::activeConnections).min().orElseThrow();
        var candidates = healthy.stream()
                .filter(b -> b.activeConnections() <= min + tieTolerance)
                .collect(toList());
        var chosen = candidates.get(ThreadLocalRandom.current().nextInt(candidates.size()));
        chosen.recordSelection();
        return chosen;
    }
}
```

The **tie tolerance** is a real parameter. With `tolerance = 0` and integer counters, two
backends at 0 connections look identical forever and clients split unevenly between them.
With a tolerance of 1, a genuinely idle backend is still preferred, but the pool does not
oscillate.

## 5. Health check transitions — the state machine that prevents flapping

```java
/**
 * States and the only legal transitions:
 *
 *   HEALTHY    --(N consecutive failures)-->  UNHEALTHY   (ejected, no traffic)
 *   UNHEALTHY  --(1 success)------------->   RECOVERING  (small share of traffic)
 *   RECOVERING --(success, weight++)------>  RECOVERING
 *   RECOVERING --(weight >= 100%)--------->   HEALTHY
 *   RECOVERING --(1 failure)-------------->   UNHEALTHY
 *
 * The direct UNHEALTHY -> HEALTHY edge is deliberately absent. A node that was just
 * failing is not trusted immediately on its first success: a single lucky response after
 * a restart is not evidence of readiness, and admitting it at full weight reproduces
 * the original outage.
 */
enum State { HEALTHY, UNHEALTHY, RECOVERING }
```

The subtlety in `RECOVERING` is that the node is neither fully in nor fully out:

```java
private void probe(Backend b) {
    boolean healthy = probeRealDependency(b);       // a DB round trip, not a static file
    if (!healthy) {
        b.consecutiveFailures().incrementAndGet();
        if (b.consecutiveFailures() >= FAILURE_THRESHOLD) transition(b, State.UNHEALTHY);
        else if (b.state() == State.RECOVERING) transition(b, State.UNHEALTHY);
        return;
    }
    b.consecutiveFailures().set(0);
    if (b.state() == State.RECOVERING) {
        b.weightPercent(b.weightPercent() + RAMP_STEP);
        if (b.weightPercent() >= 100) transition(b, State.HEALTHY);
    } else if (b.state() == State.UNHEALTHY) {
        transition(b, State.RECOVERING);
        b.weightPercent(RAMP_START_PERCENT);         // start small, not at the ramp step
    }
}
```

## 6. Jitter — one line that prevents an outage

```java
@Scheduled(fixedDelayString = "${health.interval:5000}")
void check() {
    /**
     * Without jitter, every backend is probed at the same instant, every probe times out
     * at the same instant during a shared upstream blip, and the whole fleet is ejected
     * together. A fixed interval converts a partial dependency problem into a total one.
     */
    for (Backend b : backends) {
        long jitter = ThreadLocalRandom.current().nextLong(0, MAX_JITTER_MS);
        scheduler.schedule(() -> safeProbe(b), jitter, MILLISECONDS);
    }
}
```

## 7. Debugging guide: which cache is lying to you?

| Symptom | Most likely cache | Command |
|---|---|---|
| Change not visible from one machine | Client OS / JVM `InetAddress` cache | `dig @127.0.0.1 <name>` vs `dig <name>` |
| Change not visible from an office | Recursive resolver cache | `dig @8.8.8.8 <name>` |
| Change not visible anywhere | Authoritative server, or zone transfer not done | `dig +norecurse @ns1.example.com <name>` |
| New name does not resolve | Negative cache (NXDOMAIN TTL) | `dig <name>` — check SOA TTL and MINIMUM |
| One client pinned to a dead node | Client cached the multi-record answer set | `dig <name> A` — expect several records |

A useful discipline when debugging DNS is to add `+trace`, which walks the delegation
chain and shows the TTL remaining in each cache — the tool turns "it is not working" into
"it is stuck at hop 3 with 240 seconds remaining".

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 1035 §4.1.4 specifies message compression and the pointer format decoded above,
  including the label length limits enforced during parsing.
  https://www.rfc-editor.org/info/rfc1035/
- RFC 2181 §5.2 discusses the robustness requirements for a DNS implementation, including
  the pointer-jump constraints that prevent loops.
  https://www.rfc-editor.org/info/rfc2181/
