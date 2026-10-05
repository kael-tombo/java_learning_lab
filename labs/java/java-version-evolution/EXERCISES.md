# Exercises — Java Version Evolution (9 hands-on)

## E1 — Lambdas (8)
```java
list.sort((a,b) -> a.length() - b.length());
```
Tasks: loop→lambda→method-ref; flags none.

## E2 — Streams (8) + Date/Time (8)
Tasks: old Date bug demo → java.time fix; stream agg.

## E3 — var + Modules (10/11)
Tasks: `var` readability; `jdeps` + minimal `jlink` hello.

## E4 — Records + Sealed (16/17)
Tasks: DTO record; sealed Shape switch exhaustive.

## E5 — Text Blocks + Switch Expr (15/14)
Tasks: JSON text block; switch expression with yield.

## E6 — Pattern Matching (21)
Tasks: instanceof pattern + record pattern + guard.

## E7 — Virtual Threads (21)
```java
try (var ex = Executors.newVirtualThreadPerTaskExecutor()) { ex.submit(task); }
```
Tasks: 10k tasks; flags `-Djdk.virtualThreadScheduler.parallelism=4`.

## E8 — Sequenced Collections + Gatherers (21/22)
Tasks: SequencedMap ops; sliding-window gatherer.

## E9 — Upgrade Capstone
Tasks: migrate 8→21 sample: warnings, `--release 8` vs 21, G1→ZGC compare.
Flags: `-Xlog:gc* -XX:+UseZGC`. Checklist: build green, perf noted.
