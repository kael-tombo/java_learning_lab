# Distributed Failure Detection - Mini Project

## Project: Three Detectors, One Fault Injector

### Objective
Implement three failure detectors against a simulated cluster, inject faults of known
duration, and measure each detector's false-positive rate and detection latency.

### Requirements
1. `TimeoutFailureDetector` — fixed threshold
2. `EwmaFailureDetector` — exponentially weighted moving average of heartbeat arrival
3. `PhiAccrualFailureDetector` — probability from a sliding window of heartbeat intervals
4. `FaultInjector` — hard kill, GC pause, high latency, and network drop
5. `DetectorBenchmark` producing a per-fault latency/false-positive table

### Steps

**Step 1: Timeout — the baseline everyone ships**
```java
boolean isAlive() { return (now - lastHeartbeat) < thresholdMs; }
```
Simple, and wrong for any system with variable latency. Measure it: inject a 400ms GC pause
into a cluster whose threshold is 200ms and count the false positives.

**Step 2: EWMA — adapts to recent history**
```java
void onHeartbeat() {
    long delta = now - last;
    double alpha = elapsed > minInterval ? 1.0 : (elapsed > minInterval / 2 ? 0.5 : 0.1);
    estimate = alpha * delta + (1 - alpha) * estimate;     // slow to adapt, stable
    last = now;
}
boolean suspect() { return estimate > meanThreshold * estimate; }
```
EWMA reacts slowly and deliberately. It will not fire on a single spike, which is the point —
but it also detects a genuine failure later than a timeout would. Measure both effects.

**Step 3: Phi-accrual — a probability, not a flag**
```java
void onHeartbeat(long now) {
    long delta = now - last;
    intervals.add(now, delta);
    last = now;
}
double phi() {
    long t = now - last;
    if (intervals.mean() == 0) return 0;
    double p = t / intervals.mean();
    return p <= 1 ? p : 1 + Math.log(p);       // the +log(p) tail is what makes it useful
}
boolean suspect() { return phi() > threshold; }   // e.g. 3 => "≈ 1 in 1000 chance of error"
```
Cassandra and HashiCorp Consul both use this. It degrades gracefully: instead of a binary
verdict you get "I am 99.9% sure this node is dead", which a load balancer can act on
proportionally.

**Step 4: Inject four faults and record the truth**
| Fault | Duration | Ground truth |
|---|---|---|
| Hard kill | permanent | dead at t=0 |
| GC pause | 400ms | alive, unresponsive |
| Added latency | +300ms sustained | alive, slow |
| Network drop | 20s | alive, partitioned |

```java
record Result(String detector, String fault, long detectedAfterMs,
              boolean correct, double falsePositiveRate) {}
```
1. Run each detector against each fault, 50 iterations
2. Record detection latency for true positives
3. Record false-positive rate when the node was alive but slow
4. Plot false positive against detection latency per detector — the ROC-like curve

**Step 5: Choose from a cost model, not intuition**
```java
record Cost(double failoverCost, double falsePositiveCost, double missedFailureCost) {}
Cost model = new Cost(500, 100_000, 900_000);   // 10 min of downtime
```
A missed failure costs 900k, so accept false positives and set phi at 2, not 5. Write the
arithmetic down — that is the deliverable, the threshold is a consequence.

**Step 6: Separate detection from action**
```java
record Health(SUSPECTED, CONFIRMED, HEALTHY) {}
// detector emits SUSPECTED; a policy layer decides CONFIRMED
```
Suspected: probe it, stop sending new work. Confirmed: evict and fail over. Two-stage
detection cuts false positives because the confirmation step is cheap and independent.

### Deliverables
1. Three detectors behind a `FailureDetector` interface
2. `FaultInjector` for the four fault modes with ground-truth timings
3. Benchmark results: detection latency and false-positive rate per detector per fault
4. A threshold choice with the cost arithmetic shown, plus the two-stage policy

### Extension (CHALLENGE)
Implement phi-accrual with a heartbeat *distribution* rather than a mean, and show the
detection improves when interval variance is high but the mean is misleading.

### Estimated Time
3 hours