# AWS Serverless - Mini Project

## Project: An Order-Processing Serverless Pipeline

### Objective
Build a real event-driven pipeline — API → queue → processor → downstream notification — with
idempotency, a dead-letter path, and measured cold-start and scaling behaviour.

### Requirements
1. `LambdaSimulator` — cold start, warm reuse, concurrency, timeout, and memory model
2. Idempotent handler with a dedupe store keyed by event ID
3. Partial batch failure handling for stream sources
4. `StateMachineSimulator` — states, retries with backoff, and catch paths
5. Benchmark comparing container and function cold-start distributions

### Steps

**Step 1: Model the invocation honestly**
```java
class LambdaSimulator {
    record Result(int billedMemoryMb, long durationMs, String outcome, boolean coldStart) {}

    Result invoke(Request req, int concurrency) {
        var wasWarm = runtime.containsKey(req.function);
        runtime.putIfAbsent(req.function, new Runtime());      // the container exists or not
        var startOverhead = wasWarm ? 0 : coldStartMsFor(req.memoryMb, req.jvmVariant);
        try {
            var out = handler.handle(req);
            runtime.get(req.function).releaseAfterIdle(Duration.ofMinutes(10));
            return new Result(req.memoryMb, startOverhead + out.durationMs(), "ok", !wasWarm);
        } catch (TimeoutException e) {
            return new Result(req.memoryMb, TIMEOUT_LIMIT, "timeout", !wasWarm);
        }
    }
}
```
Then calibrate the simulator against real measured cold starts before trusting any conclusion
from it. A simulator that does not match reality teaches nothing.

**Step 2: Measure cold starts properly**
```text
Cold start ≈ image pull + runtime init + JVM start + class loading + JIT warmup + handler work
```
| Memory | Cold start (measured) | p50 duration |
|---|---|---|
| 512 MB | ~1.4 s | 60 ms |
| 1024 MB | ~1.0 s | 45 ms |
| 2048 MB | ~0.9 s | 35 ms |

CPU scales with memory, so more memory means faster execution *and* a faster cold start — but
billed at a higher rate. Find the break-even on your own workload: the point where
`memory × duration` stops decreasing.

**Step 3: Idempotency, because the event bus means at-least-once**
```java
public class OrderHandler implements RequestHandler<OrderEvent, Void> {
    private final DedupeStore dedupe;         // DynamoDB conditional put
    private final OrderRepository orders;

    public Void handleRequest(OrderEvent e, Context ctx) {
        if (!dedupe.markProcessing(e.eventId(), ctx.getRemainingTimeInMillis())) {
            return null;                       // already done -- ack quietly
        }
        try {
            orders.save(new Order(e));          // effect committed
            dedupe.markDone(e.eventId());
        } catch (Exception ex) {
            dedupe.release(e.eventId());       // allow a retry to proceed
            throw ex;                          // let the platform retry
        }
        return null;
    }
}
```
The subtlety: if you mark "done" before the effect commits and then crash, the retry is
skipped and the work is lost. Mark processing, do the work, then mark done. Test the crash
between those two points.

**Step 4: Partial batch failure — the one that surprises people**
A batch of 100 records where 3 are poison will retry **all 100** unless you tell the service
which ones succeeded.
```java
// Report per-record success so the service can skip the good ones on retry
return new BatchResponse(failures.stream()
    .map(f -> new BatchItemFailure(f.itemIdentifier()))
    .toList());
```
1. Report only the failures as `BatchItemFailure`
2. The service advances the checkpoint past the rest
3. Send poison records to a DLQ after a bounded number of attempts
4. **Test it**: assert the successful records are processed exactly once across retries

**Step 5: A state machine with the failure paths written down**
```
 CreateOrder
     │ (no catch)                    -- if this throws, the whole execution fails
     ▼
 ReserveStock ──catch──▶ ReleaseReservation ──▶ NotifyCustomer(compensated)
     │ (success)
     ▼
 ChargePayment ──catch(States.ALL)──▶ RefundPayment ──▶ NotifyCustomer(refunded)
     │
     ▼
 CreateShipment ──retry(3, backoff)──▶ NotifyOps ──▶ Succeed
```
1. Decide explicitly, per state, whether a failure retries or terminates the execution
2. `catch` with a compensating action is the SAGA pattern from lab 04, expressed declaratively
3. Bounded retries with backoff; a Step Functions retry without a bound is an infinite bill
4. Test: inject a failure at each state and assert the execution reaches a terminal state

**Step 6: The extension that pays: idempotency everywhere**
Trace one event through API Gateway → queue → function → DynamoDB → EventBridge → email.
For each hop, ask: if this happens twice, what breaks? Any hop you cannot answer is a bug
waiting for the retry that triggers it.

### Deliverables
1. `LambdaSimulator` calibrated against real measured cold starts
2. Idempotent handler with the crash-between-mark-and-commit test
3. Partial batch failure response with a test proving single processing across retries
4. State machine with per-state failure policy and an injected-failure test at each state

### Extension (CHALLENGE)
Compare reserved concurrency against provisioned concurrency: measure p99 latency under a
burst and identify the knee point where provisioned concurrency stops paying for itself.

### Estimated Time
4 hours