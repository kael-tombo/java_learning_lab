# Quiz: ConcurrentLinkedQueue

## Q1. What are the two linearization points?

**A.** `offer`: `NEXT.compareAndSet(p, null, newNode)` (element joins).
`poll`: `p.casItem(item, null)` (element leaves). All FIFO reasoning
reduces to ordering these CAS events.

## Q2. Why may tail lag behind head?

**A.** Both are hints — correctness lives in `next` links. Offer walks
from tail to the true end regardless; the source notes tail-behind-head
is possible and harmless.

## Q3. What does `p == q` mean, and what does the walker do?

**A.** Node self-linked (`next` points at itself) = dequeued garbage.
Walker abandons the chain and restarts from `head`
(`continue restartFromHead`).

## Q4. Why is `size()` O(n), and why is it stale?

**A.** It walks the chain counting live items; concurrent offers/polls
during the walk shift the truth by up to ±rate×walktime. Correct for some
instant mid-walk, never necessarily return time.

## Q5. Why does `offer(null)` throw NPE?

**A.** Null `item` is the dequeued/dummy sentinel — allowing null values
would corrupt the protocol (a live null reads as dead).

## Q6. How is the no-ABA argument made?

**A.** No state reuse: `next` goes null → node → self (never back to
null); `item` goes value → null one way. Nothing returns to a previous
value, so no CAS can be fooled by ABA.

## Q7. Lock-free vs wait-free — which is CLQ, and what does it promise?

**A.** Lock-free: some thread always progresses (CAS loser implies a
winner). Not wait-free: an individual thread can starve retrying.
