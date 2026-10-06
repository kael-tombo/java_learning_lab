# Payment System - REAL WORLD PROJECT

## Project: Marketplace Payments with Multi-Processor Failover

**Time**: 4-6 weeks (team of 5)

**Scenario**: You process payments for a marketplace: 3.4M orders/month,
14,000 merchants, split payments to sellers, and **three card processors** with
different coverage, fees, and failure characteristics. Requirements:

- Funds must never be lost or duplicated.
- Regulatory audit: reconstruct any balance at any timestamp, on demand.
- Peak: 18 txns/s normal, 300 txns/s during a 20-minute flash sale.
- Merchant settlement in 14 currencies with tiered fee schedules.
- Two of the three processors have a recurring 20-minute weekly maintenance
  window during which they return partial failures.

### Step 1: The Invariant, Stated and Machine-Checked

```
INVARIANT: for every account A and version v,
           balance(A, v) == sum(entries(A) with seq <= v)
AND        sum(all balances) == sum(all entries)              -- nothing created
AND        sum(processor_settled) + sum(in_flight) == sum(entries)   -- nothing lost
```

Implement the verifier to run **continuously**, not nightly, and export it as
the artefact the auditor receives. Deliverable: a tool that takes a timestamp
and an account and returns the reconstructed balance with its full entry trail.

### Step 2: Multi-Processor Routing and the Partial-Failure Problem

Route by merchant preference, card scheme, geography, and cost. Then handle the
hard case: **a processor that partially succeeded**.

```
Processor A: 92% success, 6% soft-fail (timeout, unknown), 2% hard-fail
Processor B: 99.4% success (best), 2% pricing, limited coverage
Processor C: 88% success, cheapest, new entrant

Routing rule: preference first, fallback on SOFT-FAIL ONLY.
  NEVER fall back on unknown-outcome responses without reconciling first --
  the first processor may have charged.
```

The 6% soft-fail band is the entire difficulty of this project. Design:

```
soft-fail -> query processor BY REFERENCE (never re-send)
          -> CONFIRMED   -> record the capture, do not fall back
          -> ABSENT      -> safe to fall back to processor B
          -> UNKNOWN     -> stay in-flight, do not fall back, escalate by age
```

**Required:** a `soft_fail_rate` table for all three processors, and the policy
of "reconcile before fallback" written down and enforced in code. Show that a
naive fallback-on-error implementation produces duplicate charges at
`0.06 x fallback_rate` of soft failures.

### Step 3: Split Payments to Sellers

Marketplace order: customer pays once; funds split across up to 8 sellers,
minus platform fee, minus payment processing fee, minus per-seller fee.

Implement exact remainder distribution (`SplitCalculator` semantics) and prove:

```
  sum(seller_amounts) + platform_fee + processing_fee == gross
```

Required tests:
- 1M random `(gross, seller_count, fee_schedule)` cases. Assert the identity
  holds in every case and no cent is created or destroyed.
- A single seller whose share rounds to 0 must be handled explicitly (suppress
  the payout, accrue it) — not silently skipped.
- Platform fee tiers change mid-month. Assert splits computed across a tier
  boundary conserve money.
- Batch settlement: assert `sum(daily settlement lines) == gross - all fees`.

### Step 4: Idempotency Across Every Caller

Key derivation agreed in a written spec with all internal callers:

```
idempotency_key = merchant_id : checkout_order_id : operation
```

Enforcement at four layers, each with a distinct purpose:

| Layer | Mechanism | Failure it prevents |
|-------|-----------|---------------------|
| Edge API | Fingerprint check on key reuse | Conflicting replay (409) |
| Checkout service | Redis SETNX fast path | Duplicate DB load |
| Ledger | `UNIQUE` constraint | **The actual guarantee** |
| Processor | Stable reference field | Duplicate at the PSP |

**Required test:** fire the same `checkout_order_id` 200 times concurrently
across all three processors. Assert exactly one capture, everywhere, and that
every caller gets an identical response body. Also assert: key reuse with a
different amount returns 409 and executes nothing.

### Step 5: Reconciliation as a First-Class System

```
Every 5 minutes:
  1. Find all payments in non-terminal states older than 60 s.
  2. Group by processor; rate-limit queries per processor (and PAUSE entirely
     during a known processor incident -- otherwise you emit thousands of
     phantom corrections at the worst possible moment).
  3. Query by reference. Classify: WE_MISSED / THEY_MISSED / IN_FLIGHT /
     STUCK / MISMATCHED.
  4. Emit a correction event for WE_MISSED and MISMATCHED.
  5. Re-drive only ABSENT-and-safe cases. Never re-drive UNKNOWN.
  6. Emit metrics per classification; page on WE_MISSED > 0.
  7. STUCK beyond 24 h -> page a human with the full timeline.
```

