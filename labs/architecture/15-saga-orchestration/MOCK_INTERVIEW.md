# Mock Interview: The Orchestrated Travel Package

> Transcript. Wayfare sells holiday bundles — a flight, a hotel, a rental car booked as one purchase. Tangled `catch` blocks are today's failure plan; the panel wants that made coherent.

---

## Warm-Up

**Panellist**: "Draw the flow you would ship."

**Candidate**: "Two parallel holds — flight and car — then hotel confirmation, then one payment capture. Any step failing triggers a compensation list executed in strict reverse. Each leg commits locally; the coordinator only sequences what happens next and what unravels when a leg refuses."

**Panellist**: "Where does the flow's progress live?"

**Candidate**: "In the coordinator's own store: a saga row per booking holding step status, timestamps, and the pending-compensation list. After a restart the row is reloaded and the incomplete leg is re-issued. That row is the single truth about progress; nothing depends on process memory."

**Panellist**: "The hotel stops answering mid-leg."

**Candidate**: "Every command gets a deadline timer. When one expires the leg is marked ambiguous, settled legs get compensated, and the customer is told plainly. Ambiguity is accepted on purpose — releasing a held room beats holding somebody's card open forever."

**Panellist**: "What lives inside the coordinator?"

**Candidate**: "Sequence and compensation, deliberately thin. Prices, refund percentages, and eligibility stay in the services it calls. A coordinator dumb enough to survive rule churn is a coordinator that survives the next quarter at all."

**Panellist**: "Why not let the services react to each other's events — the choreographed style?"

**Candidate**: "Four steps with a parallel branch and join, plus compensation interplay. Event wiring would scatter the flow across handlers and make nobody able to read it whole. With one coordinator, the journey is a single artifact a new engineer reads in an afternoon instead of inferring it from six repositories."

**Panellist**: "A coordinator restart replays a command. Consequences?"

**Candidate**: "None, if commands carry the saga id and step number, and receivers keep a ledger keyed by that pair. A replayed command returns the recorded outcome instead of charging twice. Idempotency is purchased at the receiver, once, as design — not hoped for at runtime."

**Panellist**: "Sounds easy to overgrow. What restrains it?"

**Candidate**: "A review rule: any debate about business policy inside the coordinator is lost by the coordinator — the rule moves to the owning service. Its code is reviewed for sequencing correctness and nothing else."

**Panellist**: "How do you see a stuck one at three in the morning?"

**Candidate**: "One metric: age of unfinished sagas by step. Alert when it passes the maximum legal hold window, since holding a room longer is a bill somebody pays. Step-level aging turns 'the system feels slow' into 'step three of run 8821 is stuck', which is an actionable page."

---

## Probes

- "Compensation itself fails — payment already captured but the flight leg releases nothing." Escalate to a dead-letter queue plus a reconciliation task that retries in bounded intervals; finance owns the escalation after the automatic window closes.
- "Does the coordinator ever sit on the request path?" It starts sagas and reports status, so a customer sees 'held' immediately; nothing user-facing waits on a full bundle completion.
- "Does compensation order ever vary per leg?" — the saga row declares its compensation list per step, and the coordinator follows what the row declares, never a guessed sequence.
- "Testing the coordinator itself?" — recorded leg failures — timeout, decline, duplicate delivery — replayed against fakes, with the coordinator the only real component, asserting compensation lists fire in declared order.
- "An audit request for one booking?" — export the saga row plus every leg event attached to its id; the transitions reconstruct the purchase for a third party without narration from anyone.

---

## Red Flag

A "coordinator" that sits in a synchronous chain, waiting inline on every call. That is a distributed monolith in saga clothing — a real orchestrator persists state and survives losing its own process.
