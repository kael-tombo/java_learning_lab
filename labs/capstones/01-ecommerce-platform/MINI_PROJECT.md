# Ecommerce Platform — MINI PROJECT

## Project: Order Pipeline with Reservations, Idempotent Checkout, and a Ledger

A working slice of a retailer: catalogue → cart → reservation → checkout →
ledger, plus the event stream and a reconciliation job. Java 21, H2/Postgres,
in-memory HTTP.

### Scope
- Catalogue with versioned prices (a price change never mutates history).
- Cart with a reservation model: `available - reserved >= 0`, enforced in the
  database, not in Java.
- Checkout with an idempotency key, a payment call with a simulated timeout,
  and a compensating refund path.
- Double-entry ledger: every movement is a balanced pair of postings.
- Events published to an in-memory log with at-least-once delivery.
- Daily reconciliation against a simulated payment provider settlement file.

### Architecture

```
[HTTP API]  -> Catalogue / Cart / Checkout services
                   |                     |
             reservation table     [payment provider] (simulated, can time out)
                   |
             orders (state machine)
                   |
             [event log] -> projection / warehouse loader
                   |
             ledger postings (append only)  ->  daily reconciliation
```

### Implementation — inventory without overselling

The reservation is the whole concurrency story. `available` and `reserved` are
columns, and the check happens inside the transaction.

```java
public final class InventoryService {
    /**
     * Reservations, not stock decrements. We decrement `available` by
     * incrementing `reserved` in the same transaction, and commit only if
     * there is enough to reserve. Java-side checking would race.
     */
    public Reservation reserve(String sku, int qty, String cartId) {
        return txTemplate.execute(status -> {
            int updated = jdbc.update("""
                    UPDATE inventory
                       SET reserved = reserved + ?
                     WHERE sku = ?
                       AND on_hand - reserved >= ?
                    """, qty, sku, qty);
            if (updated == 0) throw new InsufficientStock(sku, qty);
            long ttl = now() + Duration.ofMinutes(15).toMillis();
            jdbc.update("INSERT INTO reservations (id, sku, qty, cart_id, expires_at) "
                    + "VALUES (?,?,?,?,?)", newId(), sku, qty, cartId, ttl);
            return new Reservation(newId(), sku, qty, cartId, ttl);
        });
    }

    /** A sweeper releases expired reservations. Without it, abandoned carts
     *  permanently consume stock, and the business calls it "phantom OOS". */
    @Scheduled(fixedDelay = 60_000)
    public int releaseExpired() {
        return jdbc.update("""
                UPDATE inventory i
                   SET reserved = reserved - r.qty
                  FROM reservations r
                 WHERE r.sku = i.sku AND r.expires_at < ? AND r.released_at IS NULL
                """, now());
    }
}
```

### Checkout idempotency

```java
public final class CheckoutService {
    /**
     * The idempotency key comes from the client, is stored with the outcome,
     * and the whole thing is one transaction. Two concurrent retries for the
     * same key serialize on the row and the second returns the first's result.
     */
    public CheckoutResult checkout(String idempotencyKey, CheckoutRequest req) {
        CheckoutResult prior = store.findByIdempotencyKey(idempotencyKey);
        if (prior != null) return prior;

        Order order = orders.createPending(req);          // state = PENDING_PAYMENT
        try {
            PaymentResult payment = paymentGateway.charge(
                    order.id(), req.total(), idempotencyKey);
            orders.markPaid(order.id(), payment.reference());
            ledger.recordOrderRevenue(order);             // balanced postings
            store.putIdempotencyKey(idempotencyKey, CheckoutResult.ok(order.id()));
            eventLog.publish("order.paid", order.id());
            return CheckoutResult.ok(order.id());
        } catch (PaymentTimeout e) {
            // Do NOT retry blindly: we do not know if the charge landed.
            // Mark for reconciliation, and let the provider's answer decide.
            orders.markPaymentUnknown(order.id());
            reconciliationQueue.enqueue(order.id());
            store.putIdempotencyKey(idempotencyKey, CheckoutResult.pending(order.id()));
            return CheckoutResult.pending(order.id());
        }
    }
}
```

### Double-entry ledger

```java
public final class Ledger {
    public record Posting(String account, long amountMinor, String currency,
                          String orderId, String reason, Instant at) {}
    public enum Account { CASH, RECEIVABLE, REVENUE, TAX_PAYABLE,
                          INVENTORY, COGS, REFUNDS, PAYMENT_FEES }

    /** Every entry is balanced: debits == credits. If not, the entry is rejected. */
    public Entry recordOrderRevenue(Order o) {
        return entry("order.revenue", List.of(
                new Posting(Account.REVENUE.toString(), -o.subtotalMinor(), o.currency(), o.id(), "revenue", now()),
                new Posting(Account.TAX_PAYABLE.toString(), -o.taxMinor(), o.currency(), o.id(), "tax", now()),
                new Posting(Account.CASH.toString(), o.totalMinor(), o.currency(), o.id(), "cash", now())));
    }

    public Entry recordRefund(Order o, long amountMinor) {
        return entry("order.refund", List.of(
                new Posting(Account.REFUNDS.toString(), amountMinor, o.currency(), o.id(), "refund", now()),
                new Posting(Account.CASH.toString(), -amountMinor, o.currency(), o.id(), "refund", now())));
    }

    private Entry entry(String type, List<Posting> postings) {
        long debits = postings.stream().filter(p -> p.amountMinor() < 0)
                .mapToLong(p -> -p.amountMinor()).sum();
        long credits = postings.stream().filter(p -> p.amountMinor() > 0)
                .mapToLong(p -> p.amountMinor()).sum();
        if (debits != credits) {
            throw new UnbalancedEntry(type, debits, credits);   // fail at write time
        }
        return append(type, postings);                           // never update, only append
    }
}
```

