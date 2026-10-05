# VISION — Zero Trust Architecture: Never Trust, Always Verify
> Where this lab takes you: from "put it behind the VPN" to designing a system where location implies nothing.

## The Arc
1. **Why** — the perimeter dissolved: cloud, remote work, SaaS, and lateral movement.
2. **Principles** — no implicit trust based on network position; explicit per-request policy.
3. **Identity** — workload identity, service mesh identity, SPIFFE/SPIRE, and short-lived certs.
4. **Micro-segmentation** — per-service policy, default deny, and lateral movement containment.
5. **Continuous evaluation** — device posture, session risk, and dynamic access decisions.

## Milestones (checkable)
- [ ] M1: draw the trust boundaries in an estate that has none, and label each one.
- [ ] M2: replace a network-trust assumption with an identity-and-policy decision.
- [ ] M3: implement default-deny network policy and prove lateral movement is blocked.
- [ ] M4: issue short-lived workload certificates and eliminate long-lived service credentials.
- [ ] M5: describe how a compromised service's blast radius is bounded to one dependency.

## Core Competencies
- Translating "inside the network" into "presents a valid identity with sufficient posture".
- Policy decision and enforcement separation, and where that boundary sits operationally.
- Workload identity issuance, rotation, and revocation (SPIFFE/SPIRE-style).
- Trust zones, tiering, and micro-segmentation granularity trade-offs.

## Anti-Goals
- "Zero trust" as a synonym for "we bought a product".
- Identity established at connection time and then trusted for hours.
- Segmentation policies written as a flat allow-everything-then-exceptions list.

## Interview Lens
- "Your service can reach the database. What stops lateral movement if the service is compromised?"
- "How do you authorize every request without a performance disaster?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: map trust boundaries in a sample estate.
- Wk2 QUIZ/FLASHCARDS to 90%+; implement default-deny policies.
- Wk3 MINI_PROJECT: mTLS + policy enforcement between three services.
- Wk4 REAL_WORLD_PROJECT: staged zero-trust migration with posture and telemetry.

## Done = You Can
- Produce a zero-trust target architecture for a real estate, sequence the migration
  so nothing breaks, and quantify the blast radius change for a given compromise.
