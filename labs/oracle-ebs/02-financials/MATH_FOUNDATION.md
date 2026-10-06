# Lab 02: Financials (GL + Subledger with Reconciliation) — Math Foundation

## 1. The Balancing Identity

Every journal entry must satisfy, exactly, in every currency:

```
Σ debits  =  Σ credits          (per journal, per ledger, per currency)
```

```
Journal: standard invoice, USD, 2 lines
  Debit  6110 Expense - Travel      1,250.00
  Credit 2110 Accounts Payable      1,250.00
  ΣD = 1,250.00    ΣC = 1,250.00    Difference = 0.00   ✓
```

### Floating Point Is Not Accounting

```
0.1 + 0.2 = 0.30000000000000004   (IEEE 754 binary floating point)
0.1 + 0.2 = 0.3                   (NUMBER(12,2) in Oracle)
```

```
A 3-line journal with a per-line rounding distribution:
  Total: 100.00 split across 3 lines of 33.333...
  Line 1: 33.33
  Line 2: 33.33
  Line 3: 33.33
  Σ = 99.99   ← off by 0.01

  Correct: the LAST line absorbs the residual
  Line 3: 100.00 − 33.33 − 33.33 = 33.34
  Σ = 100.00  ✓
```

**Any allocation routine that does not put the residual on a final line will
produce unbalanced journals.** This is the single most common source of
"batch failed: unbalanced" errors.

```sql
-- Enforce it in the API, not by review
IF l_debit_total != l_credit_total THEN
   RAISE_APPLICATION_ERROR(-20001,
      'Unbalanced journal: debits '||TO_CHAR(l_debit_total,'FM999999990.00')||
      ' vs credits '||TO_CHAR(l_credit_total,'FM999999990.00'));
END IF;
```

## 2. Currency Conversion Mathematics

```
Transaction currency:  EUR
Reporting currency:    USD

Invoice:  EUR 10,000.00
Rate type: Spot Daily, rate date = invoice date
Rate:     1.0850 USD per EUR

Functional (reporting) amount = transaction × rate
  10,000.00 × 1.0850 = USD 10,850.00
```

### Which rate applies to which amount

```
Amount types and their rate source:
  Transaction amount:  the original EUR figure        (no conversion)
  Functional amount:   converted for reporting        (rate type + date)
  Balancing amount:    functional, derived, never entered
  Reporting amount:    presentation in the ledger currency (usually == functional)
```

```
Reversal (credit memo):
  Original invoice rate:        1.0850  (stored on the original)
  Reversal rate:                MUST equal 1.0850

  If today's rate is 1.0920 and the reversal converts at today's rate:
    Reversal: −10,000 × 1.0920 = −10,920.00
    Original: +10,000 × 1.0850 = +10,850.00
    Net effect on the ledger: −70.00   ← phantom variance in the account
```

**A reversal that does not use the original rate creates a real balance
difference that no reconciliation will ever explain.** This is why rate
information is stored on the source transaction, not looked up at reversal time.

## 3. Three-Way Reconciliation

```
Subledger transaction:  AP Invoice 1,042
  Subledger amount:      USD 12,450.00
  GL impact:             USD 12,450.00

Reconciliation controls:
  1. GL Journal Import (accounting)  → GL batch
  2. GL Transfer to Subledger         → subledger balance
  3. GL Balance                        → GL account balance

Matched on: account, period, currency, amount

Subledger vs GL, AP account, period SEP-26, USD:
  Subledger:     12,450.00
  GL:            12,450.00
  Difference:        0.00  → reconciled
```

```
Unreconciled exposure arithmetic:
  Transactions per month (AP):           42,000
  Late/failed imports (est. 2%):          840
  Average amount:                      $8,400
  Unreconciled value: 840 × 8,400 = $7.06M per period

  With GL reconciliation requirement: 100% within 2 days
  Currently reconciled within 2 days: 96.2%
  Gap: 3.8% = $268K of unreconciled value per period
```

