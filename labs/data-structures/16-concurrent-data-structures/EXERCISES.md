# Exercises: Concurrent Data Structures

Implement from scratch in Java (no AI-written core logic). Trace each exercise on paper before coding; commit the trace as a comment.

## Beginner

1. **Racy counter demo**: Show lost updates with N threads x 100k increments on a plain int; record final error.
```java
// Lab 16-concurrent-data-structures: Racy counter demo
counter++ // racy: measure lost updates
```

2. **Synchronized fix**: Guard with synchronized; measure throughput drop at 8 threads.
```java
// Lab 16-concurrent-data-structures: Synchronized fix
synchronized (lock) { counter++; }
```

3. **CAS retry counter**: AtomicInteger/AtomicLong loop; count retries under contention.
```java
// Lab 16-concurrent-data-structures: CAS retry counter
v.updateAndGet(x -> x + 1); // count retries
```

## Intermediate

4. **LongAdder stripes**: Compare AtomicLong vs LongAdder at 16 threads; plot ops/s.
```java
// Lab 16-concurrent-data-structures: LongAdder stripes
LongAdder a = new LongAdder(); a.increment();
```

5. **BlockingQueue pipeline**: Producer-consumer with ArrayBlockingQueue; measure handoff latency.
```java
// Lab 16-concurrent-data-structures: BlockingQueue pipeline
queue.put(item); ...; queue.take();
```

6. **Copy-on-write snapshot**: CopyOnWriteArrayList readers vs synchronized list; read-heavy bench.
```java
// Lab 16-concurrent-data-structures: Copy-on-write snapshot
CopyOnWriteArrayList<String> list = ...;
```

## Advanced

7. **ReadWriteLock cache**: Read-heavy map with ReentrantReadWriteLock; hit-rate + latency.
```java
// Lab 16-concurrent-data-structures: ReadWriteLock cache
rw.readLock().lock(); try { ... }
```

8. **CompletableFuture fan-out**: Fan out 8 fetches, combine with allOf; timeout + fallback path.
```java
// Lab 16-concurrent-data-structures: CompletableFuture fan-out
CompletableFuture.allOf(futs).join();
```

## Traces and checks
- Commit one ASCII hand-trace per exercise (state before/after the hot path).
- Invariant holds after every op; trace matches execution or the exercise fails.

## Grading rubric

- Correctness 40 / hand traces 20 / edge-case tests 20 / benchmark note 20.

## How to work this set

- Timebox: Beginner 25 min, Intermediate 40 min, Advanced 60 min.
- Write the trace first; code second; fuzz last.
- If stuck more than 20 min, shrink the input to n = 3 and re-trace.

## Common wrong turns

- Skipping the hand trace and debugging blind against failing tests.
- Testing only sorted/insertion-order input; adversarial order finds the real bugs.
- Forgetting the empty and singleton cases in every new operation.
- Measuring performance without warmup and reporting noise as signal.

## Stretch

- S1. Swap one core design choice (array vs map, iterative vs recursive) and re-benchmark.
- S2. Write the 5-line lesson-learned note: what broke, what fixed it, what to check first next time.

## Done when

- [ ] 8/8 exercises green with committed traces
- [ ] Fuzz run clean for 10k random ops against the naive model
- [ ] Benchmark table filled at n = 1k / 10k / 100k
