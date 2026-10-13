# Reflection: JMM Foundations

## Prompt 1: your thinnest edge

Which of the four guaranteed demos (start 1499500, join 41541750, lock
2000000, latch true) surprised you by needing *so little* mechanism?
Write down the three hb links for that demo from memory, then note
where in your own code you currently pay for a heavier edge (lock,
blocking queue) that this lighter one could replace.

## Prompt 2: a race you shipped

Recall a real visibility bug (stale config, half-built object, flag
spin that hung once). Name the two conflicting accesses and the edge
that was missing. Would the failure have been a stale value, a reorder,
or a hang — and which demo in this lab is its minimal reproduction?

## Prompt 3: determinism vs consistency

In your own words, distinguish "deterministic" from "sequentially
consistent," using `LockEdge` (always 2000000, never the same
interleaving twice) as the exhibit. Why do code reviews that demand
exact thread order always fail, while reviews that demand exact final
state succeed?

## Prompt 4: causality's boundary

`CausalityFloor` sees only values in `[0, 100000]` in arbitrary order.
Describe a consumer for that stream that is *correct* without edges
(e.g., a progress metric taking any value) and one that is *broken*
without edges (e.g., an index into the array). What distinguishes the
two — and how do you classify new consumers at review time?

## Prompt 5: the library-edge habit

List three places in your current project where hand-rolled flags,
sleeps, or double-checked plain reads could become `CountDownLatch`,
`Future.get`, or queue handoff. What stops the swap today (API shape,
legacy code, habit)? What is the first one you will convert, and what
exact oracle (like the latch's four field checks) will prove it?

## Prompt 6: teaching it forward

Explain DRF-implies-SC to a teammate in five sentences using only this
lab's numbers (1499500, 41541750, 2000000, latch true, zero invented
values). If any sentence needs the words "basically" or "just," the
explanation is not ready — rewrite until each sentence names an edge.
