# Mental Models: Atomic Classes

## 1. One instruction is the ballot box
Each RMW commits in a single `lock cmpxchg`: the hardware compares and swaps atomically, so the winner linearizes there and losers simply retry. No monitor, no park, no BLOCKED — just another lap around the loop.

## 2. The loop is optimistic: assume solo, repair on collision
Read `prev`, compute `next`, CAS. Uncontended, one lap (~10-20ns on x86). Contended, laps multiply and burn CPU while guaranteeing only that *some* thread wins each round. Throughput under contention is a retry budget, not a queue.

## 3. Update functions are rehearsals, not performances
`getAndUpdate(f)` may run `f` several times (about 3x observed under contention in this lab's dive) because `f` executes outside the CAS. A function with side effects performs them repeatedly — keep `f` pure arithmetic.

## 4. ABA is the swapped twin
CAS compares values, not histories: A->B->A looks untouched. Where node identity matters (lock-free stacks), twins corrupt the structure silently. Fresh allocation, stamps, or marks distinguish the twins; bare CAS cannot.

## 5. Striping is many ballot boxes with a fuzzy total
LongAdder hashes writers across cells so each CAS rarely collides; `sum()` then walks base plus cells with no lock, so concurrent updates blur the total. Read it as "some value from during the walk", perfect for metrics, wrong for money.

## 6. Weak CAS is a "try again" coupon, not a verdict
`weakCompareAndSet` may fail spuriously even when the expected value matches, so it belongs only inside retry loops where a false loss costs one lap. One-shot decisions demand plain `compareAndSet`; witnesses (`compareAndExchange`) save a re-read on failure.

## 7. Retries are a lottery where every draw costs a ticket
Each CAS attempt pays full price (read, compute, fence-grade instruction) win or lose; losers pay again. At N writers the mean tickets-per-prize ≈ N — budget the lottery, not the single draw, and stripe when the ticket bill exceeds a cell array.

## 8. Stamps are history you can compare
CAS compares values; stamps compare biographies: A-with-stamp-0 vs A-with-stamp-2 differ even when the letters match. Pay the Pair allocation only where biographies matter (recycled links) — counters have no biography worth buying.

## 9. Striping is a food court, not a bigger kitchen
One kitchen (single word) queues every order; a food court (cells) serves most orders in parallel and totals the registers afterward (`sum()`). The register tape mid-lunch is approximate — exact accounting happens after closing (quiescence).

## 10. Weak CAS is a coupon that sometimes tears itself
`weakCompareAndSet` may fail with the right answer in hand (spurious, real on ARM) — inside a retry loop the torn coupon costs one more lap; as a one-shot verdict it denies a truth. Coupons belong in loops; verdicts demand `compareAndSet`.

## 11. Two atomics are two cash registers, not one safe
Sequential sets on A then B expose the A-done-B-pending moment to every reader — no refund policy (rollback) exists. Multi-field invariants need one safe (lock) or one bill (packed single-word CAS), never two registers and hope.

## Drill
- Price one increment three ways (uncontended CAS, N-writer loop, striped cell) in laps-per-commit before touching JMH.
- Narrate the Treiber ABA schedule (pop-A, pop-B, push-A, stale-CAS) with finger-counted stamps, then show the rejection.
- Sort update functions into pure vs effectful by reading three `getAndUpdate` lambdas; move each effect after the commit line.
- Defend the counter pick (AtomicLong vs LongAdder vs locked total) for metrics, sequence numbers, and billing — three shapes, three answers.
- Recite the weak-CAS rule as a gate: loops welcome weak, verdicts demand plain — say which platform punishes confusion (ARM/LL-SC) and why x86 hides it.
- State the Pair-allocation price of stamps before proposing them on any hot path — correctness first, allocation pressure second.
