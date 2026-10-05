# Message Queues & Protocols - MINI PROJECT

## Project: RelayLine — a broker with consumer groups, delivery semantics, and a real DLQ

Implement a minimal broker: partitioned topics, consumer groups with rebalancing, at-least
once delivery, and a dead-letter queue. Then make consumption idempotent and prove the
semantics hold under failure.

### Architecture

```
  Producers ──▶ Broker ──▶ Topic (N partitions, replicated)
                 │            │
                 │            ├──▶ Consumer Group A: 3 members, each owns 1 partition
                 │            │    rebalance: member joins/leaves -> partitions reassigned
                 │            │
                 │            └──▶ Consumer Group B: 2 members (independent offsets)
                 │
                 └──▶ DLQ (messages that failed MAX_ATTEMPTS or failed validation)

  Delivery semantics under test:
    at-most-once:  commit offset BEFORE processing   -> messages can be LOST
    at-least-once: commit offset AFTER processing    -> messages can be DUPLICATED
    effectively-once: at-least-once + idempotent processing + transactional effects

  The offset model:
    consumer keeps (partition, offset) per group
    commit = "I have processed everything up to offset N in partition P"
    rebalance -> new owner resumes from the last committed offset
```

### Implementation

The broker core, where the commit decision determines the semantics:

```java
final class Partition {
    private final Deque<Record> log = new ArrayDeque<>();
    private final Map<String, Long> committedOffsets = new HashMap<>();   // per consumer GROUP
    private final int maxRecords;

    void append(Record r) {
        if (log.size() == maxRecords) {
            // Retention, not an error. A bounded log is what makes a partitioned-log broker
            // fundamentally different from an unbounded queue: storage is a fixed budget.
            log.pollFirst();
        }
        log.addLast(r);
        // A single broker with one partition is a queue with a retention policy. The
        // LOG model only earns its complexity with many partitions and replay.
    }

    /** Read for a group: everything AFTER the group's committed offset. This is the
     *  mechanism that makes replay and rewind possible. */
    List<Record> readFrom(String group, int max) {
        long from = committedOffsets.getOrDefault(group, 0L);
        return log.stream().filter(r -> r.offset() >= from).limit(max).toList();
    }

    void commit(String group, long offset) {
        // Monotonic commit: a stale commit from a slow consumer must not rewind the group,
        // or another consumer would reprocess records that were already handled.
        committedOffsets.merge(group, offset, Math::max);
    }
}
```

Consumer group coordination and rebalancing, the part that causes real incidents:

```java
final class GroupCoordinator {
    private final Map<String, GroupState> groups = new ConcurrentHashMap<>();

    /**
     * The classic membership protocol. A joiner sends JoinGroup; the leader (the member
     * with the lowest id) collects all members and computes an assignment, then SyncGroup
     * distributes it.
     */
    void onJoinGroup(String group, String memberId) {
        var state = groups.computeIfAbsent(group, GroupState::new);
        state.addPendingMember(memberId);
        if (state.isLeader()) {
            // Leader assigns partitions. Rebalance policy matters:
            //   range: partitions grouped by topic, simple but can be unbalanced
            //   round-robin: spreads evenly, standard choice
            //   sticky: minimises partition movement on rebalance (fewer duplicates)
            var assignment = stickyAssigner.assign(state.members(), state.partitions());
            state.commitAssignment(assignment);
            state.notifyLeaderComplete();
        }
    }

    /**
     * STICKY assignment is the improvement that most reduces operational pain. On a
     * naive range assignment, adding one consumer to a 3-consumer/12-partition group moves
     * many partitions, so many records get reprocessed. Sticky keeps most partitions
     * where they were and moves as few as possible.
     */
    record Assignment(Map<String, Set<Integer>> memberToPartitions) {
        int partitionsMovedOnRejoin(String newMember, Set<String> existing) {
            // Only partitions for the new member are new work; the rest stay put.
            return memberToPartitions.getOrDefault(newMember, Set.of()).size();
        }
    }
}
```

Idempotent consumption, which is what converts at-least-once into effectively-once:

