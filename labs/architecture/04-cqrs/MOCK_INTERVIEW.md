# Mock Interview: Splitting Reads from Writes

> Two chairs, one candidate. Halcyon Air runs a fare search page and a booking flow that disagree badly about shape.

---

## Round One

**Chair**: "Ninety seconds on CQRS."

**Candidate**: "The command side owns every rule for changing state; the query side serves reads from a shape built for the screen. Two models — one stores intent, one answers lookup. The split pays off exactly where reads and writes disagree in volume and shape, and airline seat search is the textbook case: thousands of filter combinations per actual booking."

**Chair**: "Where would you refuse to use it?"

**Candidate**: "Profile pages and admin screens. A form saving one row gains nothing from a second model, and the price is doubled code plus an eventual-consistency explanation nobody wants to give. It belongs where a query cannot be answered cheaply by the write store — full-text search, geo filtering, cross-entity rollups."

**Chair**: "Bookings change seat availability; the search page must see it. Describe the pipe."

**Candidate**: "The booking side emits BookingPlaced; a projector folds it into a denormalized search document — route, date band, seats left, price band. The index is disposable: delete it, replay the command events, and you get the same document back. That rebuildability is the strongest structural argument for the whole pattern."

**Chair**: "I paid for seat 4A and the search page still shows it free."

**Candidate**: "Lag — the projector hadn't caught up. Two mitigations. The confirmation page always reads the authoritative store and never lies. And lists carry a revision marker so a client can tell that its data is older than the decision it is making; when in doubt the screen says 'check availability' instead of selling the same seat twice."

**Chair**: "Who owns the projector?"

**Candidate**: "Whoever consumes the screen. Their contract is the event schema; beyond it, they may reshape documents at will, because any shape is reconstructable from the same stream later."

**Chair**: "Does the query side ever write?"

**Candidate**: "Its own plumbing only — refresh cursors and revision stamps. Business state change belongs to command handlers; the day a query mutates an order, the boundary exists in a diagram and nowhere else."

**Chair**: "Two commands racing on the same aggregate?"

**Candidate**: "Uniqueness and version rules stay with the write store as always. The split changes the read story, not the write discipline; concurrency conflicts remain write-side problems with write-side answers."

---

## Second-Round Probes

- "Commands look like service methods. Why the ceremony?" — one command, one handler keeps a single home for preconditions; validation, authorization and the audit note sit beside the stated intent rather than scattering across three controllers.
- "Cheap first step for a group that wants 'some of this'?" — pull query endpoints out of the command service's process while keeping one store; promote a second model only when a real query proves it needs one.
- "What does projector backlog cost, and who pays it?" — the read side, visibly: lag minutes on its own dashboard, and any screen needing fresher answers reads the authoritative store for that field.
- "State an acceptance criterion for lag." — listings may trail by seconds, but no answer that charges a customer may come from a view; a price or seat decision always consults the source of truth.
- "Who else reads the events besides the projector?" — the audit trail, then later teams with new screens. The command side publishes once and everyone subscribes — direct table peeks across stores are never the currency.
- "During a projector deploy?" — the existing projection keeps serving until its replacement passes the diff, so a deploy is a swap of pointers rather than a rebuild in place.
- "How do you reproject safely?" — build a shadow instance, diff a sampled set of new documents against the existing ones, and let readers switch only after the diff is clean. No downtime, and the diff tells you which rules drifted.

---

## Red Flag

Any candidate who claims CQRS "buys consistency". The command store is consistent; the sold-out seat may still appear on lists for seconds. Promising otherwise means the split — and its failure modes — have been misunderstood.
