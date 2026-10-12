# References: CompletableFuture

## Books

- Brian Goetz et al., *Java Concurrency in Practice* (2006) — `Future`/`FutureTask`
  foundations (ch. 6); read before judging what CF improved.
- Doug Lea, "Asynchronous Tasks in Java" (ongoing notes,gee.cs.oswego.edu) —
  design background for `CompletableFuture` and `ForkJoinPool` interplay.
- Cay Horstmann, *Modern Java in Action*-era coverage — practical CF pipeline
  patterns (map/flatMap/combine).

## Papers

- Jeffrey Dean & Luiz Barroso, "The Tail at Scale" (CACM 2013) — the hedged-
  request (`anyOf`) rationale quantified.
- Halpern & Moses lineage on async coordination (background for barrier/race
  combinators `allOf`/`anyOf`).

## OpenJDK sources (authoritative for this lab)

- `java.base/java/util/concurrent/CompletableFuture.java` — completion stack,
  `UniApply`/`UniCompose`/`BiApply`, `AltResult`, `cancel()` ignoring its flag,
  `orTimeout`/`completeOnTimeout` returning `this`, `USE_COMMON_POOL`.
- `java.base/java/util/concurrent/ForkJoinPool.java` — the default async
  executor CF borrows (common pool sizing).
- `java.base/java/util/concurrent/FutureTask.java` — contrast: `cancel(true)`
  *does* interrupt its runner (CF has no runner).

## Documentation

- `CompletableFuture` class javadoc — per-method thread/executor rules and the
  `allOf` (`CF<Void>`) / `anyOf` (`CF<Object>`) signatures.
- `CompletionStage` interface javadoc — the combinator contracts.
- `ForkJoinPool.commonPool()` javadoc — shared-pool sizing and caveats.
