# Lab 01: EBS Architecture — Math Foundation

## 1. Utilisation and Headroom

Utilisation is the fraction of capacity in use.

```
U = used / capacity
Headroom = 1 - U
```

| Tier | Used | Capacity | U | Headroom |
|------|------|----------|---|----------|
| App tier | 100 | 100 | 1.00 | **0.00** |
| Database | 60 | 100 | 0.60 | 0.40 |

**Rule of thumb**: at U = 1.00 the system has zero absorption capacity. Any
new arrival cannot begin immediately; it must wait for a release. This is the
definition of saturation, and it is why latency rises non-linearly near 100%.

Queueing theory puts the practical threshold around **70–80%** for interactive
workloads, because service time variance means queues grow sharply before
capacity appears exhausted.

## 2. Little's Law

The central relationship for any queue:

```
L = λ × W
```

Where `L` = average number of items in the system, `λ` = arrival rate,
`W` = average time in the system.

**Worked example** — month-end before remediation:
- Requests arriving: λ = 12 per minute
- Average time in system: W = 15 minutes
- Therefore: L = 12 × 15 = **180 requests outstanding**

**After** specialisation and node cloning:
- λ unchanged at 12 per minute (arrival rate is demand, not capacity)
- W falls to 2.5 minutes
- L = 12 × 2.5 = **30 requests outstanding**

**Key insight**: adding capacity does not reduce λ. It reduces W, and L falls as
a consequence. Anyone claiming the fix "reduced the number of requests" has
misread the system — the queue length fell because throughput rose.

## 3. Utilisation Multiplier

Response time scales roughly as `1 / (1 - U)` under an M/M/1 model:

| U | Multiplier | Interpretation |
|---|-----------|----------------|
| 0.50 | 2.0× | Comfortable |
| 0.70 | 3.3× | Degrading |
| 0.80 | 5.0× | Unacceptable for interactive |
| 0.90 | 10× | Collapse territory |
| 0.95 | 20× | Queue explodes |

At U = 0.90, a request taking 1 second at U = 0.50 takes about 10 seconds.
This is why the same system can feel fine on Tuesday and unusable on the last
day of the month — utilisation crosses the threshold rather than degrading
gently.

## 4. Effective Capacity under Contention

When `n` workers contend on one lock, only one holds it at a time:

```
Effective throughput ≤ 1 / (lock hold time + acquire overhead)
```

With `n` spinning workers:

```
Wasted CPU fraction ≈ (n-1) / n
```

| Workers | Useful work | Wasted |
|---------|-------------|--------|
| 2 | ~50% | 50% |
| 5 | 20% | 80% |
| 20 | 5% | 95% |

**This is the key non-obvious result.** At 20 workers on one lock, 95% of CPU is
spent spinning. Adding more workers makes the CPU number *worse* and throughput
*no better* — exactly the 100%-CPU-with-poor-throughput fingerprint in this lab.

## 5. Capacity Sizing

### Forms processes
```
Processes ≈ Users / 50
```
5,000 users → 100 processes. Distributed by regional share:
US 50% → 50, EMEA 30% → 30, APAC 20% → 20.

### OAF threads
```
Threads ≈ Users / 100
```
5,000 users → 50 threads; scale up ~60% for JVM overhead → ~80.

### Concurrent workers
Size by queue depth, not by CPU. Target: peak wait under 30 minutes.

```
Workers_needed ≈ Peak_arrival_rate × Target_W / 60
```
If 12 requests/min must clear in 2.5 min on average → 30 workers.

## 6. Time Zone Conversion

Shifts must be defined in **database time zone**, not local:

```
EST_offset = UTC-5
CET_offset = UTC+1  → 6h ahead of EST
SGT_offset = UTC+8  → 13h ahead of EST

EMEA 08:00-18:00 CET  →  02:00-12:00 EST
APAC 08:00-18:00 SGT  →  19:00-05:00 EST (wraps midnight)
```

Getting this wrong shifts your capacity to exactly the wrong hours — the system
looks fine during the day and fails at 3am.

## 7. Improvement Measurement

For the before/after comparison, report the ratio rather than raw deltas:

```
Improvement = Before / After

Wait time:  180 / 30 = 6.0× improvement
Completion: 4.00× / 1.00× = 4.0× improvement
```

Ratios stay meaningful across different scales. Absolute minutes do not compare
between two different systems, but a 6× improvement does.

## 8. Cost of the Fix

Adding a node has a real cost; quantify it so the recommendation is honest:

```
Node cost = Hardware + OS + Patching + Monitoring + Failure domain
```

Per-node fixed cost is paid 3× for the cluster. The benefit must exceed not just
the hardware line but the operational overhead too. If the fix reduces month-end
by 3 days of analyst overtime, that is the number to compare against.