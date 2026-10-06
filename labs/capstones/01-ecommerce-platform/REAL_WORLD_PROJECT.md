# Ecommerce Platform — REAL WORLD PROJECT

## Context

A mid-market home-and-garden retailer (~$180M GMV) sells through its own site,
two marketplaces, and 340 physical stores sharing one inventory. The
engineering org has 40 services, a strangler-fig migration off a monolith in
progress, and a data platform that reports revenue a day late. The order
service is the crown jewel and the single largest source of executive
meetings. You are the tech lead for the commerce platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| GMV | $180M/year, 4.1M orders/year, 62k orders on peak day |
| Peak | 1,400 orders/minute at Black Friday 00:00, 3x normal catalogue traffic |
| Channels | web, iOS, Android, 2 marketplaces, in-store POS, call centre |
| Systems | 40 services, monolith still serving catalogue + accounts, Postgres + DynamoDB |
| Inventory | 340 stores + 2 DCs, 1.9M active SKUs, 38k oversold lines/month |
| Money | 3 payment providers, 1 marketplace payout, daily settlement, 7-year audit |
| Compliance | PCI in checkout, tax by jurisdiction (14 states), PCI scope audit annually |
| Constraint | no big-bang cutover; the monolith must keep working throughout |

## Architecture (target)

```
        clients / marketplaces / POS
                   |
            [edge: BFF + CDN]            one contract per channel
                   |
   +---------------+----------------+
   |               |                |
 catalogue     cart/checkout     order service          (services)
 (monolith      + order svc)
  strangling)        |
              +-----+------+
              |            |
        [payment router]  [inventory reservation]
        3 providers      Postgres, authoritative
              |            |
              +-----+------+
                    |
          [order event log]  ->  projections  ->  warehouse
                    |                          (idempotent sinks)
              [ledger service]
                    |
       daily [reconciliation]  vs provider settlement files
```

Four decisions carried the design, each chosen for a specific reason.

## Key Implementation — the four decisions

**Decision 1: order state is a legal state machine, and only the order service
may move it.** Before, nine services could write `order.status`, and 31% of
support tickets were "what happened to my order".

```java
public enum OrderState {
    DRAFT, PENDING_PAYMENT, PAYMENT_UNKNOWN, PAID, PICKING, PACKED,
    SHIPPED, DELIVERED, CANCELLED, REFUNDED, PARTIALLY_REFUNDED
}

/** Transition table is data, not scattered if-statements. Illegal transitions
 *  are a bug and must be loud, not silently ignored. */
public final class OrderStateMachine {
    private static final Map<OrderState, Set<OrderState>> LEGAL = Map.of(
            DRAFT,                 Set.of(PENDING_PAYMENT, CANCELLED),
            PENDING_PAYMENT,       Set.of(PAID, PAYMENT_UNKNOWN, CANCELLED),
            PAYMENT_UNKNOWN,       Set.of(PAID, CANCELLED),        // resolved by reconciliation
            PAID,                  Set.of(PICKING, CANCELLED, REFUNDED, PARTIALLY_REFUNDED),
            PICKING,               Set.of(PACKED, CANCELLED),
            PACKED,                Set.of(SHIPPED),
            SHIPPED,               Set.of(DELIVERED),
            DELIVERED,             Set.of(REFUNDED, PARTIALLY_REFUNDED),
            CANCELLED,             Set.of(),
            REFUNDED,              Set.of(),
            PARTIALLY_REFUNDED,    Set.of(REFUNDED));

    public void transition(Order o, OrderState to, Actor actor) {
        Set<OrderState> allowed = LEGAL.get(o.state());
        if (!allowed.contains(to)) {
            throw new IllegalTransition(o.id(), o.state(), to, actor);
        }
        if (!actor.mayTransition(o.state(), to)) {
            throw new UnauthorisedTransition(o.id(), actor);
        }
        // Every transition is an event, not just a column update.
        outbox.insert(o.id(), "order.state", o.state(), to, actor, now());
    }
}
```

The outbox pattern matters: the state change and the event are committed
together, so "the order was paid but no event was published" is impossible. That
class of inconsistency was previously a daily occurrence.

**Decision 2: inventory is reserved, not decremented, and the check is in the
database.** 38k oversold lines a month came from Java-side availability checks
racing.

