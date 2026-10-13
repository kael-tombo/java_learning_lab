# Exercises: JMM Foundations

All exercises run on JDK 9+ with no dependencies. Expected values are
exact: `1499500` (start), `41541750` (join), `2000000` (lock).

## 1. Break the start edge (then restore it)

Move one element write to *after* `t.start()` in `StartEdge`:

```java
t.start();
d.values[0] = -999; // unordered now: no hb covers it
```

Run 20 times. The checksum comparison may still pass (the write often
lands visibly by luck) — explain in hb terms why green proves nothing
and why the program is now racy regardless of output.

## 2. Consume before join

In `JoinEdge`, read `result` and compute the sum *before*
`worker.join()`, then compare with `41541750`. Repeat 20 times and
record how often the sum is short. Then move the read after `join()`
and confirm 20/20 exact. Write one sentence: which hb rule did the
reordering restore?

## 3. Split the lock

In `LockEdge`, guard half the threads with a second lock object
`LOCK2`. Run and record the count shortfall from `2000000`. Then
revert to one lock and confirm exactness 3/3 runs. Explain why two
lock chains cannot compose into one total order (preview of the
release/acquire lesson in lab 02/03).

## 4. Latch vs flag

Replace the `CountDownLatch` in `LatchEdge` with a plain boolean
`ready` spin (`while (!ready) Thread.onSpinWait();`). Run 10 times.
Then restore the latch and confirm `true` 10/10. Deliverable: the hb
chain for the latch version as three links
(write-graph -> countDown -> await-return -> reads).

## 5. Causality probe

Extend `CausalityFloor` to track the minimum and maximum observed
values across 100000 reader samples. Assert `min >= 0` and
`max <= 100000` and `weird == 0`. Run 5 times. Then answer: which
orderings did you observe (repeats? skips? going backward?) and why
does none of that violate JLS 17.4.8?

## 6. Edge-swap challenge

Publish the `StartEdge` 1000-element array using each of the four
edges in turn: start, lock, volatile reference, latch. For each, write
the 3-link hb chain and confirm checksum `1499500` 5/5 runs. Note
which version needed the least code change and which you would ship —
then defend the choice in two sentences (hint: match the edge to the
thread-lifecycle shape, not to taste).

## Done when

You can draw any demo's hb chain from memory, predict which single-line
move breaks it, and explain why a green run of the broken version is
still a race.
