# VISION — On-Call Excellence for Deadlocks

## 1. Future State
Deadlocks never hide as "mystery slowness". Dumps auto-capture when pools saturate, the cycle is diagrammed in the alert, and fixes ship as lock-ordering rules enforced by tests — not heroics at 2 a.m.

## 2. What Good Looks Like
- `jvm_threads_deadlocked` alert pages with attached `Thread.print` excerpt.
- Every lock has a documented order; PRs adding `synchronized` nesting require ordering justification.
- Health probes run on isolated threads so stuck workers can't fake healthy.

## 3. Behaviors
Capture-before-restart discipline, draw-the-cycle habit, blameless focus on ordering design rather than "unlucky timing".

## 4. Anti-Vision
Restart-and-hope, "add more threads", single dumps that prove nothing, silent retries that turn deadlock into livelock storms.

## 5. Commitment
This week: add deadlocked-thread alert + 3-dump runbook link. Next: audit one service for nested locks and add an inversion soak test.

> Excellence = make the cycle visible, break it by order, defend with timeouts.
