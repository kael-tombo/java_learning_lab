# DNS & Load Balancing - README

## Overview
This lab drills into how names become addresses and how traffic gets distributed once it
has one. DNS is the layer teams change in a hurry and understand least: a TTL is chosen by
guesswork, a round-robin record is mistaken for a load balancer, and both become an
availability incident during a failover.

## Learning Objectives
- Trace a complete resolution from stub resolver to authoritative server, naming every cache
- Explain recursive vs iterative resolution and where each hop can hold a stale answer
- Use A, AAAA, CNAME, SRV, and TXT records and know what each one breaks
- Implement negative caching per RFC 2308 and show why it matters under load
- Implement round robin, weighted, and least-connections balancing algorithms
- Build a health checker that avoids flapping and thundering-herd recovery

## Prerequisites
- Java 21+
- Basic TCP/IP knowledge
- Familiarity with command-line DNS tooling (`dig`, `nslookup`)

## Lab Structure

| Directory/File | Description |
|----------------|-------------|
| `src/main/java/` | DNS server, caching resolver, balancers, health checker |
| `src/test/java/` | JUnit 5 tests including cache and balancing correctness |
| `MINI_PROJECT/` | Minimal authoritative server + caching resolver + balancers |
| `REAL_WORLD_PROJECT/` | Multi-region DNS policy and traffic management |
| `SOLUTION/` | Solutions to exercises |

## Quick Start

```java
// Query a name through every hop and print the TTLs that come back.
var response = new SimpleResolver("127.0.0.1", 5300).resolve("api.example.com", Type.A);
System.out.println("rcode=" + response.rcode() + " ttl=" + ttlOfFirstAnswer(response));
```

```bash
# Observe the cache in action
dig +noall +answer api.example.com
dig +noall +answer api.example.com     # second query is served from cache
```

## Topics Covered
1. Recursive vs iterative resolution and the delegation chain
2. Record types: A, AAAA, CNAME, SRV, TXT, SOA, and their lookup differences
3. TTL semantics, cache layering, and negative caching (RFC 2308)
4. NXDOMAIN vs NODATA, and why conflating them is a bug
5. Balancing algorithms: round robin, smooth weighted, least connections
6. Health checking: thresholds, jitter, ramp-up, and deep probes
7. Failover propagation, and the caches you cannot control

## Assessment
- Complete the coding exercises in `EXERCISES.md`
- Pass the quiz in `QUIZ.md`
- Submit the mini project
- Complete the real-world project

## Estimated Time
4-5 hours

## References
- RFC 1035 - Domain Names: Implementation and Specification
- RFC 2181 - Clarifications to the DNS Specification
- RFC 2308 - Negative Caching of DNS Queries
- RFC 2782 - Weighted Ranking for DNS SRV