```java
@Service
class OrderProcessingConsumer {
    private final ProcessedMessageRegistry registry;      // durable, not in-memory
    private final OrderRepository orders;
    private final PaymentGateway payments;

    /**
     * At-least-once means duplicates WILL happen (a rebalance between processing and
     * committing, a crash, a redelivery after a timeout). So the handler must be
     * idempotent. Two mechanisms, and the registry is the essential one.
     */
    @KafkaListener(topics = "orders.placed", groupId = "order-processing")
    public void onOrderPlaced(OrderPlaced event) {
        // 1. Dedupe on the event ID, in a DURABLE store with a uniqueness constraint.
        //    In-memory dedupe fails the moment the pod restarts, which is exactly when a
        //    redelivery is most likely.
        if (registry.alreadyProcessed(event.eventId())) {
            log.debug("duplicate order event {}, skipping", event.eventId());
            registry.markDuplicate(event.eventId());
            return;                                        // safe: no side effects repeated
        }

        try {
            // 2. Perform the side effect with an idempotency key the DOWNSTREAM honours.
            //    The payment gateway is called with eventId as its idempotency key, so a
            //    duplicate returns the original result instead of charging twice.
            var confirmation = payments.capture(event.paymentId(), event.amount(),
                                                idempotencyKey: event.eventId());

            // 3. Record success durably. Order matters: record AFTER the effect. If we
            //    record first and then crash, the retry is skipped and the effect never
            //    happens. After, a crash causes a retry, which the idempotency key absorbs.
            registry.record(event.eventId(), confirmation.reference(), Instant.now());
            orders.markPaid(event.orderId(), confirmation.reference());

        } catch (ValidationException e) {
            // 4. PERMANENT failure: do NOT retry. Retrying an invalid message forever is
            //    how a poison pill stops a partition. Route it to the DLQ immediately.
            dlq.publish(event, DeadLetterReason.VALIDATION_FAILED, e.getMessage());
            registry.record(event.eventId(), "DLQ", Instant.now());

        } catch (TransientException e) {
            // 5. TRANSIENT failure: throw so the framework does NOT commit the offset and
            //    the message is redelivered. No registry write, so the retry is genuine.
            throw e;
        }
    }
}
```

DLQ policy, with the hygiene most implementations lack:

```java
@Service
class DeadLetterQueue {
    /**
     * A DLQ is only useful if it is (a) bounded, (b) alerted on, and (c) replayable.
     * An unbounded DLQ is a second data-loss problem: it fills a disk and nobody notices.
     */
    void publish(Record record, DeadLetterReason reason, String detail) {
        dlqQueue.offer(new DeadLetter(
                originalTopic: record.topic(), partition: record.partition(), offset: record.offset(),
                payload: record.payload(), reason, detail,
                attempts: record.deliveryAttempts(),
                failedAt: Instant.now(),
                expiresAt: Instant.now().plus(RETENTION)));        // 30 days, then purge
        metrics.counter("dlq.message", "reason", reason.name(), "topic", record.topic()).increment();
        alert.onNewDeadLetter(record.topic(), reason);              // an alert, not a log line
    }

    /** Replay with care: reprocessing a DLQ entry can double side effects, so replay
     *  requires the SAME idempotency guarantees as the original consumer. */
    void replay(String deadLetterId, boolean force) {
        var dl = dlq.get(deadLetterId);
        if (!force && dl.reason() == VALIDATION_FAILED)
            throw new CannotReplayException("will fail again: the message is still invalid");
        broker.publish(dl.originalTopic(), dl.payload());
        dlq.remove(deadLetterId);
    }

    @Scheduled(fixedDelay = 3600_000)
    void enforceBounds() {
        // Report, then purge. Never purge silently: a DLQ that empties itself hides the
        // fact that it was full, which is the signal someone needed.
        var expired = dlqQueue.expiredBefore(Instant.now().minus(RETENTION));
        if (!expired.isEmpty()) { metrics.gauge("dlq.purged", expired.size()); audit.purged(expired); }
    }
}
```

The poison-pill control that actually prevents a stuck partition:

```java
/**
 * A partition stops progressing when one message always fails. The remedies, in order of
 * preference:
 *   1. Distinguish transient from permanent failure and never retry the permanent one.
 *   2. Cap delivery attempts, then DLQ.
 *   3. Increase max.poll.interval only if processing legitimately takes long, so a slow
 *      consumer is not rebalanced away mid-message.
 */
record ConsumerConfig(int maxDeliveryAttempts, Duration maxPollInterval, Duration backoff) {
    static final ConsumerConfig DEFAULT = new ConsumerConfig(5, Duration.ofMinutes(5), Duration.ofSeconds(1));
    // max.poll.interval is the subtle one: exceed it and the broker assumes the consumer
    // is dead and reassigns its partitions, so a slow handler causes a rebalance, which
    // causes reprocessing, which makes it slower. That feedback loop is a classic outage.
}
```

