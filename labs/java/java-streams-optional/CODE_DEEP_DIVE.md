# Code Deep Dive — Streams & Optional

## 1. Source Tour
- `java.util.stream.ReferencePipeline`, `Collectors`, `Optional` (java.base).
- `Spliterators.ArraySpliterator.trySplit` halves array — ideal parallel.
- `Collectors.groupingBy` → HashMap + downstream combiner.

## 2. Bytecode: Lambda in Stream
```java
list.stream().map(s -> s.length())
```
`javap -c -p` shows `invokedynamic LambdaMetafactory` + synthetic `lambda$...`.
JIT inlines small lambdas; megamorphic call sites deopt — keep lambdas stable.

## 3. Lazy Fusion
Intermediate ops build pipeline object; terminal triggers `evaluate`.
`peek` without terminal emits nothing — prove with counter test.

## 4. Boxing Path
`Stream<Long>.mapToInt` unboxes per element (`Long.longValue`).
JFR allocation profile shows `Long` churn; fix with `mapToLong(Long::longValue)` early or LongStream.

## 5. Parallel Mechanics
`parallelStream` → AbstractTask split via Spliterator → ForkJoinPool.commonPool.
Bad: `LinkedList` (poor split) vs good: arrays/ArrayList/range.
Custom: `ForkJoinPool(4).submit(() -> stream.parallel()...).get()`.

## 6. Collector Internals
`groupingBy` supplier HashMap, accumulator `map.merge`, combiner `putAll`-ish.
Concurrent variant uses ConcurrentHashMap + no combiner barrier.

## 7. Optional Bytecode
`Optional.map` = null-check + apply; `orElse` = field read + branch.
`orElse(new Heavy())` always News — bytecode shows NEW before branch; use orElseGet.

## 8. Profiling
```bash
java -XX:+UseG1GC -Xlog:gc* Main
jfr: jdk.ObjectAllocationInNewTLAB for boxing
async-profiler -e cpu -- stream hotspots
```

## 9. HotSpot Refs
`LambdaMetafactory`, `ReferencePipeline::forEachWithCancel` (short-circuit flag).
