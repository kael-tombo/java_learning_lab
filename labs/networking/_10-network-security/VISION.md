# VISION — Network Security: TLS, Segmentation, and the Network as Attack Surface
> Where this lab takes you: from "we use HTTPS" to configuring a handshake, segmenting a network, and reasoning about the packets.

## The Arc
1. **TLS** — handshake mechanics, version negotiation, cipher selection, and session resumption.
2. **Certificates** — chains, validation, pinning, rotation, and the failure modes of each.
3. **mTLS** — service identity, workload certificates, and the operational burden of rotation.
4. **Network defence** — firewalls, segmentation, IDS/IPS, and what the network cannot do.
5. **Layered posture** — how network controls combine with application controls, and where they overlap.

## Milestones (checkable)
- [ ] M1: perform a TLS 1.3 handshake and explain every message.
- [ ] M2: build a certificate chain and validate it, then find a deliberately broken one.
- [ ] M3: configure mTLS and show a request failing on a client certificate mismatch.
- [ ] M4: write a segmentation policy with a default-deny posture and test lateral movement.
- [ ] M5: state precisely what TLS protects and what it does not.

## Core Competencies
- TLS 1.3 handshake, cipher suites, forward secrecy, and 0-RTT trade-offs.
- Certificate validation, chain building, expiry management, and rotation without downtime.
- Network segmentation as a containment control, with default deny.
- IDS/IPS placement, false-positive management, and what network visibility cannot see.

## Anti-Goals
- "Encryption" asserted without knowing which protocol version and which cipher suite.
- Certificate expiry discovered by an outage rather than by monitoring.
- Segmentation written as a flat allowlist that permits the entire internal network.

## Interview Lens
- "Your certificate expires in 12 hours and the CA is down. What now?"
- "What does TLS not protect you from?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: handshake capture, chain building, validation failures.
- Wk2 QUIZ/FLASHCARDS to 90%+; segmentation design and testing.
- Wk3 MINI_PROJECT: mTLS service plus a segmentation policy.
- Wk4 REAL_WORLD_PROJECT: a service mesh with automated certificate lifecycle.

## Done = You Can
- Design and operate encrypted service-to-service communication with an automated
  certificate lifecycle, and prove lateral movement is contained.