```java
/**
 * on_hand and reserved are the only two numbers. A sale moves stock from
 * `on_hand` to `sold`; a reservation moves it from `on_hand` to `reserved`.
 * The invariant `on_hand >= reserved >= 0` is enforced by a CHECK constraint,
 * not by application code, so a bug in any of 40 services cannot break it.
 */
@Transactional
public Reservation reserve(String sku, int qty, ReservationRequest req) {
    int updated = jdbc.update("""
            UPDATE inventory
               SET reserved = reserved + ?, version = version + 1
             WHERE sku = ? AND on_hand - reserved >= ? AND version = ?
            """, qty, sku, qty, req.expectedVersion());
    if (updated == 0) {
        throw new Conflict("insufficient stock or concurrent update for " + sku);
    }
    insertReservation(req.reservationId(), sku, qty, req.ttl());
    return reservation(req.reservationId());
}
```

Two additions that mattered more than the SQL:

```java
/** Channel-aware availability: a marketplace may only see stock we have
 *  allocated to it, otherwise a marketplace order consumes store stock that
 *  a shopper is standing in front of. */
public int sellableTo(String sku, Channel channel) {
    int physical = inventory.onHand(sku) - inventory.reserved(sku);
    int allocated = channelAllocation.get(sku, channel);
    return Math.max(0, Math.min(physical, allocated));
}

/** A reservation that is not converted to a sale within its TTL is released.
 *  This is the difference between 3% and 0.4% phantom out-of-stock. */
@Scheduled(fixedDelay = 30_000)
public int sweepExpired() { /* bulk update, index on expires_at */ }
```

**Decision 3: money is a ledger, and totals are derived.** Finance and support
could not always explain a total, because totals were stored on the order and
mutated by refund logic in three places.

```java
/**
 * Append-only, double-entry, and the balance is derived. Three properties that
 * fall out of this and that the old model could not provide:
 *   1. Every number is explainable: sum the postings.
 *   2. Nothing is silently mutated: a refund is a new entry, not an update.
 *   3. Mistakes are detectable: an unbalanced entry is rejected at write time.
 *
 * Amounts are integer minor units throughout. This is the single highest-value
 * decision in the codebase; every money bug traced back to a float.
 */
public Entry post(String orderId, List<Posting> postings) {
    long net = postings.stream().mapToLong(Posting::amountMinor).sum();
    if (net != 0) throw new UnbalancedEntry(orderId, net);
    return ledgerAppend(orderId, postings);   // no UPDATE path exists
}
```

Result: 4 audit findings on revenue reporting became 0, and refund handling
went from three implementations to one.

**Decision 4: checkout idempotency is client-supplied and durable.** The
timeout case is the hard one: you do not know whether the charge landed.

```java
public CheckoutResult checkout(String idempotencyKey, CheckoutRequest req) {
    // A durable record of the KEY, not the order. Retries return the recorded
    // outcome, whatever it is, including "pending".
    Optional<CheckoutResult> prior = attempts.find(idempotencyKey);
    if (prior.isPresent()) return prior.get();

    Order o = orders.create(req, idempotencyKey);
    try {
        PaymentResult p = router.charge(o, req, idempotencyKey);
        switch (p.status()) {
            case SETTLED -> { orders.markPaid(o, p); ledger.postOrderRevenue(o); }
            case DECLINED -> orders.failPayment(o, p.declineCode());
            case UNKNOWN  -> { orders.markPaymentUnknown(o, p); reconciler.enqueue(o); }
        }
        attempts.record(idempotencyKey, CheckoutResult.of(o));
        return attempts.find(idempotencyKey).orElseThrow();
    } catch (PaymentTimeout e) {
        orders.markPaymentUnknown(o, e);      // never retry a possibly-landed charge
        reconciler.enqueue(o);
        attempts.record(idempotencyKey, CheckoutResult.pending(o));
        return CheckoutResult.pending(o);
    }
}
```

And the recovery loop that resolves `PAYMENT_UNKNOWN`, which is the state the
old system simply did not have:

```java
@Scheduled(fixedDelay = 60_000)
public int resolveUnknownPayments() {
    List<Order> unknown = orders.inState(PAYMENT_UNKNOWN, olderThan(2, MINUTES));
    for (Order o : unknown) {
        PaymentLookup lookup = router.lookup(o.paymentAttemptId());   // idempotent read
        switch (lookup.status()) {
            case SETTLED -> { orders.markPaid(o, lookup); ledger.postOrderRevenue(o);
                              alerts.info("resolved " + o.id()); }
            case ABSENT  -> { orders.failPayment(o, "not found at provider");
                              alerts.info("released " + o.id()); }
            case PENDING -> { /* still pending: leave it, look again next tick */ }
        }
    }
    return unknown.size();
}
```

