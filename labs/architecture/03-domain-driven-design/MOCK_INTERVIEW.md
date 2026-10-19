# Mock Interview: Bounded Contexts on a Ferry Network

> Simulated transcript. BlueHarbor runs passenger ferries; panellist Priya, a principal engineer, drives the session.

---

## Framing

"BlueHarbor sells trips — a customer reserves a seat on a departure — operates vessels with rosters and maintenance windows, and invoices harbour authorities for berth usage. One model currently serves all three, and the word 'reservation' means a passenger seat to sales but a berth slot to operations. Releases fail integration tests weekly for reasons nobody can state."

---

## Deep Dive

**Priya**: "Where does the concrete pain show up?"

**Me**: "In reviews. Operations engineers bolt berthing fields onto the trip class; sales then breaks arrival-time logic. One class no longer communicates a purpose. The fix is three contexts — Trip Sales, Sailing Operations, Port Billing — each defining 'reservation' its own way, each owning a separate store."

**Priya**: "A reservation still touches a vessel. Isn't one aggregate easier?"

**Me**: "No. The reservation aggregate records departure id, seat count, and passenger names; its job is bookkeeping, not capacity truth. Seats live on the departure's ledger in Sailing Operations, where every decrement lands anyway. A reservation is granted by calling that context's small command API, so overselling is structurally impossible no matter how badly Trip Sales is written."

**Priya**: "There's a decades-old mainframe still rewriting the booking ledger nightly. How do your models survive it?"

**Me**: "Behind an anticorruption layer. Fixed-width mainframe dumps arrive; a translator converts them into our own snapshot type with real invariants. Legacy vocabulary never enters the new model, and when the mainframe retires, only the translator changes."

**Priya**: "What language do the teams share?"

**Me**: "Each context keeps a glossary drawn from its own department's words. Where the crew says 'manifest', sales says 'confirmations list'. Forcing a single term across contexts is exactly how the giant shared model grew in the first place."

**Priya**: "Could sales and billing share one money type?"

**Me**: "Each copies the small value types it needs. A shared kernel reads as convenience and behaves as coupling — one side dictates the shape, the other freezes its roadmap."

**Priya**: "Last one: how do you keep the three from quietly re-growing into one?"

**Me**: "Contract tests between contexts, reviewed like surface changes, plus a standing rule that nobody merges a shared type without both owners named in the pull request. Drift gets arrested weekly, not rediscovered yearly."

**Priya**: "And how does Port Billing learn that a trip happened?"

**Me**: "Trip Sales publishes ReservationConfirmed; billing subscribes and prices by berth class. No direct table reads between contexts. If billing is dark, bookings still sell — the event waits in a queue. That asymmetry is why we picked events over a synchronous call here."

---

## Corner Cases the Panel Will Push

- "Draw where each invariant sits." Oversell protection belongs to the departure ledger; refund ceilings belong to Port Billing; cancellations inside the sales window belong to Trip Sales. Boundaries fail when invariants migrate silently.
- "Two contexts need the same word." Let them disagree, deliberately — one word, two definitions, documented per context. A shared term with two meanings is cheaper than a shared model with two owners.
- "Whose fact is boarding?" — Sailing Operations publishes BoardingStarted; sales keeps it as read-only reference. Facts flow one way across context edges, and ownership never flips midstream.
- "Delivery deadlines — who validates them?" — Operations owns schedule truth; sales stores only what it promised the customer. When they disagree, operations wins the fact and sales manages the expectation.

---

## Trap to Avoid

Answering "document the term properly and move on". A bounded context is enforced by separated ownership — teams, deployments, databases. A glossary without ownership changes nothing.
