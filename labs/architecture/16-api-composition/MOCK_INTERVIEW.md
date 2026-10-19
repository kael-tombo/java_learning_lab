# Mock Interview: Composing the Order-Tracker Screen

> Answers drafted against a screen spec. GreenCart, a grocery delivery service: the tracking page shows a profile chip, order details, and a live arrival estimate. Under the hood sit profile, orders, and dispatch services.

---

## Spec Questions

1. "One endpoint returns all of it. Design the fan-out."
   A composition tier calls profiles, orders, and dispatch concurrently, each child owning a slice of an overall render budget of a few hundred milliseconds. Late children miss the page rather than delay it; the tier aggregates whatever arrived in time.

2. "Dispatch is down. Render what?"
   Partial success, graded by criticality. Profile and order details render normally while the arrival widget degrades to "calculating…". A decorative child failing never fails a whole page — but if orders, the anchor of the screen, fails, the entire response is an error. Partial answers are for decorations, never for the spine.

3. "The estimate needs the shipment id, which only the orders answer contains. Sequential join?"
   That chain is inherent: orders first, dispatch second with the id in hand. The screen can prefetch during page load to shave the first hop, but the business dependency itself is real and the two-step latency should be presented as such rather than hidden.

4. "Composition results cached?"
   The composite gets a handful of seconds keyed by user and order-status bucket, with an eviction on each status change so staleness stays honest. Static children — profile chip — cache far longer and separately. Coarse shared caching would make one user's refresh pay for another user's staleness.

5. "Why not have the phone compose?"
   A phone making five sequential calls burns battery and lets the slowest child govern page load — the tail is then the customer's problem. Composing at the edge pulls that tail in-house, where parallelism, proximity to services, and caching actually work.

6. "Rush hour — does composition collapse?"
   Duplicate in-flight requests for the same cart collapse into one; per-child concurrency caps stop a synchronized storefront demand from becoming a coordinated flood. The compositor's job is absorbing pace mismatch, not relaying it.

---

## Probes

- "Error shapes differ across the three children — who normalizes them?" the compositor, once, into a stable problem taxonomy the client has always known; translating per child is duplication the tier exists to delete.
- "Who owns the compositor?" — the client-facing team, since the render budget is theirs; service teams veto budgets they genuinely cannot meet, which forces the negotiation before code instead of after.
- "Schema drift across children?" — the compositor declares minimum fields per child; new fields arrive freely, while a removal waits until every consumer's view model has stopped reading it.
- "Retry policy at the compositor?" — reads only, capped per child, with spacing between attempts; never a retry that could fire a write twice — the write path owns its own idempotence.
- "Observability?" — per-child latency, errors, and counts exported under one span tree, so the slow child of a slow page surfaces by name instead of by folklore.
- "Authentication for the composite call?" — the edge verifies the user once and forwards their context; children trust the compositor and never the open internet directly.

---

## Closing Reply

**Interviewer**: "One sentence on why composition lives here and not in the app?"

**Candidate**: "Because the page is the customer's product — deciding what is essential and what may degrade is a product judgement, and it deserves an owner beside the services rather than inside every client."

---

## Red Flag

Failing the entire page whenever any child errors. Treating a profile chip and the order record as equally essential reveals no product sense about what the screen exists to do.
