# Mock Interview: Choreographed Checkout Under Failure

> Numbered probes, terse answers. CrateDrop, a subscription-box retailer, runs its order lifecycle across three services with no central coordinator.

---

## Setup

Placing an order fans out through the warehouse, the payment gateway, and a courier partner. Choreography was chosen because the flow is a straight line; the debate is whether it survives contact with failure.

---

## Probe List

1. "Name the chain."
   OrderCreated → BoxAllocated → PaymentCaptured → PickupScheduled. Each service commits locally, then publishes its outcome for the next subscriber. The flow lives inside the subscribers — that is both its flexibility and its biggest debugging liability.

2. "Payment declines after the box was allocated. Undo it."
   The warehouse listens for PaymentDeclined and releases the reservation. Compensation runs in the reverse order of completed steps, and every compensator must survive replay — releasing an allocation twice must be harmless, so the release is keyed by order id.

3. "What if that decline message is lost?"
   Silence is treated as failure, never success. Each order that enters "awaiting payment" carries a deadline; when the timer fires with no event seen, the order is marked stalled and compensation is triggered automatically. No endpoint waits forever on an absence.

4. "Events show up misordered — capture before allocation."
   The courier step refuses to fire on a single prerequisite. Each subscriber keeps a local per-order state row ticking off received prerequisites, and the action triggers only when the row says every predecessor is done. It is a local join, cheap and honest.

5. "Where is the audit trail?"
   Every transition lands in an `order_lifecycle` row keyed by order id — step, status, timestamps. Support asks where order 4421 stands and one query answers. Without that table, choreography is operable in theory only.

6. "Why choreography rather than an orchestrator here?"
   Three steps, one straight line, no branches. An orchestrator earns its keep when the graph branches, joins, or holds mid-flow state; those are absent, so a coordinator would be one more moving part buying nothing.

7. "Where does the design show its age first?"
   When a second box type arrives with different allocation rules. A choreographed flow that starts branching deserves rewriting into an orchestration — write down today what would trigger that rewrite, so the call is made by evidence rather than by exhaustion.

---

## What the Panel Pushes Next

- "Compensation later becomes impossible — stock already sold out." Retry the release in a bounded queue; if it stays impossible, a dead-letter row flags the order for a human refund decision. Finance must accept that goods and money reconcile asynchronously.
- "What exercises the failure paths?" — event fixtures that replay decline, timeout, and dupes against real subscribers in CI, asserting the compensators fire in the right order.
- "Who watches the chain end to end?" — the lifecycle table plus per-step lag metrics; choreography's bill is building that visibility early, because the coupling hides inside consumers.
- "How long may the customer see 'pending'?" — the payment deadline answers it: once the window passes, the order plainly reports failure and releases the goods, with no support involvement.

---

## Candidate Red Flag

Answering the out-of-order question with "add a distributed lock". Correct design makes each subscriber demand a known order per key; leasing shared state across services papers over the real problem.