### Three-way match (PO → Receipt → Invoice)

```
PO:        100 units @ $12.00 = $1,200.00
Receipt:    98 units received   = $1,176.00
Invoice:    98 units @ $12.00   = $1,176.00

Match tolerance: 2%
  Value variance: |1,176.00 − 1,200.00| / 1,200.00 = 2.0%
  Exactly at tolerance → matched
  Quantity variance: |98 − 100| / 100 = 2.0% → matched
```

```
The third leg catches what the first two cannot:
  PO and receipt agree, but the invoice is for a different item:
    PO item:   SKU-4471
    Invoice:   SKU-9912
    Amount matches, quantity matches
    WITHOUT the item check → wrong item invoiced, paid, and reconciled clean
```

## 4. SLA (Subledger Accounting) — One Engine, Many Ledgers

```
Business event: a subledger transaction is created
  1. Capture  — writes to subledger tables
  2. Journal  — SLA builds the accounting, one journal line per accounting rule
  3. Transfer — journal import moves it to GL
  4. Summary  — SLA summary, optional, for subledger reporting

Journals per transaction: 1 to 12
  AP standard:       2 lines (accrual + liability)
  AP with tax:       4 lines (accrual, input tax, liability, discount)
  Project billing:  up to 12 (intercompany, project WIP, revenue, AR)
```

```
Journal line count drives batch size:
  AP transactions/month:            42,000
  Average lines per transaction:    2.6
  GL journal lines/month:           109,200

  Manual 2-line journals instead of SLA:
    42,000 × 2 = 84,000 lines but 42,000 separate header/import operations
    SLA: 1 journal with 109,200 lines, imported as one batch

  Import overhead per batch: ~85 ms
  Manual: 42,000 × 85 ms = 3,570 s = 59.5 min of pure import overhead
  SLA:       1 × 85 ms + line processing 109,200 × 0.4 ms = 43.8 s
  Saving: ~56 minutes per period
```

## 5. Journal Line Volume and Batch Sizing

```
GL batch constraints:
  Max lines per journal import request:   configurable, commonly 5,000-10,000
  GL period posting requires:             all lines balanced
  Failure granularity:                    the whole batch

Lines per period (all subledgers):        380,000
```

```
Batch size trade-off:
  Batch = 10,000 lines, 38 batches per period

  Failure impact:
    1,000-line batch, 380 batches:
      A failure loses 1,000 lines of work  -> ~4 min to rebuild
    10,000-line batch, 38 batches:
      A failure loses 10,000 lines of work -> ~40 min to rebuild
    Whole-period batch:
      A failure loses the entire period     -> ~2.7 hours to rebuild
```

```
Batch size from restart tolerance:
  Batch size = total_lines × (restart_tolerance / total_runtime)

  Total runtime: 380,000 lines × 0.4 ms = 152 s = 2.5 min
  Restart tolerance: 60 s
  Batch = 380,000 × (60 / 152) = 150,000 lines

  But the binding constraint is failure blast radius, not restart time:
  A 150,000-line batch that fails takes 2.5 min to rerun and lands in a
  single period. 10,000-line batches give isolated, retryable failures.
  Choose the smaller one: failure isolation wins over restart arithmetic.
```

## 6. Period Close Timing

```
Close task durations (manual vs orchestrated):
  Task                       Manual    Orchestrated   Saving
  Subledger accounting          240 s        240 s        0
  GL journal import            1,800 s      1,800 s       0
  Reconciliation review        9,000 s      3,600 s    5,400 s
  Variance investigation       4,800 s      1,200 s    3,600 s
  Intercompany elimination     2,400 s      1,200 s    1,200 s
  Consolidation prep           3,600 s      1,800 s    1,800 s
                                ------      --------    -------
  Total                        21,840 s    12,840 s    9,000 s
                               (6.1 h)      (3.6 h)     2.5 h
```