Order totals are then *derived*:

```java
public Money orderTotal(String orderId) {
    long minor = ledger.balanceOf(orderId, Account.REVENUE)
               .plus(ledger.balanceOf(orderId, Account.TAX_PAYABLE));
    return Money.ofMinor(minor, currencyOf(orderId));
}
```

Nothing writes `order.total` except the order creation path, and the ledger can
overrule it. When they disagree, the ledger is right — that is the point.

### Daily reconciliation

```java
public final class Reconciliation {
    public record Diff(String date, long ourCount, long theirCount,
                       long ourTotal, long theirTotal, Verdict verdict) {}

    public List<Diff> run(LocalDate day) {
        List<Order> settled = orders.settledOn(day);
        ProviderFile file = provider.settlementFile(day);
        Map<String, Long> theirs = file.byReference();
        Map<String, Long> ours = settled.stream()
                .collect(toMap(o -> o.paymentReference(), Order::totalMinor, Long::sum));

        List<Diff> out = new ArrayList<>();
        for (String ref : union(ours.keySet(), theirs.keySet())) {
            long a = ours.getOrDefault(ref, 0L), b = theirs.getOrDefault(ref, 0L);
            out.add(new Diff(day.toString(), ours.containsKey(ref) ? 1 : 0,
                    theirs.containsKey(ref) ? 1 : 0, a, b,
                    a == b ? Verdict.MATCH : Verdict.MISMATCH));
        }
        return out;      // an empty list is the only acceptable daily outcome
    }
}
```

### The per-order timeline

The debugging tool that turns "the customer says they paid twice" into a
one-screen answer.

```java
public final class OrderTimeline {
    public record Entry(Instant at, String source, String kind, String detail) {}

    public List<Entry> timeline(String orderId) {
        List<Entry> out = new ArrayList<>();
        out.addAll(db.select("SELECT created_at, 'db', 'created', status FROM orders "
                + "WHERE id = ?", orderId).stream()
                .map(r -> new Entry(r.ts(), "db", "state", r.status())).toList());
        out.addAll(eventLog.eventsFor(orderId).stream()
                .map(e -> new Entry(e.at(), "event", e.type(), payloadOf(e))).toList());
        out.addAll(ledger.entriesFor(orderId).stream()
                .map(e -> new Entry(e.at(), "ledger", e.type(), summarize(e))).toList());
        out.addAll(paymentGateway.callsFor(orderId).stream()
                .map(c -> new Entry(c.at(), "gateway", c.outcome(), c.reference())).toList());
        out.sort(Comparator.comparing(Entry::at));
        return out;
    }
}
```

### Test It

```java
@Test void concurrentReservationsNeverOversell() throws Exception {
    inventory.setOnHand("sku-1", 10);
    ExecutorService pool = Executors.newFixedThreadPool(50);
    List<Future<Boolean>> futures = new ArrayList<>();
    for (int i = 0; i < 50; i++) {
        futures.add(pool.submit(() -> {
            try { inventory.reserve("sku-1", 1, cartId()); return true; }
            catch (InsufficientStock e) { return false; }
        }));
    }
    long granted = futures.stream().filter(f -> f.get()).count();
    assertEquals(10, granted);
    assertEquals(10, inventory.reserved("sku-1"));
}

@Test void timeoutDoesNotDoubleCharge() {
    gateway.failNextWith(new PaymentTimeout());
    CheckoutResult r1 = service.checkout("key-1", request());
    CheckoutResult r2 = service.checkout("key-1", request());   // client retry
    assertEquals(r1.orderId(), r2.orderId());
    assertEquals(1, gateway.chargeAttempts("key-1"));
    assertEquals(Verdict.PENDING, reconciliationQueue.status(r1.orderId()));
}

@Test void ledgerIsBalanced() {
    ledger.recordOrderRevenue(order("o1", 1000, 80));
    ledger.recordRefund(order("o1", 1000, 80), 1000);
    for (Entry e : ledger.all()) assertEquals(0, signedSum(e), "unbalanced: " + e);
}
```

### Stretch

- Add a `PAYMENT_UNKNOWN` recovery flow driven by the provider's lookup API.
- Add a returns and restock path that reverses the inventory reservation.
- Emit events for every state transition and build a projection that asserts
  the projection matches the source.

## Deliverables
- [ ] Catalogue, cart, reservation, checkout, ledger, events — runnable end to end
- [ ] Reservation enforced in the database with a 50-thread concurrency test
- [ ] Idempotent checkout, including the timeout path, with a double-charge test
- [ ] Append-only double-entry ledger with a balance assertion at write time
- [ ] Daily reconciliation against a simulated settlement file
- [ ] Per-order timeline tool joining db, events, ledger, and gateway
- [ ] Order state machine with illegal transitions rejected