## Data Platform Side

The warehouse is downstream of the event log, and its correctness rules are
the ones from `labs/data-engineering/19-data-governance`.

- **Revenue** is computed from ledger postings, never from `order.total`. This
  single change made revenue reproducible at any past instant.
- **Daily reconciliation** against each of the 3 provider settlement files, with
  0.5% tolerance and an empty-diff daily requirement.
- **Freshness SLO** on `orders_enriched`: 2h, owner = commerce analytics, with
  the consequence written down: it feeds the 06:00 revenue email.
- **Idempotent sink** keyed by `order_id` with the event's LSN guard, so a
  replay converges.
- **Point-in-time** customer features: the LTV feature used for a campaign must
  be the LTV as of the campaign date, not today.

```java
/** Reconciliation is per provider, because providers fail differently and a
 *  combined diff hides which one is wrong. */
public List<ReconciliationReport> reconcileAll(LocalDate day) {
    return List.of(stripe.reconcile(day), adyen.reconcile(day), braintree.reconcile(day));
}
```

## Failure Modes and the Runbook

1. **Oversell despite reservations.** Symptom: a SKU goes negative after the
   release wave. Cause: a channel allocation greater than physical stock.
   Fix: the CHECK constraint fires first; the real fix is reconciling
   allocations daily and clamping sellable-to to physical.
2. **Payment unknown backlog grows.** Symptom: orders stuck in
   `PAYMENT_UNKNOWN`. Fix: the resolution loop is the mechanism; alert on
   backlog age, and check whether the provider's lookup API is degraded, which
   looks identical from the order side.
3. **Order stuck in PENDING_PAYMENT.** Cause: a worker died between the charge
   and the state transition. Fix: a sweeper that re-resolves via the provider
   lookup, exactly as for `PAYMENT_UNKNOWN`. Both states share one recovery path.
4. **Tax mismatch by jurisdiction.** Cause: a rate table change mid-checkout.
   Fix: the tax rate is snapshotted onto the order at checkout and the source
   rate table is versioned; disputes resolve against the snapshot.
5. **Reconciliation non-empty at 06:00.** Fix: do not release the revenue
   figure. Ship with a stated provisional number and the diff, and escalate.
   A silent release is how a 3% overstatement reached a partner once.
6. **Outbox backlog grows.** Symptom: events late, state correct. Cause: the
   relay is down or the topic is throttled. Fix: outbox is a queue with a
   depth SLO, and a "catch up from the outbox" command that is safe because the
   consumers are idempotent.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- The transactional outbox pattern commits a state change and its event in one
  database transaction, with a relay publishing afterwards; it removes the
  "state changed but the event was lost" failure without distributed
  transactions.
  - Reference: https://microservices.io/patterns/data/transactional-outbox.html
  - Reference: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/outbox.html
- Idempotency keys are the standard mechanism for making retried payment or
  order operations safe when a client cannot know whether the first attempt
  succeeded.
  - Reference: https://docs.stripe.com/api/idempotent_requests
  - Reference: https://datatracker.ietf.org/doc/html/rfc9110#name-idempotent-methods
- Kafka's consumer groups and committed offsets, combined with idempotent
  consumers, are the basis for at-least-once event propagation from the outbox
  to downstream projections and the warehouse.
  - Reference: https://kafka.apache.org/documentation/#intro_concepts_and_terms
  - Reference: https://kafka.apache.org/documentation/#consumerconfigs

## Deliverables
- [ ] Order state machine as data, with only the order service permitted to
      transition, and every transition producing an outbox event
- [ ] Reservation model with a database-enforced invariant, channel allocation,
      and an expiry sweeper; oversell rate target < 0.01%
- [ ] Idempotent checkout with a durable key and a `PAYMENT_UNKNOWN` recovery
      loop driven by provider lookup
- [ ] Append-only double-entry ledger in integer minor units, totals derived
- [ ] Revenue computed from the ledger, reproducible at any past instant
- [ ] Daily per-provider reconciliation with an empty-diff requirement
- [ ] Outbox relay with a depth SLO and a safe catch-up command
- [ ] Per-order timeline tool spanning db, events, ledger, and provider
- [ ] Runbook for the six failure modes
