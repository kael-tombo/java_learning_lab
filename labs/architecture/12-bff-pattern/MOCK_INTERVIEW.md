# Mock Interview: One Backend per Client, Not per Server

> Dialogue, three-way panel. TrailMate is a hiking product with a phone app (offline-tolerant), a web dashboard, and a support console sharing one general API. The phone pulls megabytes to render a list.

---

## Warm-Up

**Panel**: "Sell the idea in a sentence."

**Candidate**: "Each client type gets a small backend owned by the squad shipping that client, shaped exactly to its screens, with domain services untouched underneath. The contract belongs to the consumer, not to a committee."

**Panel**: "Who owns each of these backends?"

**Candidate**: "The client team, end to end. When the mobile squad reshapes a screen they change their backend in the same release. Nobody negotiates a generic data contract across three teams to ship one button."

**Panel**: "Doesn't the same logic get written three times?"

**Candidate**: "Duplication of shape — naming, trimming, ordering — is fine and intended. Duplication of rules is not: an age gate or a surcharge computed in two backends is a defect waiting to disagree with itself. These layers compose from domain services and reshape; they do not re-decide."

**Panel**: "Walk me through fixing the phone's payload pain."

**Candidate**: "The mobile backend trims responses to fields the screens actually render, collapses five round trips into one composite call, and can adopt a leaner wire format than the web one uses. Nothing behind it changes — the same services keep answering."

**Panel**: "A downstream service times out mid-request. What does the client see?"

**Candidate**: "Nothing about our internals. The backend holding the client's contract converts the timeout into a per-field degraded signal plus a retry hint — never a stack trace, never a service name. Error shaping is its job, which is why clients can trust the surface."

**Panel**: "Three clients is small. Is a plain gateway enough?"

**Candidate**: "If all screens agree on payload shape and one squad serves everyone, yes — one gateway, one API, no extra tax. The pattern answers divergence, not fashion. It pays when client teams drift apart in release rhythm and needs."

**Panel**: "Trail alerts have to arrive in real time. Where?"

**Candidate**: "Over a persistent socket held by whichever backend needs it — the phone backend translates push events into screen-shaped messages on the spot, while the web side may not need that stream at all."

---

## Closing Probes

- "Rate limiting: per backend or global?" — coarse quotas at the shared edge, fine caps per backend type, because a runaway console script must not exhaust the phone allowance.
- "Where do sockets terminate?" — in each client's own backend only; domain services stay request-scoped, and push translation is presentation work, so no shared service ever holds a live connection.
- "Who arbitrates an interface change on the domain services?" — the domain team owns the shape; every backend adapts on its own cadence, which is precisely the decoupling being purchased here.
- "What if the web team lobbies to absorb the phone backend?" — decline unless they can staff it: each backend exists because its makers feel its consequences, and centralizing it rebuilds the shared API we just dismantled.
- "Metrics split along which seam?" — every backend owns the service objectives of its own client surface; domain services own theirs, and dashboards express that boundary as ownership rather than plumbing.
- "Who reviews a proposal to merge two of them?" — whoever can argue the convergence test: identical screens, one team, one release rhythm. Without that evidence the merge is consolidation theatre.
- "What stops rules drifting into these backends?" — review discipline: anything that prices, gates, or refuses belongs to a domain service; showing up in a backend's code gets it bounced to the service that owns the rule before merge.
- "Where does testing sit?" — each backend runs against stubbed domain services, plus one thin smoke per client type; the shared services keep their own contract suites untouched.

## Red Flag

Treating these per-client layers as a convenient dump for rules "just temporarily". Every rule parked there becomes a second implementation to keep in sync with the domain — and it never moves back.
