# Mental Models: Lock-Free Queue

## 1. Two CASes are the queue; the rest is hints

`NEXT.compareAndSet` (offer) and `casItem` (poll) define membership. Head,
tail, walks, hops — all optimization around those two atomic sentences.
Reason about interleavings at the CASes, nowhere else.

## 2. Staleness is a budget, not a bug

Slack-2 spends up to two steps of pointer staleness to buy halved CAS
traffic. Ask of any concurrent pointer: "what breaks if this is stale?"
Here: nothing — walks self-correct.

## 3. Losers retry, never wait

CAS failure is information (someone else progressed), not conflict. The
protocol converts contention into extra steps for the loser while the
system as a whole always advances — lock-free, not wait-free.

## 4. Garbage signposts itself

Self-links turn freed nodes into restart markers. Memory reclamation and
walker correctness share one mechanism — elegant because neither needs
the other's bookkeeping.

## 5. Null is protocol, not value

`item == null` means "dequeued or dummy" — which is exactly why
`offer(null)` is banned. Sentinels work only when users cannot forge them.

## 6. Size is a rumor

`size()` counts a moving chain; the answer is stale before it returns.
Treat it as telemetry (monitoring, tests) — never as control flow in hot
concurrent paths. `isEmpty()` is cheaper but equally non-binding.

## 7. No ABA by construction

Nodes never return to a previous state (`next`: null → node → self;
`item`: value → null, one way). Without state reuse there is nothing for
ABA to exploit — GC freshness does the work version counters do elsewhere.
