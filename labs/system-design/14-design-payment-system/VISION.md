# Payment System - Vision

## Why This Lab Exists
Payments is where distributed systems mistakes become legal problems. Duplicate
charges, lost authorisations, and unreconciled balances are not bugs — they are
financial incidents with regulators involved. This lab exists because every
general-purpose pattern (eventual consistency, at-least-once delivery, retries)
is correct engineering and *wrong* here until you constrain it explicitly.

## The Mental Model
One invariant dominates everything else:

```
  sum(ledger entries) == balance, for every account, at every version
```

Everything else — idempotency, state machines, reconciliation, outbox — exists
to protect that identity. If you cannot state the invariant in one sentence and
make it machine-checkable, you do not have a payment system, you have a balance
column with race conditions.

## The Three Surfaces With Different Guarantees

| Operation | Guarantee | Why |
|-----------|-----------|-----|
| `AUTHORIZE` | Linearizable, idempotent by merchant reference | Reserves funds; must not double-hold |
| `CAPTURE` | At-most-once capture per authorisation | Capturing twice is a direct charge |
| `REFUND` | At-least-once with idempotent refunds | Under-refunding is worse than double-refunding |
| `SETTLE` | Batch, eventually consistent to the bank | External system, bounded by bank windows |
| `BALANCE` | Read your own writes | Users must never see "less money than I have" |

Note the asymmetry in the third row: duplicates are *safer* than losses for
refunds, and *catastrophic* for captures. A single retry policy does not fit
both.

## Patterns That Are Right and Wrong Here

| Pattern | Verdict | Reason |
|---------|---------|--------|
| Outbox | **Right** | Business write + event must be atomic |
| Saga with compensation | **Right** | Partial states are unavoidable; make them visible |
| 2PC with the processor | **Wrong** | You cannot share a transaction manager with a PSP API |
| Eventually-consistent balance | **Wrong** | Users lose trust immediately |
| Last-write-wins on balance | **Catastrophic** | Silent money loss |
| Reconciler as an afterthought | **Wrong** | It is the primary correctness mechanism |

The last row is the one people learn on the job. Reconciliation is not a safety
net; it is the process by which two independent systems agree.

## What You Should Be able To Do
- Write the balance invariant and implement a machine-checkable verification.
- Design an explicit capture/refund state machine with visible intermediate
  states, and defend each.
- Build layered idempotency (edge, service, ledger constraint, processor
  reference) and explain why each layer exists.
- Write a reconciliation loop that classifies disagreements and handles each
  class, including "genuinely in flight for 24 hours".
- Explain why capture must be at-most-once and refund at-least-once.
- Say what you would do about a processor outage at 03:00 that no one is awake
  for.

## The Anti-Goals
- No mutable balance row updated in place without an entry. The entry is the
  audit trail; the balance is a projection.
- No per-attempt UUID as an idempotency key. That disables deduplication while
  appearing to work in tests.
- Never treat your own state as the truth about your own transaction without
  querying the processor.

## Success Criteria
You can specify a payment system with: the invariant, the state machine with
every visible intermediate state, idempotency key derivation agreed across
callers, the reconciliation classification, the dispute/refund policies, and
the failure playbook for each processor failure mode.

## How To Use This Lab
1. `THEORY.md` for the architecture and flows.
2. `MATH_FOUNDATION.md` for money arithmetic, fees, retries, reconciliation
   rates.
3. `CODE_DEEP_DIVE.md` for the ledger, state machine, idempotency layers.
4. `MINI_PROJECT.md` to build a ledger and inject processor failures.
5. `REAL_WORLD_PROJECT.md` for a production money-movement platform.