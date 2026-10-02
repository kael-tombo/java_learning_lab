# Distributed Transactions Exercises

## Exercise 1: 2PC Coordinator Implementation (Code Task)

**Implement** a 2PC coordinator and participant framework:

```java
// TwoPhaseCommitCoordinator.java
public class TwoPhaseCommitCoordinator {
    // TODO: 
    // 1. beginTransaction() → returns transactionId
    // 2. enlistParticipant(transactionId, participant)
    // 3. prepare(transactionId) → sends Prepare to all, collects votes
    // 4. commit(transactionId) or abort(transactionId)
    // 5. Recovery: on restart, read log, complete in-doubt transactions
}

// Participant Interface
public interface XAResource {
    void prepare(String txId) throws XAException;
    void commit(String txId) throws XAException;
    void rollback(String txId) throws XAException;
}
```

**Requirements**:
- Persistent transaction log (write-ahead) for coordinator
- Participant state machine: INITIAL → PREPARED → COMMITTED/ABORTED
- Timeout handling: abort if participant doesn't respond to prepare
- Idempotent prepare/commit/rollback (retry safe)

**Failure Injection Tests**:
1. Kill coordinator after prepare, before decide → verify recovery completes
2. Participant crashes after prepare → verify it recovers to PREPARED state
3. Network partition during commit → verify eventual consistency

---

## Exercise 2: Orchestrated Saga for Order Placement (Code Task)

**Implement** a Saga orchestrator with persistent state:

```java
// SagaOrchestrator.java
public class SagaOrchestrator {
    // State machine per saga instance:
    // CREATED → STEP_1_EXECUTING → STEP_1_COMPLETED → STEP_2_EXECUTING → ...
    //                    → COMPENSATING_STEP_1 → COMPENSATED → FAILED/COMPLETED
    
    // TODO:
    // execute(SagaDefinition saga, Map<String, Object> input)
    // handleReply(stepName, result)
    // handleTimeout(stepName)
    // compensate(completedSteps)
}

// SagaDefinition:
SagaDefinition orderSaga = SagaDefinition.builder()
    .step("reserveInventory", ReserveInventoryAction.class, ReleaseInventoryCompensation.class)
    .step("chargePayment", ChargePaymentAction.class, RefundPaymentCompensation.class)
    .step("createShipment", CreateShipmentAction.class, CancelShipmentCompensation.class)
    .build();
```

**Requirements**:
- Persist saga state after each step (DB or event store)
- Idempotent action execution (idempotency keys)
- Configurable timeouts per step with retry policy
- Compensation ordering: reverse of execution
- Event emission for monitoring (SagaStarted, StepCompleted, Compensating, SagaCompleted)

**Failure Injection**:
1. Payment service returns 500 after inventory reserved → verify compensation runs
2. Orchestrator crashes after "chargePayment" → verify resumes correctly on restart
3. Network timeout on "createShipment" → verify retry then compensate

---

## Exercise 3: Outbox Pattern Implementation (Code Task)

**Implement** the transactional outbox pattern with a relay:

```java
// OutboxEntity.java
@Entity
public class OutboxEvent {
    @Id String id;
    String aggregateType;
    String aggregateId;
    String eventType;
    String payload; // JSON
    Instant createdAt;
    Instant publishedAt; // null = not published
    int retryCount;
}

// OutboxRepository.java
public interface OutboxRepository {
    List<OutboxEvent> findUnpublished(int batchSize);
    void markPublished(String id);
    void incrementRetry(String id);
}

// OutboxRelay.java
@Component
public class OutboxRelay {
    // TODO: Poll unpublished events, publish to Kafka, mark published
    // Handle: ordering per aggregate, retries, dead letter
}
```

**Application Usage**:
```java
@Transactional
public void placeOrder(Order order) {
    orderRepository.save(order);
    outboxRepository.save(new OutboxEvent(
        UUID.randomUUID().toString(),
        "Order", order.getId(),
        "OrderPlaced",
        toJson(new OrderPlacedEvent(order))
    ));
}
```

**Requirements**:
- Relay polls every 100ms, batch size 100
- Preserve ordering per aggregate (partition by aggregateId)
- Exponential backoff retry (max 5 retries)
- Dead letter queue for permanently failed events
- Metrics: lag, throughput, error rate

