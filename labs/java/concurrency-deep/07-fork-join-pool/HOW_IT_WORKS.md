# How Fork-Join Works

## One deque per worker

Each worker owns a double-ended queue. The owner pushes newly forked tasks and
pops work at the **same end (LIFO)** — the freshest (smallest, most
cache-resident) subtask runs first. An idle thief steals from the **opposite
end (FIFO)** — the oldest (largest) chunk, maximizing work per steal and
minimizing steal count.

## The canonical shape

```java
protected Long compute() {
    if (hi - lo <= THRESHOLD) return computeDirectly();
    int mid = (lo + hi) >>> 1;
    SumTask left = new SumTask(a, lo, mid);
    left.fork();                              // queue async
    long right = new SumTask(a, mid, hi).compute(); // run half inline
    return left.join() + right;               // await (+ help) left
}
```

One fork per split (not two — the second half runs in the current worker,
saving a queue op). `join()` on the left first scans the worker's own deque
and helps; only when nothing local remains does it park.

## The three verbs, precisely

- `task.fork()`: inside a worker → push to own deque; outside → shared
  submission queue. Never blocks.
- `task.join()`: await the result; workers execute other pending tasks while
  waiting (helping), then park only if truly empty-handed. Returns the value
  (or throws the task's exception).
- `pool.invoke(task)`: submit from outside + join — the scoped-pool entry.
  `task.invoke()` runs the fork/join path inline.

## Threshold mechanics

`THRESHOLD` bounds task-creation overhead: leaves ≈ `n / THRESHOLD`, total
nodes ≈ `2n / THRESHOLD`. Too small → millions of task objects and queue
churn; too large → fewer tasks than workers and idle cores. Target leaf work
~1–10µs (hundreds to thousands of tasks per worker).

## ManagedBlocker flow

```java
pool.managedBlocker(new ManagedBlocker() {
    public boolean block() throws InterruptedException { socketRead(); return true; }
    public boolean isReleasable() { return finished; }
});
```

While `block()` parks, the pool may add a compensating thread — `getPoolSize()`
rises above `getParallelism()` (the documented signal). Without this, a parked
worker reads as "busy" and effective parallelism drops silently.

## Ordering flag

`asyncMode=false` (default, common pool): local LIFO — fresh subtasks first,
right for divide-and-conquer. `asyncMode=true` (`newWorkStealingPool`):
local FIFO — older tasks first, right for independent event-style submissions.
