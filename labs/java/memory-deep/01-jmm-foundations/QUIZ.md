# Quiz: JMM Foundations

## Q1: Which accesses form a data race?

A program has two threads sharing `int x`. Thread A writes `x = 1`,
thread B reads `x`, with no synchronization between them.

**Answer:** This is a data race: two conflicting accesses (same
variable, one a write) unordered by happens-before. Sequential
consistency is forfeited — the read may see 0, 1, or any stale value,
and no reasoning about "order" applies.

## Q2: What must `StartEdge` print, and which rule forces it?

**Answer:** `expected checksum = 1499500` and `thread observed =
1499500` with `true`. The thread-start rule: `t.start()` hb the child's
first action, and transitivity extends the edge to all 1000
program-ordered prior writes.

## Q3: Main reads worker output before `join()`. Verdict?

**Answer:** Data race — the worker's writes are hb only the `join()`
return, and a pre-join read has no chain to it. Moving the identical
read after `join()` converts the verdict to guaranteed (sum
41541750), with zero code change besides position.

## Q4: 8 threads x 250000 locked increments print 1999999. Possible?

**Answer:** No — if every increment is inside `synchronized (LOCK)` on
one monitor, 2000000 is forced by the unlock->lock chain. Observing
1999999 proves some access escaped the lock (different monitor,
unlocked fast path, or non-atomic reset). The count is an oracle.

## Q5: What does `countDown()` hb, exactly?

**Answer:** The return from `await()` (on the same latch): everything
program-ordered before `countDown()` is visible to everything
program-ordered after the `await()` that observes it. The demo's four
field checks (`url`, `timeout`, two ports) assert the whole graph.

## Q6: Racy reader sees values 7, 7, 3, 99999, 5. Violation?

**Answer:** No causality violation: every value was written (range
0..100000), and repeats, skips, and backward steps are legal without
edges. A value of −1 or 100001 in the same trace *would* violate JLS
17.4.8. Order chaos is allowed; invention is not.

## Q7: Which JSR rewrote the JMM, when, and what changed for DCL?

**Answer:** JSR-133, shipped in Java 5 (2004; Manson/Pugh with Lea's
group, Goetz documenting). It gave volatile real acquire/release-plus-SC
semantics, which made double-checked locking correct *with* a volatile
field (broken without it, before and since).

## Q8: Two threads use *different* locks to guard one counter. Verdict?

**Answer:** Still a race: the monitor rule chains unlock->lock only on
the *same* monitor. Two lock chains never compose into one total order
— the counter loses updates exactly as if unlocked. One shared lock, or
an atomic, or a striped accumulator.