**Failure Injection**:
1. Kafka broker down for 30s → verify relay catches up
2. Duplicate publish (relay crashes after publish, before mark) → verify idempotent consumer handles
3. Outbox table grows → verify cleanup job for published events

---

## Exercise 4: Idempotent Payment Processing (Design + Code Task)

**Scenario**: Payment service receives `ChargeRequest { idempotencyKey, amount, currency, customerId }`.

**Design** the idempotency layer:

```java
// IdempotencyService.java
public class IdempotencyService {
    // TODO: 
    // checkAndReserve(key) → returns IdempotencyResult { status: NEW | PROCESSING | COMPLETED, result? }
    // complete(key, result)
    // fail(key, error)
}

// PaymentController.java
@PostMapping("/charges")
public ResponseEntity<ChargeResponse> charge(@RequestHeader("Idempotency-Key") String key, 
                                              @RequestBody ChargeRequest request) {
    // TODO: Use IdempotencyService
}
```

**Requirements**:
- States: NEW → PROCESSING → COMPLETED/FAILED
- TTL on PROCESSING (e.g., 5 min) to handle crashed requests
- Concurrent requests with same key: one executes, others wait or return 409
- Store full response for replay

**Test Scenarios**:
1. Client sends request, network fails before response → client retries with same key → returns original result
2. Two concurrent requests with same key → only one processes
3. Request takes 30s, client retries at 10s → second request waits for first

---

## Exercise 5: Consistency Model Trade-off Analysis (Reasoning Task)

**Analyze** each scenario. For each, specify:
- **Chosen pattern**: 2PC / Saga (orchestrated) / Saga (choreography) / Calvin-style / Spanner
- **Consistency model achieved**: Linearizable / Causal / Eventual / Read-your-writes
- **PACELC classification**
- **Why not the alternatives?**

| Scenario | Requirements | Your Choice | Consistency | PACELC | Why Not Others? |
|----------|--------------|-------------|-------------|--------|-----------------|
| Bank transfer (internal) | No lost money, audit, < 50ms | | | | |
| Bank transfer (cross-bank) | External systems, days to settle | | | | |
| E-commerce order | Inventory, payment, shipping | | | | |
| Ride-hailing dispatch | Match driver, reserve, notify | | | | |
| Config deployment | All nodes same version, fast | | | | |
| Analytics pipeline | Process events exactly-once | | | | |
| Multiplayer game state | Low latency, eventual OK | | | | |
| Distributed lock service | Mutual exclusion, fast | | | | |

---

## Exercise 6: Calvin-Style Deterministic Transaction (Code Task)

**Implement** a simplified Calvin sequencer + executor:

```java
// CalvinSequencer.java
public class CalvinSequencer {
    // Uses Raft to agree on transaction log order
    // TODO: propose(Transaction tx) → returns global sequence number
}

// CalvinExecutor.java
public class CalvinExecutor {
    // Executes transactions in sequence number order
    // TODO: execute(Transaction tx) → deterministic, no locks
    // Pre-condition: read/write sets known statically
}

// DeterministicTransaction interface:
interface DeterministicTransaction {
    Set<String> readSet();   // Keys read
    Set<String> writeSet();  // Keys written
    Result execute(ReadOnlyView snapshot); // Pure function of snapshot
}
```

**Requirements**:
- Sequencer: Raft-based (use existing library or simple majority)
- Executor: Single-threaded per partition, applies in seq order
- Transaction must declare read/write sets upfront
- No random, no time, no external calls in execute()

**Test**:
1. Submit 1000 concurrent transactions → verify serializable execution
2. Kill executor → restart → verify state matches log replay
3. Compare latency vs 2PC for same workload

---

## Exercise 7: Spanner TrueTime Simulation (Analysis Task)

**Simulate** Spanner's commit wait with TrueTime uncertainty:

