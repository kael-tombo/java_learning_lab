# Math Foundation: Lock-Free Progress

## Linearization points (the correctness math)

An operation "takes effect" at one atomic step. Offer linearizes at
`NEXT.compareAndSet(p, null, n)` success; poll at `casItem(x, null)`
success. All FIFO reasoning reduces to ordering these two event types in
time: offers sort by link-CAS order, polls consume the earliest linked
live node. If offer₁'s CAS precedes offer₂'s, poll returns 1 before 2.

## Lock-free vs wait-free (progress guarantees)

- Lock-free: in every infinite execution, *some* thread completes
  infinitely often. A CAS loser implies a winner — system progress per
  retry.
- Wait-free: *every* thread completes in bounded steps. CLQ is NOT this —
  a thread can starve retrying under adversarial contention.
- Practical bound: uncontended offer ≈ 1 CAS + walk; contended-k offer ≈
  k extra steps worst case per retry round, with expected retries small
  (contention window is one pointer).

## Slack-2 amortization

Updating tail/head every op = 1 CAS per op on a hot line. Updating only
when ≥ 2 stale ≈ 1 CAS per 2 ops — halves coherence traffic on the
pointer lines. Walk cost rises by ≤ 2 steps (bounded staleness), each a
cheap volatile read. Net: fewer expensive CASes, slightly more cheap reads.

## Size() error bounds

`size()` counts live nodes during a walk of duration T. Concurrent
offer/poll rate r shifts the true size by up to ±r·T during the count —
error is unbounded in theory, ~r·T in practice. Hence "stale on return":
the value was correct for *some* instant during the walk, never
necessarily return time.