**Deliverable:** the classification queue sized from the arithmetic in
`MATH_FOUNDATION.md`, staffed for the projected daily volume, with the
per-processor query rate limit documented.

### Step 6: Ghost Holds and Authorisation Lifecycle

Track `ghost_hold_count` as a first-class metric:

```
  15% of authorisations abandoned
  200k authorisations/day outstanding
  -> 30,000 ghost holds/day freezing customer funds for up to 7 days
```

Implement:

- Auto-void on authorisation expiry (not a background batch — a hook at the
  expiry boundary).
- Partial capture with automatic release of the remainder.
- Customer-visible "pending hold" with an expiry timestamp.
- Daily report of ghost holds prevented vs. leaked.

**Required:** a drill that forces a 7-day expiry and verifies the void happens
within 5 minutes of expiry.

### Step 7: Settlement, FX, and Reconciliation of Reconciliation

- Fix the FX rate at capture, disclose the policy. Write the disclosure into
  the merchant contract summary.
- Tiered fee schedules applied per period, with the tier boundary asserted to
  conserve money.
- Daily settlement files matched against processor reports to the cent.
- Variance above 0.01% automatically opens an investigation.

**Deliverable:** a month-end close runbook with the variance checks and named
owners.

### Step 8: Failure Drills (the real deliverable)

1. **Processor A returns partial failures for 30 minutes.** Verify no
   duplicate captures, reconciliation classifies correctly, and settlement is
   unaffected. Report the classification distribution.
2. **Kill the service between processor success and ledger write.** Verify
   reconciliation recovers it and no customer is charged twice on checkout
   retry. (This is the incident from lab 07; here it is production.)
3. **Processor outage during flash sale (300 txns/s).** Verify routing degrades
   to the healthy processor, that the soft-fail band does not cause fallback
   storms, and that pending-age p99 is alerted before customers notice.
4. **Redis (idempotency fast path) down.** Verify the ledger `UNIQUE`
   constraint still prevents duplicates. This drill justifies layer 3.
5. **Clock skew of 3 s on one node.** Verify no ordering or expiry logic
   depends on wall clock (auth expiry, settlement windows, reconciliation
   age). Assert `STUCK` classification is unaffected.
6. **Split payment fails on leg 3 of 5.** Verify partial state is visible,
   reconciliation compensates the completed legs, and money is conserved.

### Deliverables

1. Stated invariant with a continuous verifier and an on-demand historical
   balance reconstruction tool.
2. Multi-processor routing with a soft-failure policy (reconcile before
   fallback), enforced in code, with the duplicate-rate arithmetic.
3. Split payment engine with 1M-case money-conservation property tests.
4. Four-layer idempotency with the 200-way concurrent test and the
   conflicting-replay test.
5. Reconciliation system with classification metrics, query rate limits,
   incident-pause behaviour, and a staffed queue projection.
6. Ghost-hold elimination with the 7-day expiry drill.
7. Settlement, FX, and month-end close with variance checks and owners.
8. Six drill reports with measured numbers and timelines.
9. Metrics: capture success/fail by processor, soft-fail rate, pending-age
   p99, reconciliation queue depth by class, invariant violations, ghost holds,
   settlement variance, dedup replays, duplicate rejects.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Soft failures | Fall back on any error | Reconcile by reference before fallback; duplicate math shown |
| Idempotency | App-level check | Four layers; 200-way concurrent test; conflict test |
| Splits | `total / n` | Remainder distribution + 1M-case conservation proof |
| Reconciliation | Nightly script | 5-minute cycles, incident pause, staffed queue, paged |
| Audit | "We have logs" | On-demand historical balance with entry trail |
| Ghost holds | Periodic cleanup | Expiry-boundary hook with a 7-day drill |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 9110 — *HTTP Semantics*: normative definitions of `402 Payment Required`,
  `409 Conflict` (the correct response for an idempotency-key replay with a
  different body), `412`, and `429`. Cite the section when designing the payment
  API's error contract.
  https://www.rfc-editor.org/rfc/rfc9110.html
- AWS Well-Architected Framework — Reliability and Operational Excellence
  pillars: change management, failure management, and the workload-recovery
  guidance this project applies to processor failover and reconciliation
  design.
  https://aws.amazon.com/architecture/framework/

Both are reference-quality but the AWS pillar guidance is versioned and
periodically revised. Pin the version you read, and treat all processor-specific
behaviour (soft-fail semantics, reference-field idempotency windows, reversal
timelines) as something you must confirm in writing with each PSP rather than
infer from general documentation.