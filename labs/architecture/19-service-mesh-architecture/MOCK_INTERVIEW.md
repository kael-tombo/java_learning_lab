# Mock Interview: Making the Mesh Case to a Reluctant Estate

> Dialogue. Halcyon runs about 120 services across five languages. Security wants service-to-service encryption and workload identity; meanwhile every team hand-rolls its own retry logic, badly.

---

## Round One

**Chair**: "Plead for a mesh over libraries."

**Candidate**: "One enforcement point for identity, in-flight encryption, call policy, and uniform telemetry — versus five client libraries drifting apart in five languages. Libraries scale their maintenance linearly with languages; a mesh scales once."

**Chair**: "What does mutual TLS actually deliver here?"

**Candidate**: "Every workload receives a cryptographic identity issued by the control plane and rotated automatically. Calls verify both ends before any bytes move. Authorization then attaches to identity — who is calling — rather than to network position, which stops 'internal' meaning 'unauthenticated' the moment a pod moves."

**Chair**: "And the extra leg through a proxy — what does that bill come to?"

**Candidate**: "Each call now crosses two proxies — a real, fixed increment per call. I will not hand-wave it: profile one busy path in a canary with the proxy attached and with it removed, watch the tail and CPU. A latency-critical path that regresses gets deliberately exempted, with the reason recorded — silence on this question is how mesh rollouts die."

**Chair**: "Convince me the mesh improves release mechanics, not just security."

**Candidate**: "Percentage routing lives in the mesh configuration: two percent of order traffic to the new revision, header pinning for staff. Teams stop building rollout plumbing inside applications, and a bad revision sheds traffic in seconds from one policy file."

**Chair**: "Where does the mesh's reach end?"

**Candidate**: "At side effects. A proxy retries the request it observed; only the application knows whether attempt one had consequences — captured a card, booked a seat. Payment semantics stay in code. The mesh also sees request traffic, not business events, so product analytics live where they always did."

**Chair**: "Rollout order for a nervous estate?"

**Candidate**: "Telemetry first — every call's fate reported with zero code churn, which buys trust cheaply. Then encryption in observe mode, then enforced, then routing policy, with authorization last. Each stage earns belief before the next stage can damage anything."

**Chair**: "When should a shop skip this entirely?"

**Candidate**: "A handful of services, one language, one team: a tuned shared client plus a solid edge gateway beats a proxy per pod. The mesh is a response to heterogeneity and headcount, and adopting it for the compliance checkbox alone is the fastest way to inherit a useless data plane."

---

## Probes

- "Egress to third parties through the mesh?" — wrapped as named destinations with the same identity and policy treatment, otherwise partners become the unmanaged hole the whole design exists to close.
- "Business-level authorization — where?" — in the application, where domain context lives; the mesh answers "may this workload call that one" and nothing finer.
- "Proxy faults versus app faults — how kept apart?" — mesh-emitted response classes separate transport failures from application errors in the dashboards, and pages filter on that boundary first.
- "What does the mesh see that app metrics cannot?" — connection truths: TLS outcomes, retries the proxy added, error classes per destination — the difference between "my code" and "the wire".
- "Who owns mesh incidents?" — the platform team owns the data plane and its changes; teams own their SLOs. The proxy's fate must be visible in every service's dashboard, or outages get misattributed to app regressions.

---

## Closing Exchange

**Chair**: "One sentence for the budget holder?"

**Candidate**: "The mesh converts security and rollout policy from sixty repositories into one maintained plane — cheaper to audit, and far cheaper to evolve."

---

## Red Flag

Adopting the mesh without re-measuring the per-hop cost on real traffic. The first latency incident lands on the mesh, and the platform team loses the argument for good.
