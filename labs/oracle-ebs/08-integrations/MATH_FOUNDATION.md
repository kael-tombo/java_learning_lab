# Lab 08: Integrations — Math Foundation

## 1. Manual vs Automated — The Business Case

Current state: manual double entry, 2-day quote delay, 15% error rate.

### Latency comparison

```
Manual:
  Rep closes opportunity    day 0
  Data entry to EBS        day 2  (batched, once daily)
  EBS quotes                day 2
  Total latency:            ~48 hours

Automated:
  Opportunity saved         t=0
  Event published           t+1s
  Consumer picks up         t+30s (scheduler interval)
  Quote created             t+75s (API + validation)
  Status pushed to SF       t+80s
  Total latency:            ~80 seconds
```

```
Improvement: 48 hours → 80 seconds = 2,160×
```

### Error rate impact

```
Manual:   15% error rate
Automated with validation + idempotency: ~1%  (residual data errors only)

Daily orders: 60
Manual errors:      60 × 15% = 9 orders/day wrong
Automated errors:   60 ×  1% = 0.6 orders/day
```

At $8,400 average order value and a $280 cost to detect and correct one error:

```
Manual:    9 × $280 = $2,520/day   →  $630,000/year
Automated: 0.6 × $280 = $168/day   →   $42,000/year
Annual saving: ~$588,000
```

**$588K/year in error correction alone**, against an integration cost measured in
weeks. That is the business case; latency is the headline, error cost is what
funds it.

## 2. Idempotency — Quantifying the Duplicate Risk

Ambiguity arises whenever a response is lost:

```
P(response lost) ≈ P(network failure during return path)
```

Assume 1 in 200 calls experiences it:

```
P(ambiguous outcome) = 0.005
```

Naive retry-on-timeout policy:

```
Client times out at 30s
Client retries
Server had already created the order

Duplicate rate = 0.005 per timeout × retry-always-on-timeout
               = 0.5% of orders duplicated
```

At 60 orders/day:

```
0.5% × 60 = 0.3 duplicates/day = ~110 duplicates/year
```

Cost per duplicate (cancellation, customer credit, sales effort):

```
~$1,200 per duplicate
110 × $1,200 = $132,000/year
```

**With idempotency keyed on the Salesforce Opportunity ID, duplicates = 0.**
The check is one primary-key insert; the saving is $132K/year.

### Detection of changed payloads

A client may resend with corrections:

```
Same external_id, different payload_hash
```

The idempotency record stores `payload_hash`. On mismatch:

```
Same ID + same hash    → replay the stored result
Same ID + different hash → flag for review; do NOT silently update
```

Silently updating an order after it has been transmitted downstream creates a
downstream inconsistency that is very hard to trace.

## 3. Retry Math — Why Bounds Are Mandatory

### Unbounded retry failure mode

```
Retry every 30 seconds, forever:
  Attempt count after 24 hours: 2,880
  Load on the failing service:   2,880 requests/day per stuck message
  DLQ entries:                   never created
  Operator visibility:           none — it just "keeps trying"
```

This is a denial-of-service pattern applied to your own dependency. Bounded
attempts with a terminal state is not optional.

### Bounded backoff schedule

```
Base delay = 2s, max 5 attempts

Attempt 1: t=0
Attempt 2: t=2s      (+2)
Attempt 3: t=6s      (+4)
Attempt 4: t=14s     (+8)
Attempt 5: t=30s     (+16)
Attempt 6: give up → DLQ at t=30s
```

Total elapsed before DLQ: **30 seconds**.

### Impact of backoff on the failing service

| Policy | Requests per stuck message/hour |
|--------|---------------------------------|
| Immediate retry | 3,600 |
| Fixed 5s delay | 720 |
| Exponential (base 2s) | ~120 average |
| Bounded (5 attempts) | 6 total, then 0 |

Bounded exponential backoff is the difference between a dependency being knocked
over and staying up while it recovers.

### Recovery time advantage

A dependency with a 3-minute transient outage:

```
Immediate retry:  message succeeds at t=180s (attempt ~180)
Bounded 5:        message moved to DLQ at t=30s, needs manual replay
```

Immediate retry recovers automatically but hammers throughout. Bounded fails to
auto-recover. **This is why transient-recovery retries and terminal retries are
different mechanisms:**

```
Transient retry:  more attempts, longer horizon, service-protection backoff
Terminal retry:   few attempts, then DLQ for a human
```

## 4. Error Classification — The Cost of Retrying Wrong Things

Classification accuracy determines whether retry helps or hurts.

```
Volume: 100,000 messages/year
Classification accuracy: 98%
```

```
Correctly classified: 98,000
Misclassified:            2,000
```

### Misclassification scenarios

| Actually | Classified as | Consequence |
|----------|--------------|-------------|
| TERMINAL | RETRYABLE | Wasted attempts, delayed DLQ entry, cost |
| RETRYABLE | TERMINAL | **Premature DLQ; message never auto-processes** |

The second is worse. A transient failure misclassified as terminal means manual
intervention for something the system could have handled.

```
Misclassified RETRYABLE as TERMINAL: 1,000 messages/year
Manual triage cost: 15 min each = 250 hours/year
```

**Classification rules should be explicit and reviewed, not guessed per call.**
Defaults matter: unknown errors should be TERMINAL (safer — it surfaces to a human
rather than looping).

## 5. Throughput and Capacity

```
Opportunities per day:       400
Peak hour (25% of volume):   100
Message processing time:     2s average
Required workers = (100 × 2s) / 3600s = 0.056 workers
```

**Concurrency needed: less than one.** This integration is nowhere near capacity
with any reasonable configuration.