### Test It

```java
@Test void atLeastOnceProducesDuplicatesButNoLoss() {
    broker.append("t", record(eventId: "e1", payload: "order-1"));
    consumer.process("g", commitBeforeProcessing: false);
    // Simulate a crash AFTER processing, BEFORE committing.
    consumer.crashAfterProcessing("g");
    broker.redeliverUncommitted("g");

    assertThat(deliveredCount).isEqualTo(2);          // duplicate delivered
    assertThat(registry.processedCount()).isEqualTo(1); // but only one effect
}

@Test void atMostOnceCanLoseMessages() {
    consumer.process("g", commitBeforeProcessing: true);
    consumer.crashAfterProcessing("g");
    broker.redeliverUncommitted("g");
    // The offset was already committed, so the record is never redelivered: a LOSS.
    assertThat(deliveredCount).isEqualTo(1);
    // This test exists to make the trade-off concrete: at-most-once is only correct when
    // losing a message is genuinely acceptable.
}

@Test void idempotentConsumerProducesOneEffectFromManyDuplicates() {
    repeat(10, () -> consumer.onOrderPlaced(orderPlaced(eventId: "e-42", amount: 100)));
    assertThat(paymentsGateway.captureCalls()).isEqualTo(10);   // all calls attempted
    assertThat(paymentsGateway.chargesActuallyMade()).isEqualTo(1);  // one charge, via idempotency key
}

@Test void permanentFailureGoesStraightToDlqWithoutRetrying() {
    consumer.onOrderPlaced(orderPlaced(eventId: "bad", amount: -5));   // invalid
    assertThat(deliveryAttemptsFor("bad")).isEqualTo(1);       // not 5
    assertThat(dlq.size()).isEqualTo(1);
    assertThat(dlq.get(0).reason()).isEqualTo(VALIDATION_FAILED);
}

@Test void poisonPillDoesNotStallThePartition() {
    broker.append("t", poisonMessage());                 // always fails
    broker.append("t", goodMessage());
    consumer.processBatch("g");
    // The good message MUST still be processed. A stuck partition is the failure mode.
    assertThat(processedSuccessfully()).contains("good-message");
}

@Test void rebalanceReassignsPartitionsAndResumesFromCommittedOffset() {
    group.join("m1", "m2", "m3");                     // 3 members, 6 partitions
    group.leave("m2");
    var assignment = group.stickyAssignment();
    assertThat(assignment.partitionsFor("m1")).isNotEmpty();
    assertThat(assignment.partitionsFor("m3")).isNotEmpty();
    // Sticky assignment: m1 and m3 keep most of what they had, minimising reprocessing.
    assertThat(assignment.movedFrom("m1")).isLessThan(2);
}

@Test void replayOfAnInvalidDlqEntryIsRefused() {
    dlq.publish(record, VALIDATION_FAILED, "amount negative");
    assertThrows(CannotReplayException.class, () -> dlq.replay(id, force: false));
    assertThat(dlq.replayableNow()).isFalse();
}

@Test void lagIsMeasuredAndAlertedBeforeItBecomesAnOutage() {
    consumer.pause();
    broker.appendBulk("t", 100_000);
    metrics.collect();
    // Lag alert fires while there is still time to act, not after the SLO is already lost.
    assertThat(alerts.raised()).anyMatch(a -> a.name().equals("CONSUMER_LAG_HIGH")
            && a.consumerGroup().equals("order-processing"));
}
```

## Deliverables

- [ ] Partitioned broker with per-consumer-group committed offsets and monotonic commits
- [ ] Consumer group with leader-coordinated assignment and sticky rebalancing
- [ ] At-most-once and at-least-once modes, each with a test demonstrating its failure mode
- [ ] Idempotent consumer using a durable dedupe registry and downstream idempotency keys
- [ ] Transient vs permanent failure distinction, with permanent failures DLQ'd immediately
- [ ] Bounded DLQ with alerting, retention, and a replay guard for still-invalid messages
- [ ] Poison-pill test proving a bad message does not stall its partition
- [ ] Lag metric with an early alert threshold, and `max.poll.interval` documented
- [ ] A delivery-semantics decision doc naming the guarantees and their boundaries