```
Close window requirement (all business units, parallel where possible):
  12 business units, close orchestrated in 3 waves of 4:
    Wave duration: 3.6 h  -> total 10.8 h vs 12 × 3.6 = 43.2 h sequential

  Finance close policy: complete within 5 business days
  Current: 9 days.  Orchestrated: 4 days.
```

```
The saving is almost entirely investigation, not processing:
  Investigation: 14,800 s manual -> 4,800 s orchestrated = 67.6% reduction
  Because reconciliation output is ranked by amount, the 3.8% of transactions
  that are 92% of the value get reviewed first.
```

## 7. Prioritised Reconciliation — Ranked by Value

```
Unreconciled transactions in a period: 1,280
Value distribution:
  Top 5% by value (64 txns):   $4.98M  (71% of total variance value)
  Next 15% (192 txns):         $1.72M  (25%)
  Remaining 80% (1,024 txns):  $0.36M  (4%)

Review all 1,280:                     9,000 s
Review by value rank until clean:       2,400 s
```

```
Coverage of the residual risk:
  Full review:      100% of transactions, 100% of value
  Ranked review:    finds 100% of the large discrepancies, misses small ones
  Ranked + tolerance band (auto-accept < $50):  96% of value, 12% of transactions
```

**Auto-accept below a dollar threshold is a policy decision with a number
attached.** State the threshold, state what it implies for residual exposure
(0.36M × 4% ≈ $14K unreviewed), and let the business accept it explicitly.

## 8. Load-Time Performance Profile

```
Subledger accelerator (SLA) load, GL period SEP-26:
  Source transactions:            42,000 AP + 18,000 AR + 9,600 FA = 69,600
  Accounting lines created:                  109,200
  Journal summary balance rows:              380,000

Load phase timing (measured on a 32-core RAC, 2 instances):
  Journal creation:      109,200 × 0.4 ms / 32 = 1,365 s  (22.8 min)
  Summary balance:       380,000 × 0.3 ms / 32 = 3,562 s  (59.4 min)
  Sum:                                                    4,927 s  (82.1 min)
```

```
Ratio that decides whether to parallelise:
  journal_lines / summary_rows = 109,200 / 380,000 = 0.287

Summary generation dominates by 3.5×.
The optimisation target is the summary, not the journal.
```

| Phase | Rows | Time | Share |
|-------|------|------|-------|
| Journal creation | 109,200 | 1,365 s | 28% |
| Summary balances | 380,000 | 3,562 s | 72% |
| Total | 489,200 | 4,927 s | 100% |

## 9. Commit-Time Profile Ratio

```
Commit-to-commit intervals during a GL load on RAC:
  Intervals measured:                1,842
  Total load time:                 4,927 s
  Mean interval:                 4,927 / 1,842 = 2.68 s

  Distribution:
    p50:  0.9 s
    p90:  7.4 s
    p99: 48.2 s
    max: 312 s  (checkpoint / log switch)
```

```
The p99/max to p50 ratio is the diagnostic:
  48.2 / 0.9 = 53.6×     <- 97% of elapsed time is in the tail

Interpretation: throughput is fine; individual transactions stall.
Causes, in order of likelihood:
  1. Log switches (redo log sized for the load)
  2. Checkpoint storms during summary balance generation
  3. Contention on the summary balance table from concurrent loads
```

```
Redo sizing from the load profile:
  Peak redo generation: 34 MB/s sustained
  Required log size = peak generation × target_switch_interval
    target 15 minutes = 900 s
    34 MB/s × 900 = 30,600 MB = ~30 GB total across group logs

  Current: 3 × 2 GB = 6 GB
  Switches per hour at 6 GB:  34 MB/s × 3,600 / 2,048 MB = 59.8 switches/hour
  Required at 30 GB (3 × 10 GB): 34 × 3,600 / 10,240 = 12.0 switches/hour

  Switches reduced 5×, and the 312 s stalls disappear with them.
```

## 10. Ad-Hoc Session Sizing

