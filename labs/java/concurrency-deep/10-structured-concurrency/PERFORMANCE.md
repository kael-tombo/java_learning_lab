# Performance: Sizing Scopes

## Thread-per-subtask costs

Each fork spends roughly one thread. On virtual threads that cost is
small (heap-allocated stacks, scheduler parking); on platform threads
it is roughly a megabyte of committed stack plus OS scheduling weight.
Size the carrier to the fan-out: virtual by default, platform only for
a handful of long-lived subtasks.

## Virtual threads as the intended carrier

Virtual-thread schedulers park blocked subtasks cheaply, so a fan-out
of hundreds blocked on I/O stays affordable. Platform-thread pools
cap out far earlier under the same shape. The scope API does not pick
the carrier for you — construct subtask threads accordingly and keep
the default virtual unless you have a measured reason.

## Fail-fast shortens tail latency

`ShutdownOnFailure` cancels siblings the instant the first failure
lands, freeing their threads and downstream resources. Against manual
cancel loops the win is the reaction gap: policy shutdown fires on the
completing thread with no owner round-trip, so wasted work after a
failure approaches zero for interruptible subtasks.

## Hedging trades redundancy for latency

`ShutdownOnSuccess` spends N subtasks' work to buy the minimum latency
across replicas. Worth it when replicas are cheap and tails hurt
(slow-backend hedging); wasteful when every subtask is expensive and
success times barely vary. Measure the latency spread before hedging.

## joinUntil bounds worst-case waits

A deadline converts unbounded tail waits into a fixed budget plus
`TimeoutException` handling. Set it from service budgets (e.g. caller
SLA minus margin), not from average subtask time — the deadline guards
the tail, and `close()` still reaps whatever was cut off.

## Interruption responsiveness dominates

An interruptible subtask frees its thread within microseconds of
`shutdown()`; an interrupt-ignoring loop holds it until `close()`
drags it out. Cancellation latency is a subtask property, not a scope
property — profile the subtask's poll interval, not the scope.

## Nesting overhead is one scope per level

Each nesting level adds one scope object plus its latch — negligible
against subtask work. Depth costs stack frames in recursive shapes
(lab 07's divide-and-conquer), not scope machinery. Keep splitting
while leaves hold real work; stop when the leaf body is cheaper than a
fork.

## Custom handleComplete must stay cheap

The hook runs on completing subtask threads that race each other, so
keep it to counting and flagging under appropriate synchronization. A
slow or contended override serializes completions and stretches join
latency — record-and-shutdown, never compute, inside the callback.

## What to measure in this lab

Block latency (fork-to-close), cancellation gap (decisive completion to
sibling interrupt), thread count and carrier during fan-out, and wasted
work after first failure/success. Four numbers tell you whether the
scope shape pays for itself against the `invokeAll` baseline.
