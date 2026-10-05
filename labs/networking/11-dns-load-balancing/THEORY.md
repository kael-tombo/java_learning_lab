# DNS & Load Balancing - THEORY

## 1. What DNS actually does

DNS is a distributed, cached, hierarchical naming system. A client asks "what is the
address for `api.example.com`?" and the answer may be computed by four different servers
and then cached in three different places before it reaches the client.

The critical insight: **DNS is a caching system with deliberately inconsistent views.**
This is not a bug to be fixed; it is what makes DNS scale. The consequence for engineers is
that a change you make is not immediately visible everywhere, and the delay is not one
number — it is a distribution across many caches with different ages.

## 2. The resolution chain

```
 1. Application        getaddrinfo("api.example.com") or a DNS library
 2. Stub resolver      /etc/resolv.conf points here; usually the OS or a local daemon
 3. Recursive resolver Answers authoritatively. Caches everything it learns.
 4. Root servers       "I don't know, ask the .com servers." 13 root server addresses,
                       anycast, massively over-provisioned
 5. TLD servers        ".com is managed by these two name servers"
 6. Authoritative      "api.example.com = 93.184.216.34, TTL 300"
```

Three cache layers, and each can be the reason a change has not taken effect:

- **Client-side cache**: the OS resolver, the JVM's `InetAddress` cache, the browser.
  The JVM default is 30 seconds when a security manager is absent, forever when one is
  present — a classic source of "the change worked for my colleague but not for me".
- **Recursive resolver cache**: shared across many clients, so one lookup populates the
  cache for thousands of requests. This is where most of the propagation delay lives.
- **Authoritative server cache**: some authoritative servers cache zone data too, and
  secondary nameservers hold a zone file that is only updated by zone transfer.

## 3. Recursive vs iterative

| | Recursive | Iterative |
|---|---|---|
| Question | "Give me the final answer" | "Give me a referral / the next step" |
| Answer | The A record, or an error | Who to ask next |
| Who iterates | Nobody — the resolver walks the chain | Each server, in turn |

Clients ask **recursively** because a stub resolver should not need to know the whole
hierarchy. The recursive resolver asks **iteratively**, caching each referral. This split
is what keeps root and TLD servers fast: they answer millions of queries a second from
cached referrals, and never fetch anything.

## 4. Record types and what each one actually does

- **A** — name → IPv4. The basic answer.
- **AAAA** — name → IPv6. Presence matters: a name with A but no AAAA is treated by some
  clients as "no IPv6", while a broken AAAA record can make resolution fail entirely.
- **CNAME** — alias to another name. **It cannot coexist with other record types at the
  same name**, which is why a CNAME cannot point at a name that also has MX records. Every
  CNAME adds a resolution step, so chains add latency and grow the failure surface.
- **SRV** — service, protocol, priority, weight, port, target. Real load balancing
  information. Weight (RFC 2782) allows proportional selection, which is genuinely useful.
- **TXT** — arbitrary text. SPF, DKIM, domain verification. Also the vector for
  subdomain-takeover checks and data exfiltration over DNS.
- **SOA** — Start of Authority. Zone metadata, and the serial number used to detect zone
  changes. Its TTL and minimum fields also govern negative caching (see §5).

## 5. TTL and negative caching

TTL is the number of seconds an answer may be cached. The engineering consequence:

- **Short TTL** (30s): fast failover, but more queries — every cache expiry generates an
  upstream query, so short TTLs across a popular name can measurably load your
  authoritative servers.
- **Long TTL** (3600s): excellent cache efficiency, and a failover that takes the full hour
  to take effect everywhere. A stated "5-minute failover objective" with a 1-hour TTL is an
  objective you do not have.

**Negative caching** (RFC 2308) matters as much and is routinely forgotten. Without it, a
client asking for `exmaple.com` generates a fresh upstream query every single time. Under
a typo-squatting scan or a fat-finger incident, that is a self-inflicted denial of
service against your own authoritative servers. The negative TTL is derived from the SOA:
`min(SOA.ttl, SOA.minimum)`.

## 6. NXDOMAIN vs NODATA

These are different answers and conflating them is a genuine bug class:

- **NXDOMAIN**: the name does not exist in the zone at all.
- **NODATA** (NOERROR with zero answers): the name exists, but there is no record of the
  requested type.

Returning NOERROR-with-no-answer for a nonexistent name causes some clients to treat the
domain as valid-but-empty and attempt a subdomain of it, which is both a correctness
problem and a small information leak.

## 7. Load balancing at the DNS layer

DNS-level balancing returns multiple addresses and relies on the client's resolver to
choose, usually round-robin. It has real limits:

- **Per-connection, not per-request.** For a platform with long-lived connections —
  WebSockets, gRPC, database pools — one client can pin a node for the whole session.
  Traffic distribution stops being even, and one node can carry far more load.
- **No health awareness.** A dead address stays in the answer until its TTL expires, and
  clients cache the failure locally too.
- **Not sticky, and not policy-aware.** You cannot express "EU users to EU" from a
  round-robin record set, and you cannot shift a percentage of traffic by changing a record.

DNS balancing is fine for stateless HTTP with short connections. For anything else, the
real balancing belongs in a layer that can see connection state.

## 8. Health checking, done properly

A health check that is badly designed causes outages:

- **Synchronised checks** create a thundering herd when a node recovers and every client
  reconnects simultaneously. Fix: jitter every check interval.
- **Single-failure ejection** flaps a node under brief load spikes. Fix: require N
  consecutive failures before ejecting.
- **A check that lies** — a `/health` returning 200 while the service cannot reach its
  database — creates false confidence. Fix: make the check exercise a real dependency.
- **Instant re-admission** sends full traffic to a node that has just restarted and is not
  ready. Fix: a ramp-up period, admitting recovered nodes at a fraction of traffic.

## 9. Failover propagation

A failover is not instantaneous. It is the maximum across every cache of (remaining TTL),
plus the authoritative server's own zone refresh interval. Practical consequences:

- A 30s TTL on the failover hostname is the floor; a 300s TTL means a 5-minute objective
  is met only just, with no margin.
- Some resolvers ignore TTLs entirely or cache negatively for longer than requested.
- The answer for a name with multiple A records is often returned as a set, so a client
  may still use a dead address it cached, and will only fail over on its own retry logic.

This is why the right answer for a real failover requirement is usually: short TTLs on a
dedicated failover hostname, combined with an application-level balancer that performs its
own health-aware selection.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 1035 defines the DNS namespace, the delegation hierarchy, and the caching model
  that makes stale answers possible at every hop.
  https://www.rfc-editor.org/info/rfc1035/
- RFC 2308 specifies negative caching and the derivation of the negative TTL from the SOA
  minimum field, which the caching resolver implements.
  https://www.rfc-editor.org/info/rfc2308/
- RFC 2782 defines the use of SRV weight for proportional selection, the mechanism behind
  weighted DNS balancing.
  https://www.rfc-editor.org/info/rfc2782/