```python
# true_time_simulation.py
import random
import time

class TrueTime:
    def __init__(self, epsilon_ms=5):
        self.epsilon_ms = epsilon_ms  # uncertainty bound
    
    def now(self):
        # Returns interval [earliest, latest]
        now = time.time() * 1000
        return (now - self.epsilon_ms, now + self.epsilon_ms)
    
    def after(self, t):
        # Wait until guaranteed after t
        pass

# Spanner commit:
def spanner_commit(transaction, true_time):
    # 1. Get commit timestamp s = true_time.now().latest
    # 2. Write lock, assign s to transaction
    # 3. Paxos replicate
    # 4. true_time.after(s)  # Wait out uncertainty
    # 5. Release locks, serve reads at s
    pass
```

**Analyze**:
1. With ε = 5ms, what is minimum commit latency? (2 RTT + ε)
2. If cross-region RTT = 50ms, ε = 5ms, what is p99 latency?
3. What happens if clock uncertainty grows (e.g., GPS failure → ε = 200ms)?
4. How does this compare to Calvin (1 RTT, no wait) and 2PC (2 RTT, no ε)?

**Deliverable**: Latency calculations + failure mode analysis

---

## Exercise 8: Distributed Lock with Fencing (Code Task)

**Implement** a distributed lock using ZooKeeper/etcd with fencing tokens:

```java
// DistributedLock.java
public class DistributedLock {
    // TODO:
    // acquire(lockName, clientId) → returns FencingToken
    // release(FencingToken)
    // isValid(FencingToken) → checks token not stale
}

// FencingToken:
public record FencingToken(long sequenceNumber, String lockName) {}

// Resource server validates:
public void writeData(FencingToken token, Data data) {
    if (token.sequenceNumber() <= lastSeenToken) {
        throw new FencingException("Stale token");
    }
    lastSeenToken = token.sequenceNumber();
    // write data
}
```

**Requirements**:
- Monotonically increasing sequence numbers per lock
- TTL-based auto-release (session expiry)
- Fencing token prevents split-brain writes
- Client caches token, includes in all resource requests

**Failure Injection**:
1. Client acquires lock, GC pause 10s → lock expires, another client acquires → first client's write rejected by fencing
2. Network partition → verify only one side can acquire

---

## Exercise 9: Chaos Testing Distributed Transactions (Experimental Task)

**Target**: Running system with 2PC, Saga, or Calvin implementation.

**Inject failures** and measure:

| Failure | 2PC Behavior | Saga Behavior | Calvin Behavior |
|---------|--------------|---------------|-----------------|
| Coordinator/Sequencer kill | | | |
| Participant/Executor kill | | | |
| Network partition (split) | | | |
| Disk slow (100ms latency) | | | |
| Clock skew (NTP offset) | | | |

**Metrics to capture**:
- Time to detect failure
- Time to recover
- Data consistency (any lost updates? duplicates?)
- Client-visible errors
- Throughput during recovery

**Deliverable**: Comparison table + recommendations for each pattern

---

## Exercise 10: Real-World Incident Analysis (Research Task)

**Pick ONE** incident and write a 2-page postmortem-style analysis:

1. **Knight Capital** (2012): $440M loss from dead code path in deployment
2. **GitHub** (2018): 24h outage from MySQL orchestrator failover + orchestrator bug
3. **Cloudflare** (2020): Global outage from bad regex in WAF (not distributed txn but relevant)
4. **Amazon DynamoDB** (2015): 5h outage from metadata service overload
5. **Slack** (2022): Outage from Vitess sharding + connection pooling

**Structure**:
1. What happened (timeline)
2. Root cause (distributed transaction / consensus angle)
3. Why existing safeguards failed
4. What consistency model was violated
5. Lessons for your implementations

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1. 2PC Implementation | 20 | Correct protocol, persistent log, recovery |
| 2. Saga Orchestrator | 20 | State machine, persistence, compensation, idempotency |
| 3. Outbox Pattern | 15 | Relay works, ordering, retries, metrics |
| 4. Idempotency Layer | 15 | Correct states, TTL, concurrency handling |
| 5. Consistency Analysis | 10 | Accurate mapping, clear reasoning |
| 6. Calvin Implementation | 15 | Deterministic execution, sequencing |
| 7. TrueTime Analysis | 10 | Correct latency math, failure modes |
| 8. Fencing Lock | 10 | Monotonic tokens, split-brain prevention |
| 9. Chaos Testing | 15 | Executed, measured, compared |
| 10. Incident Analysis | 10 | Depth, distributed systems lens |

**Total**: 140 points