Add downstream volume:

| Flow | Volume/day |
|------|-----------|
| Opportunity → Quote | 400 |
| Quote → Order | 350 |
| Order status → SF | 1,500 (multiple status changes each) |
| Shipment → SF | 350 |
| **Total** | **2,600** |

Even at 10× growth:

```
26,000/day = 1.08/second average
Peak: 2.7/second
Worker requirement: negligible
```

**Capacity planning for this integration is not the constraint.** Reliability and
correctness are. Say so explicitly rather than over-engineering throughput.

## 6. Event Lag — The Scheduler Interval Tax

Events are processed by a scheduler, not instantly:

```
Scheduler poll interval: 30s
Average lag introduced:   15s
P99 lag:                  ~30s
```

Total end-to-end latency:

```
Event publish:       1s
Scheduler wait:     15s average (0–30s range)
Processing:          2s
Status push:         2s
TOTAL:              20s average, 35s p99
```

### Interval vs latency

| Interval | Avg latency | Requests/day | Trade-off |
|----------|------------|--------------|-----------|
| 10s | 5s | 8,640 | More scheduler load |
| **30s** | **15s** | **2,880** | **Balanced** |
| 60s | 30s | 1,440 | Visible delay to users |
| 300s | 150s | 288 | Users notice |

**60 seconds is the psychological threshold** — beyond it, users believe the
integration is broken. Choose an interval that keeps p99 under it, and make the
UI honest ("quote submitted, generating…") rather than hiding the wait.

## 7. DLQ Depth — Detection Thresholds

```
Daily volume: 2,600 messages
```

| DLQ/day | % of volume | Assessment |
|---------|------------|------------|
| 0 | 0% | Healthy |
| 2 | 0.08% | Normal transient failures |
| 10 | 0.4% | Investigate this week |
| 40 | 1.5% | Integration degraded |
| 200 | 7.7% | **Broken — halt manual workaround** |

**Set the alert at 10/day.** Below that, noise. Above that, every day of delay
compounds the manual backlog.

### DLQ age matters more than depth

```
10 messages, all from today:        manageable
10 messages, some 3 weeks old:       systematic failure being ignored
```

Alert on both depth and **age of the oldest entry**. Old DLQ entries mean nobody
is triaging, which means the DLQ is a graveyard rather than a recovery mechanism.

## 8. Volume Agreement — Catching Silent Drops

Error rate monitoring has a blind spot: **messages that vanish**.

```
Opportunities created in SF:      400
Orders successfully created:       400
Error rate:                        0%     ← looks perfect

Opportunities created in SF:      400
Orders successfully created:       396
Error rate:                        0%     ← STILL looks perfect
Unexplained gap:                    4      ← the real signal
```

**Four opportunities were never processed and no error was ever recorded.** The
only way to detect this is comparing source volume against target volume.

```
Detection sensitivity at various volumes:
  400/day  → 1 message = 0.25%  → detectable
  40/day   → 1 message = 2.5%   → clearly visible
  4/day    → 1 message = 25%    → glaring
```

Volume agreement is the **only** check that catches silent drops, and it is
routinely omitted. Four opportunities a day with no error is the exact failure
that erodes user trust fastest.

## 9. Transformation Coverage

```
Salesforce Account fields:          18
Mapped in XX_FIELD_MAPPING:         16
Unmapped:                            2
Coverage:                           89%
```

Hardcoded alternative — every new field needs a code deployment:

```
Add a field:  code change → test → deploy → regression test
               4 hours, 2 environments

Mapping table:
Add a field:  INSERT INTO xx_field_mapping
               2 minutes, no deployment
```

Over a year with 12 field additions:

```
Hardcoded:  12 × 4 hrs = 48 hours + deployment risk
Table:     12 × 2 min = 24 minutes
```

**Unmapped field behaviour must be explicit.** Silently dropping 2 fields produces
records missing data that nobody notices until a report is wrong.

## 10. End-to-End Latency Budget

Target: quote creation within 60 seconds of opportunity closure.

| Stage | Budget | Actual | Variance |
|-------|--------|--------|----------|
| SF saves opportunity | — | t=0 | — |
| Event published | 1s | 1s | 0 |
| Scheduler wait | 15s | 15s | 0 |
| Fetch from SF REST | 2s | 2.2s | +0.2 |
| Transform | 1s | 0.4s | −0.6 |
| Validate | 1s | 0.3s | −0.7 |
| `OE_ORDER_PUB` call | 5s | 4.1s | −0.9 |
| Idempotency + audit | 1s | 0.2s | −0.8 |
| Status push to SF | 2s | 1.8s | −0.2 |
| **TOTAL** | **28s** | **25s** | **−3s** |

Against the manual baseline of 48 hours, the total budget is irrelevant —
**the integration is not latency-constrained.** Optimising the transform step
would be wasted effort; making it reliable and observable is where the value is.

## 11. Security Exposure

```
Integration OAuth2 client secret leaked
  → attacker can create quotes as the integration user
  → if that user also has broad EBS access, full business compromise
```

Blast radius depends on the integration user's privileges:

| Design | Privileges | Blast radius |
|--------|-----------|--------------|
| Bad: reuse an AP admin | Broad | All AP functions |
| **Good: dedicated integration user** | **Quote create only** | **Quote creation only** |

```
Least-privilege value: limit a credential compromise to one operation
```

Additional exposure to size:

```
Plaintext secret in APPL_TOP:  readable by every OS user on the tier
Credential store / wallet:     readable only by the app tier service account
```

On a shared app tier with 20 admins, plaintext is a 20-way exposure.