```
Ad-hoc and reporting users:               180
Peak concurrent:                          120
Interactive (drill, form, pivot) queries: 55% of activity
Report queries (long, read-only):         45%

Mean interactive query:   1.8 s
Mean report query:        45 s
```

```
Ad-hoc pool sizing (Little's Law):
  Interactive: 120 × 0.55 × 1.8 s = 119 concurrent
  Report:      120 × 0.45 × 45 s  = 2,430 concurrent

  Total: 2,549 concurrent sessions needed if reports are unbounded.
```

**That number is impossible and the impossibility is the point.** Reports
consuming 2,430 connections for 45 seconds each is what destroys an EBS instance.

```
Control: report concurrency limit
  Max report queries at once:              20
  Report wait queue:                        80 queued
  Wait time at peak:  (2,430 − 20) / (20 / 45 s)
                          = 2,410 / 0.444 per sec = 5,422 s = 90 min

  Ad-hoc pool:  interactive 119 + report 20 = 139
  Reserved from the total pool of 300:    139  (46%)
```

```
Rule of thumb that falls out:
  report_concurrency_limit ≈ 1.5% of peak ad-hoc users for interactive-heavy
  estates; 3-5% when reports are the primary use case.

  The 45-second report is not the problem to optimise first.
  The unbounded queue in front of it is.
```

## 11. Batch Concurrency for Period Close

```
Close workload:
  Subledgers to process:                 6
  Accounts per subledger:              680
  Sequential program runs: 6 × 680 = 4,080 runs
  Mean run time (subledger load):       3.2 s
  Sequential total:           4,080 × 3.2 = 13,056 s = 3.6 hours
```

```
Parallel options and their formulas:

  Option A — parallel by account (recommended, disjoint data):
    Workers:                8
    Runs per worker:        4,080 / 8 = 510
    Wall clock:             510 × 3.2 = 1,632 s = 27.2 min
    Parallelism factor:     13,056 / 1,632 = 8.0×  (linear)

  Option B — parallel by subledger (only 6 units, poor fit):
    Wall clock:             max(680 × 3.2) = 2,176 s = 36.3 min
    Parallelism factor:     6.0×
    Imbalance: longest worker runs 22.9% longer than average
```

```
Option C — parallel by period (illegal):
  Accounts share the same period rows -> concurrent writes to the same
  summary tables. Expect ORA-00001 and ORA-08177.

  Safe worker count:
    workers <= min(usable_cores × 0.7, distinct_accounts)
    32 cores × 0.7 = 22  ->  min(22, 680) = 22
  Use 8-12 for I/O-heavy subledger loads; the DB writer becomes the
  bottleneck well before CPU does.
```

## 12. Financials Before/After

| Measure | Before | After | Change |
|---------|--------|-------|--------|
| Balanced-journal detection | at review | in the API (`RAISE_APPLICATION_ERROR`) | caught at source |
| Residual rounding per 3-line split | $0.01 unbalanced | $0.00 (residual on final line) | exact |
| Reversal rate mismatch | today's rate → $70 phantom variance | original rate → $0 | reconciled |
| Unreconciled value per period | $268K | < $15K (tolerance band) | −94% |
| GL import overhead per period | 59.5 min | 0.8 min | 74× |
| Reconciliation review time | 9,000 s | 2,400 s | 3.75× |
| Close window (12 BUs, 3 waves) | 43.2 h | 10.8 h | 4× |
| Redo log switches per hour at peak | 59.8 | 12.0 | 5× |
| Ad-hoc pool share of total | 2,549 (unbounded) | 139 (capped) | 18× |
| Close parallel wall clock | 3.6 h | 27.2 min | 8× |
| Journal : summary load ratio | 0.287 (3.5× skew) | measured first | target chosen |

The theme: **every financial control in this lab is an assertion about two numbers
being equal.** Debits equal credits, subledger equal GL, position equal
expectation. Build the assertion into the code and the review becomes a
confirmation rather than a discovery.
