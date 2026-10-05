# Network Security Deep - README

## Overview
This lab goes deep on network security as an engineering discipline rather than a device
purchase. It covers threat modelling, TLS internals and certificate lifecycle at fleet
scale, micro-segmentation as a measurable reduction in reachable paths, and — critically
— the continuous verification that proves those controls actually work. Controls that have
never been attacked are controls of unknown effect.

## Learning Objectives
- Build a threat model per service with explicit trust boundaries and out-of-scope items
- Trace a TLS 1.3 handshake, including the key schedule and session resumption
- Operate a certificate lifecycle with automated rotation and zero expiry incidents
- Express segmentation as a graph and quantify reachable service pairs before and after
- Design continuous verification: probing your own controls continuously
- Distinguish what each layer of defence can and cannot see
- Map controls to a compliance framework while reporting real coverage honestly

## Prerequisites
- Java 21+
- Completed labs 02 (TCP/UDP), _10 (network security), 14 (container security), 16 (zero trust)
- Comfortable reading packet-level and certificate structures

## Lab Structure

| Directory/File | Description |
|----------------|-------------|
| `src/main/java/` | Threat models, CA, segmentation compiler, verification suite |
| `src/test/java/` | Control verification including lateral-movement probes |
| `MINI_PROJECT/` | Aegis: mTLS service, certificate lifecycle, measured segmentation |
| `REAL_WORLD_PROJECT/` | Bastion: platform-wide segmentation with continuous assurance |
| `SOLUTION/` | Solutions to exercises |

## Quick Start

```java
// The most valuable test in the project: what can a fully compromised service reach?
var probe = lateralMovementProbe.from("orders-svc")
        .withFullyCompromisedCredentials()
        .attemptAllKnownTargets();
assertThat(probe.succeeded()).containsExactlyInAnyOrder("payments-svc:8443", "payments-db:5432");
```

## Topics Covered
1. Threat modelling: boundaries, assets, threats, and an explicit out-of-scope list
2. TLS 1.3: handshake messages, key schedule, resumption, 0-RTT
3. Certificate lifecycle: issuance, rotation overlap, revocation, fleet scale
4. Mutual TLS: service identity, SAN-based authorisation, ephemeral keys
5. Segmentation: default deny, tiers, exception governance, drift detection
6. Blast-radius mathematics: reachable pairs, graph connectivity, containment
7. Continuous verification: lateral-movement probes, policy diffing, red team
8. Network defence limits: what is invisible at the network layer
9. Assurance: evidence for audits, and honest coverage reporting

## Assessment
- Complete the coding exercises in `EXERCISES.md`
- Pass the quiz in `QUIZ.md`
- Submit the mini project
- Complete the real-world project

## Estimated Time
6-7 hours

## References
- NIST SP 800-207 - Zero Trust Architecture
- RFC 8446 - TLS 1.3
- RFC 9001 - Using TLS to Secure QUIC
- OWASP Transport Layer Security Cheat Sheet
- Kubernetes Network Policies documentation
