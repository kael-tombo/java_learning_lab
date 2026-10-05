# VISION — Network Security Deep: Cryptography, Segmentation, and Evidence
> Where this lab takes you: from "we have a firewall" to designing controls whose effectiveness you can measure.

## The Arc
1. **Threat model first** — what is being protected, from whom, and what is explicitly out of scope.
2. **Transport security** — TLS internals, certificate lifecycle, and mTLS at scale.
3. **Segmentation** — micro-segmentation, default deny, and the mathematics of blast radius.
4. **Network defence** — IDS/IPS placement, DNS security, and the limits of network visibility.
5. **Evidence & assurance** — proving a control works, penetration testing, and compliance mapping.

## Milestones (checkable)
- [ ] M1: write a threat model for a service and name its trust boundaries explicitly.
- [ ] M2: perform a TLS 1.3 handshake and explain every message and key derivation.
- [ ] M3: build a certificate lifecycle with automated renewal and zero expiry incidents.
- [ ] M4: quantify blast radius before and after segmentation with a lateral-movement test.
- [ ] M5: state what a network control cannot see, and where the compensating control is.

## Core Competencies
- Threat modelling as a design input rather than a documentation exercise.
- TLS 1.3 handshake, key schedule, and the operational realities of certificate management.
- Segmentation mathematics: reachable pairs before and after a policy.
- Control effectiveness measurement, and honest reporting of coverage gaps.

## Anti-Goals
- Security controls with no stated threat they address.
- A segmentation policy that is technically default-deny but functionally a flat network.
- Compliance mapping treated as evidence that a control works.

## Interview Lens
- "How do you know your segmentation works?" "What is your blast radius today?"
- "TLS is on. What is your biggest network risk?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: threat model, handshake analysis, segmentation maths.
- Wk2 QUIZ/FLASHCARDS to 90%+; measure control effectiveness.
- Wk3 MINI_PROJECT: mTLS service with a real certificate lifecycle.
- Wk4 REAL_WORLD_PROJECT: platform-wide segmentation and assurance programme.

## Done = You Can
- Design layered network controls, prove they work by attacking them, and report their
  effectiveness and gaps to a reviewer who will check.
