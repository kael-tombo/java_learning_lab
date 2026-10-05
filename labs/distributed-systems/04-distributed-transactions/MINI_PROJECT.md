# Distributed Transactions - Mini Project

## Project: Order Placement That Survives a Crashed Broker

### Objective
Implement a three-step order flow (reserve stock → charge payment → ship) three ways — 2PC,
SAGA, and transactional outbox — then kill the process at every step and compare the damage.

### Requirements
1. `LocalTransaction` abstraction over an in-memory store with commit/rollback
2. `TwoPhaseCoordinator` with prepare/commit/abort and an in-doubt state
3. `SagaOrchestrator` with persistent step state and compensations
4. `OutboxPublisher` — write event + outbox row in one local tx, relay publishes
5. A `CrashInjector` that kills the process at a chosen step number

### Steps

**Step 1: Two-phase commit, and its blocker**
```java
enum Decision { COMMIT, ABORT, IN_DOUBT }

void execute(List<LocalTransaction> participants) {
    final var prepared = new ArrayList<LocalTransaction>();
    for (var p : participants) {
        if (!p.prepare()) {            // vote
            participants.forEach(LocalTransaction::abort);
            return;
        }
        prepared.add(p);
    }
    // every participant must now vote commit; any crash here leaves IN_DOUBT
    participants.forEach(p -> p.commit(Decision.COMMIT));
}
```
Kill the coordinator between prepare and commit. Every participant is now IN_DOUBT, holding
locks, until a recovery process resolves the decision — which nobody wrote. That is the
practical cost of 2PC and the reason microservices abandoned it.

**Step 2: SAGA with honest compensation**
```java
record Step(String name,
            Runnable forward,
            Runnable compensate,
            boolean compensatable) { }
```
Steps: `reserveStock` → `chargeCard` → `createShipment`.

```java
void run() {
    for (int i = 0; i < steps.size(); i++) {
        var s = steps.get(i);
        try { s.forward(); journal.record(i, DONE); }
        catch (Exception e) {
            for (int j = i - 1; j >= 0; j--) {          // reverse order
                if (!steps.get(j).compensatable()) { manualReview(j); return; }
                steps.get(j).compensate(); journal.record(j, COMPENSATED);
            }
            return;
        }
    }
}
```
Mark `chargeCard` as `compensatable` but *slow* — a refund takes days. The journal is
persisted after every transition so a crash resumes rather than restarts.

**Step 3: Transactional outbox**
```java
@Transactional
void placeOrder(Order o) {
    stock.reserve(o.sku(), o.qty());        // same local tx
    outbox.insert(new OutboxRow(UUID.randomUUID().toString(),
                                "order.created", mapper.write(o)));
}
```
Relay loop:
```java
void relay() {
    for (var row : outbox.unpublished(100)) {
        try {
            broker.publish(row.topic(), row.payload(), row.id());  // id = dedup key
            outbox.markPublished(row.id());
        } catch (Exception e) { break; }     // leave for next pass, no loss
    }
}
```
If the relay crashes after publish but before `markPublished`, the event is re-sent. That is
**at-least-once**, and the consumer must dedupe on `row.id()`. Build the deduper now — you
will need it in the real-world lab.

**Step 4: Run the matrix**

| Crash point | 2PC | SAGA | Outbox |
|---|---|---|---|
| before prepare | clean abort | clean | no event emitted |
| after prepare, before commit | IN_DOUBT, locks held | N/A (no prepare) | N/A |
| mid-forward | coordinator recovery needed | compensation runs | no event, order not visible |
| after publish, before ack | N/A | N/A | duplicate event |

### Step 5: Prove the outbox claim
Assert that after a crash at every point, replaying the relay yields **exactly one logical
order.created** once the consumer's deduper is applied. Write that test; it is the entire
argument for the pattern.

### Deliverables
1. `TwoPhaseCoordinator`, `SagaOrchestrator`, `OutboxPublisher` + `DedupConsumer`
2. `CrashInjector` tests covering all four crash points for all three patterns
3. A comparison table: failure modes, recovery time, operational burden
4. A decision record: which pattern this flow should use and why

### Extension (CHALLENGE)
Add a compensating action that itself can fail (payment provider down) and implement a
retry-with-backoff plus a dead-letter path with manual reconciliation.

### Estimated Time
4-5 hours