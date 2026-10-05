# VISION — Ecommerce Platform Capstone

> Build the system behind a mid-size online retailer: catalog, cart, checkout,
> orders, fulfilment, and the data pipeline that explains all of it.

## Why this capstone

Every other lab teaches a component. This one makes you own the seams: the
order that succeeds in the service and fails in the warehouse, the inventory
that oversells because two requests raced, the refund that a ledger cannot
explain. The engineering here is mostly in the boundaries.

## The Arc

1. **Domain** — catalogue, pricing, inventory, orders, payments, fulfilment.
2. **Consistency** — where strong consistency is required and where it is not.
3. **Boundaries** — sync vs async, and what happens when a call times out.
4. **Money** — an append-only ledger, and why totals are derived not stored.
5. **Explain** — the pipeline that makes the business legible.

## Milestones (checkable)
- [ ] M1: model the order lifecycle as an explicit state machine with legal transitions only.
- [ ] M2: prevent overselling with a reservation model, and prove it under concurrency.
- [ ] M3: implement an idempotent checkout with a payment idempotency key.
- [ ] M4: build a double-entry ledger and reconcile it against the payment provider daily.
- [ ] M5: produce a per-order timeline joining application logs, events, and warehouse rows.

## Anti-Goals
- Distributed transactions across the order and payment services.
- A mutable `order.total` field that nothing can explain.
- Caching a price without a stated invalidation rule.

## Interview Lens
- "A customer was charged twice. Walk me through your design."
- "How do you know your inventory number is right?"
- "Where does the order state live, and who is allowed to move it?"

## 30-Day Plan
- Wk1 domain model + state machine + concurrency test for reservations.
- Wk2 checkout idempotency + ledger + reconciliation. Wk3 event pipeline.
- Wk4 write the per-order timeline tool and present it.

## Done = You Can
- Design a money-handling system where every number is derivable and every
  state change is explicable after the fact.
