# Distributed Queues - Mini Project

## Project: A Durable Queue with Visibility Timeouts and a DLQ

### Objective
Implement a queue where in-flight work is protected by a visibility timeout rather than a
lock, then crash consumers at every stage and prove nothing is lost or double-counted.

### Requirements
1. `InMemoryPartitionedQueue` — partitioned, durable-before-ack append
2. Visibility timeout with redelivery and a delivery-count guard
3. `DeadLetterQueue` with move-after-max-attempts and a replay tool
4. `MessageDeduplicator` — TTL-based dedupe on message ID
5. Crash harness that kills a consumer at each processing stage

### Steps

**Step 1: Durable before ack**
```java
long enqueue(Message m) {
    synchronized (this) {
        long id = nextId++;
        m.id = id;
        m.deliveryCount = 0;
        store.append(m);                              // durable FIRST
        ready.addLast(m);
        return id;
    }
}
Message poll(Duration visibilityTimeout) {
    synchronized (this) {
        requeueExpired();                            // see step 2
        var m = ready.pollFirst();
        if (m == null) return null;
        m.visibleUntil = now().plus(visibilityTimeout);
        m.deliveryCount++;
        inFlight.add(m);
        return m;
    }
}
```
Order matters: durability before the client sees the enqueue ack, and visibility before the
client sees the poll. Reverse either and you have a silent loss path.

**Step 2: Visibility timeout is a lease**
```java
void requeueExpired() {
    for (var it = inFlight.iterator(); it.hasNext(); ) {
        var m = it.next();
        if (now().isAfter(m.visibleUntil)) {
            if (m.deliveryCount >= MAX_DELIVERIES) { it.remove(); dlq.move(m); }
            else { it.remove(); ready.addLast(m); }  // redeliver
        }
    }
}
```
Sizing the visibility timeout is the main tuning decision. Too short and slow workers get
double-processed; too long and a crashed worker's message is stuck. Measure processing
duration p99 and set `timeout ≈ p99 × 3`, then verify under induced latency.

**Step 3: Dedupe so retries are harmless**
```java
boolean firstSight(String messageId) {
    return seen.putIfAbsent(messageId, now().plus(DEDUPE_TTL)) == null;
}
// consumer:
if (!dedupe.firstSight(msg.id)) { ack(msg); return; }     // already processed
process(msg);                                             // idempotent anyway -- both
```
Do both. The dedupe window makes redelivery cheap; the idempotent operation makes it correct.
Either alone leaves a gap.

**Step 4: Poison messages need a terminal path**
```java
class DeadLetterQueue {
    void move(Message m) { dlq.add(m.withHeader("x-death", reason(m))); }
    void replay(String dlqName, Predicate<Message> filter) {
        dlq.filter(filter).forEach(m -> {                // same message ID on purpose:
            target.enqueue(m.withoutDeliveryCountReset());   // dedupe sees it and skips
        });
    }
}
```
Keeping the original message ID across a replay is deliberate: if the original processing
actually succeeded but the ack was lost, replay is a no-op. Test that.

**Step 5: The crash matrix**
```java
enum Stage { BEFORE_VISIBILITY, AFTER_VISIBILITY, MID_PROCESS, AFTER_PROCESS_BEFORE_ACK, AFTER_ACK }
@Test
void noStageLosesAMessage() {
    for (var stage : Stage.values()) {
        var q = queueWithOneMessage();
        consumer.crashAt(stage);
        q.poll(Duration.ofSeconds(2));
        assertThat(processCountFor("msg-1")).isBetween(1, 2);   // never 0, at most 2
        assertThat(q.dlq().size()).isZero();                     // never lost to DLQ
    }
}
```
Run each stage. `AFTER_PROCESS_BEFORE_ACK` gives you exactly 2 processings — that is
at-least-once, and the dedupe is what makes the second one harmless. Assert it rather than
hoping.

**Step 6: Priority and delayed delivery**
```java
Optional<Message> poll(Duration visibility) {
    requeueExpired();
    // strict priority: check the urgent queue before the normal one
    var m = urgent.pollFirst();
    if (m == null) m = ready.pollFirst();
    ...
}
```
Delayed delivery needs a separate timer structure, not a scan of the main queue — scanning
per poll is O(n) and becomes the bottleneck under load.

### Deliverables
1. `InMemoryPartitionedQueue` with visibility timeout and delivery counting
2. `DeadLetterQueue` with a replay tool that preserves message IDs
3. `MessageDeduplicator` plus the five-stage crash matrix test
4. A tuning note: visibility timeout derived from measured p99, with the trade explained

### Extension (CHALLENGE)
Add fair dispatch across queues so a flood on one queue cannot starve another, and prove it
with a starvation test.

### Estimated Time
3 hours