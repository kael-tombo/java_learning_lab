# Refactoring: Memory Barriers

## Pattern 1: plain flag publication -> edged publication

Before (accident, snippet 4):

```java
static int data; static boolean flag;
// writer: data = 42; flag = true;
// reader: while (!flag) Thread.onSpinWait(); use(data);
```

After (verdict — pick one, cheapest sufficient first):

```java
static int data; static volatile boolean flag; // release/acquire pair
// or: READY.await() latch handoff (lab 01 shape)
```

Why: output unchanged (0/2000 before and after on x86), verdict
converted (race -> guaranteed). The motel now holds the prefix: release
keeps `data` before the flag, acquire keeps the use after it.

## Pattern 2: volatile-everywhere sequencing -> release chains

Before: sequence advancement through volatile `set` (~10 ns/store) for
a single-consumer pipeline — total order paid, pairwise consumed.

After: `lazySet` / `setRelease` (~1.3 ns/store), consumer-side
`getAcquire` spin (lab 02 snippet 4: 50000 intact). Saving ~8x per
store with the verdict the shape needs. Escalate to volatile only the
steps where producers mutually observe (Dekker-shaped joins).

## Pattern 3: release/acquire Dekker -> volatile or lock

Before: `X.setRelease(1); r1 = Y.getAcquire()` both sides — 61-90%
anomalies, modern spelling on a total-order problem.

After (ordering): plain `volatile` fields — 0/20000 everywhere. After
(exclusion): whole pair in one `synchronized` — 0/20000 by no overlap.
The refactor decision is shape analysis (mutual observation needs
systems, not chains), applied in one mode step.

## Pattern 4: per-element fenced publishes -> single-reference publish

Before: N volatile stores publishing N fields (N StoreLoad fences per
graph) — correct, N times overpriced.

After: N plain field writes + one volatile reference/latch release
(one fence per graph). Same hb coverage (release carries the prefix),
1/Nth the fence bill. Applicable everywhere bulk state crosses threads
(config graphs, snapshots, buffers) — lab 01's latch shape, priced by
this lab's ladder.

## Pattern 5: opaque/volatile misuse -> correct rung

- Opaque guarding data -> release/acquire minimum (opaque orders
  nothing; guards need LoadLoad/LoadStore).
- Plain 64-bit counter -> opaque minimum (plain tears; opaque is
  atomic and eventually visible) or `LongAdder` where contention rules.
- Hand-placed `Unsafe` fences -> VarHandle modes (same silicon, real
  JMM verdicts, portable placement). Delete the import, keep the
  ordering.

## Refactoring checklist

- Name the shape (handoff chain, mutual observation, bulk publish,
  statistics) before touching the mode.
- Count fences before/after (0/0/1 per side on x86) and predict the
  ladder move; confirm with one warmed in-JVM ratio run.
- Assert the verdict change (race -> guaranteed; 61-90% -> 0) with
  fixed rounds (2000/20000), never with absolutes or single runs.
- Keep println ASCII (`String.format("%.2f", ...)`); prose stays UTF-8.
