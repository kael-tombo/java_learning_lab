# Java Streams Collectors — Deep Dive: `collect()` vs `reduce()`, `groupingBy`/`partitioningBy`, Downstream & Concurrent Collectors

> Why did `Main.main()` pass but JaCoCo still flag `MapOperationsDemo` and
> `FlatMapOperationsDemo` as under-covered until `DemoSmokeTest.testRemainingDemosRun()`
> explicitly called `demonstrateChainedMapping()`, `demonstrateFlatMapVsMap()`, etc.?
> This guide traces the answer from the `Collector` interface to the coverage report.

All claims grounded in `01-core-java/04-streams-api/src/main/java/com/learning/`:
`Main.java`, `collectors/CollectorExamplesDemo.java`, `collectors/GroupingByDemo.java`,
`collectors/ComplexCollectorsDemo.java`, `transformation/MapOperationsDemo.java`,
`transformation/FlatMapOperationsDemo.java`, `terminal/CollectOperationsDemo.java`,
`terminal/ReductionOperationsDemo.java`, `EliteStreamsTraining.java:388-453`,
plus `src/test/java/com/learning/DemoSmokeTest.java`.

---

## 1. THEORY — Mental models

### 1.1 `reduce()` vs `collect()`: fold vs mutable bucket brigade

| | `reduce()` | `collect()` |
|---|---|---|
| Accumulator shape | Same type as elements (or a boxed wrapper): `T reduce(T identity, BinaryOperator<T>)` | *Different* mutable container `A`: `List`, `Map`, `StringBuilder`, `IntSummaryStatistics` |
| Signature (simplest) | `ReductionOperationsDemo.demonstrateReduction()`: `numbers.stream().reduce(0, Integer::sum)` | `CollectOperationsDemo.demonstrateCollect()`: `numbers.stream().collect(Collectors.toList())` |
| Parallel strategy | Combiner merges two partial *values* (`(a,b) -> a*b`); no shared state | `Collector` has explicit `supplier()` + `accumulator()` + `combiner()`; threads merge partial *containers* |
| Empty-stream result | No-identity overload returns `Optional.empty()` (see `Stream.<Integer>empty().reduce(Integer::sum)`) | Returns the empty container (`[]`, `{}`), never `Optional` — supplier always runs |
| When to use | Single scalar: sum, product, max, concatenation | Any shaped result: list/set/map, statistics, grouped maps, joined strings |

Mental model: `reduce()` is folding a paper strip into one square — every fold
combines two same-shaped things. `collect()` is handing each worker a bucket
(`supplier()`), letting them toss items in (`accumulator()`), then pouring buckets
together (`combiner()`), optionally sealing the lid (`finisher()`).

That is literally the `Collector<T, A, R>` interface: `supplier`, `accumulator`,
`combiner`, `finisher`, `characteristics`. `ComplexCollectorsDemo` line 436+ shows
it explicitly: `Collector.<T, LinkedHashSet<T>, List<T>>of(LinkedHashSet::new, …)`
in `EliteStreamsTraining.collectToImmutableNoDuplicates()`.

### 1.2 `groupingBy` vs `partitioningBy`: N buckets vs exactly 2

- `partitioningBy(predicate)` → `Map<Boolean, D>` with **always both keys**
  (`true` and `false`), even if one list is empty. Backed by a specialised
  implementation — no hash computation, just an if/else.
  Real code: `CollectorExamplesDemo.demonstrateCollectors()` partitions fruits by
  `s.length() > 5` and scores by `s >= 85`.
- `groupingBy(classifier)` → `Map<K, D>` with **arbitrary keys**, HashMap-based,
  one hash lookup per element. Real code: `GroupingByDemo.demonstrateGroupingBy()`
  groups fruits by `s.charAt(0)` and by `String::length`.

Interview one-liner: *partitioning is grouping specialised to a boolean key —
faster and with a total-map guarantee.*

### 1.3 Downstream collectors: collectors inside collectors

Every `groupingBy`/`partitioningBy`/`mapping`/`filtering`/`flatMapping`/`teeing`/
`collectingAndThen` overload takes a **downstream** `Collector` that post-processes
each bucket:

```
groupingBy(classifier)                          == groupingBy(classifier, toList())
groupingBy(String::length, counting())          // Map<Integer, Long>
groupingBy(c -> c, groupingBy(n -> n % 2, counting()))  // nested Map<Integer, Map<Integer, Long>>
groupingBy(n -> n % 3, summingInt(...))         // Map<Integer, Integer>
mapping(String::length, toList())               // transform before collecting
filtering(s -> s.length() > 5, toList())        // filter inside the terminal step
flatMapping(word -> word.chars()…, toList())    // flatten inside the terminal step
reducing((a,b) -> a * b)                        // reduce disguised as a collector
teeing(counting(), summingInt(…), …)            // fork one stream into two collectors
collectingAndThen(toList(), list -> sort…)      // finish, then apply a function
toMap(w -> w, String::length, Integer::sum, LinkedHashMap::new)  // merge fn + map supplier
```

All eight patterns above appear verbatim in `GroupingByDemo`, `CollectorExamplesDemo`,
and `ComplexCollectorsDemo`. The nesting is what makes collectors composable where
`reduce()` is not: you cannot express "group by length, then count, then nest by
parity" as a single `BinaryOperator`.

### 1.4 Concurrent collectors: same API, thread-safe buckets

`Collectors.groupingByConcurrent(...)` / `toConcurrentMap(...)` return a
`Collector` with the `CONCURRENT` + `UNORDERED` characteristics: one shared
`ConcurrentHashMap` that all parallel threads accumulate into, instead of merging
per-thread HashMaps at the end. Real usage:
`EliteStreamsTraining.processTransactionsInParallel()` (lines 398–410) collects
`transactions.parallelStream()` with `groupingByConcurrent(Transaction::getCategory,
counting())` and `averagingDouble(...)`.

Rule: concurrent collector + **sequential** stream = correct but pointless
(extra CAS overhead, nondeterministic order). Concurrent collector +
**parallel** stream over a largeSplittable source = the intended win.
`ParallelStreamsDemo` shows the other half of the story: `largeList.parallelStream()
.filter(…).map(…).count()` and why `limit(5)` + `forEach` prints interleaved thread IDs.

### 1.5 The coverage mystery, previewed

`Main.demonstrateTransformations()` (`Main.java:123-140`) calls only:

```java
demo1.demonstrateBasicMapping();     // MapOperationsDemo — 1 of 5 methods
demo1.demonstrateStringMapping();    // 2 of 5
demo2.demonstrateBasicFlatMap();     // FlatMapOperationsDemo — 1 of 8 methods
```

`Main.demonstrateCollectors()` (`Main.java:160-182`) calls only the three
single entry points (`demonstrateCollectors`, `demonstrateGroupingBy`,
`demonstrateComplexCollectors` — these classes each have exactly one public
method, so they are fully covered). The *transformation* demos each expose
5–8 public methods (`demonstrateObjectMapping`, `demonstrateChainedMapping`,
`demonstrateNumericMapping`, `demonstrateFlatMapWithStrings`,
`demonstrateFlatMapWithObjects`, `demonstrateFlatMapVsMap`,
`demonstrateFlatMapForCombinations`, `demonstrateNestedFlatMap`,
`demonstrateFlatMapWithOptional`, `demonstrateFlatMapPerformance`), and JaCoCo
counts **per-method/line** coverage — an uncalled public method is uncovered
code even if its class was instantiated. Hence `DemoSmokeTest.testRemainingDemosRun()`
(lines 40–70) exists purely to invoke every `Main`-skipped method so JaCoCo sees
real execution. Section 2.4 walks this line by line.

---

## 2. CODE_DEEP_DIVE — Grounded in the real files

### 2.1 `collect()` (`terminal/CollectOperationsDemo.java:18-75`) vs `reduce()` (`terminal/ReductionOperationsDemo.java:18-71`)

Side by side on the same input `List.of(1,…,10)`:

```java
// collect: mutable container, many shapes
List<Integer> even = numbers.stream().filter(n -> n % 2 == 0).collect(Collectors.toList());
Set<Integer> uniq = List.of(1,2,2,3,3,3).stream().collect(Collectors.toSet());
Map<Integer,String> words = numbers.stream().filter(n -> n <= 5)
    .collect(Collectors.toMap(n -> n, n -> switch(n){ case 1 -> "One"; … default -> "Unknown"; }));
String joined = fruits.stream().collect(Collectors.joining(", ", "[", "]"));
long count = fruits.stream().collect(Collectors.counting());   // == fruits.stream().count()
Optional<String> longest = fruits.stream().collect(Collectors.maxBy(comparingInt(String::length)));
int total = numbers.stream().collect(Collectors.summingInt(Integer::intValue));
double avg  = numbers.stream().collect(Collectors.averagingInt(Integer::intValue));
```

```java
// reduce: immutable fold to one value
int sum     = numbers.stream().reduce(0, Integer::sum);
int product = numbers.stream().reduce(1, (a, b) -> a * b);
Optional<Integer> max = numbers.stream().reduce((a, b) -> a > b ? a : b);
Optional<String> concat = words.stream().reduce((s1, s2) -> s1 + " " + s2);
int withCombiner = numbers.stream().reduce(0, Integer::sum, Integer::sum); // 3-arg: parallel split
Optional<Integer> empty = Stream.<Integer>empty().reduce(Integer::sum);    // Optional.empty
int emptyId = Stream.<Integer>empty().reduce(100, Integer::sum);           // 100 (identity returned)
```

Key observations for teaching:

1. `summingInt`/`averagingInt`/`maxBy`/`counting` are just **pre-built reducers
   expressed as collectors** — `ComplexCollectorsDemo:32-44` proves it by doing
   the same work through `Collectors.reducing((a,b) -> a*b)` and
   `Collectors.reducing("", Object::toString, String::concat)`.
2. The 3-arg `reduce(identity, accumulator, combiner)` is the bridge to parallel:
   the combiner is what `collect()`'s `combiner()` does, but restricted to the
   same type. When the result type differs from the element type (e.g. `List<String>`
   → `Map<…>`), only `collect()` can express it.
3. `reduce("", (acc, v) -> acc + "[" + v + "]")` (line 59-61) is the classic
   **string-concat-in-reduce anti-pattern**: O(n²) copies plus broken parallelism
   (non-associative if order matters). `Collectors.joining()` uses a shared
   `StringBuilder` per thread — the correct `collect()` answer.

### 2.2 `groupingBy` mechanics (`collectors/GroupingByDemo.java:18-76`)

```java
Map<Character, List<String>> byFirst = fruits.stream().collect(groupingBy(s -> s.charAt(0)));
Map<Integer, List<String>> byLen = fruits.stream().collect(groupingBy(String::length));
Map<Integer, Long> lenCounts     = fruits.stream().collect(groupingBy(String::length, counting()));
Map<String, Long> evenOdd        = numbers.stream().collect(groupingBy(n -> n % 2 == 0 ? "even" : "odd", counting()));
Map<Character, Set<String>> toSet    = fruits.stream().collect(groupingBy(s -> s.charAt(0), toSet()));
Map<Integer, Map<Integer, Long>> nested = numbers.stream().collect(
    groupingBy(n -> n / 3, groupingBy(n -> n % 2, counting())));
Map<Integer, Integer> groupedSum = numbers.stream().collect(
    groupingBy(n -> n % 3, summingInt(Integer::intValue)));
```

Default map is `HashMap`, default downstream is `toList()`. Each element pays one
classifier call + one hash lookup. The `nested` example is the interview favourite:
outer key `n/3`, inner key `n%2`, leaf `counting()` — three levels of downstream
composition in one terminal operation.

### 2.3 `partitioningBy` + downstream zoo (`collectors/CollectorExamplesDemo.java:18-68`, `collectors/ComplexCollectorsDemo.java:18-76`)

```java
// partitioningBy — Map<Boolean, …>, both keys always present
Map<Boolean, List<String>> part  = fruits.stream().collect(partitioningBy(s -> s.length() > 5));
Map<Boolean, List<Integer>> pass = scores.stream().collect(partitioningBy(s -> s >= 85));
// summarizingInt — count/avg/min/max/sum in ONE pass
IntSummaryStatistics stats = scores.stream().collect(summarizingInt(Integer::intValue));
// downstream adapters
List<Integer> lens = fruits.stream().collect(mapping(String::length, toList()));
List<String> longs = fruits.stream().collect(filtering(s -> s.length() > 5, toList()));
// ComplexCollectorsDemo: the advanced set
List<Character> chars = words.stream().collect(flatMapping(w -> w.chars().mapToObj(c -> (char) c), toList()));
Optional<Integer> prod = numbers.stream().collect(reducing((a, b) -> a * b));
String concat = words.stream().collect(reducing("", Object::toString, String::concat));
var tee = numbers.stream().collect(teeing(counting(), summingInt(Integer::intValue),
    (count, sum) -> count + " numbers, sum=" + sum));            // Java 12+
Map<String,Integer> wl = words.stream().collect(toMap(w -> w, String::length, Integer::sum, LinkedHashMap::new));
List<Integer> desc = numbers.stream().collect(collectingAndThen(toList(),
    list -> { Collections.sort(list, Collections.reverseOrder()); return list; }));
```

`toMap` deserves a callout: without the merge function (`Integer::sum`) duplicate
keys throw `IllegalStateException`; the 4-arg overload also controls the map
implementation (`LinkedHashMap::new` preserves encounter order — important when the
test asserts on iteration order). `collectingAndThen` returns an *unmodifiable*
wrapper in real code; here the finisher sorts in place and returns the same list —
fine for a demo, but flag the mutability to learners.

Note what is *not* in the basic demos: `groupingByConcurrent` /
`toConcurrentMap`. They live only in `EliteStreamsTraining:398-410` (parallel
transaction aggregation) and in the custom `Collector.of(...)` at line 436 with
`CONCURRENT/UNORDERED/IDENTITY_FINISH` characteristics discussed in the Javadoc at
lines 428-431. Teaching point: the basic demos are sequential-only, so a plain
`groupingBy` is correct; reach for the concurrent variant only with
`parallelStream()`.

### 2.4 Why `DemoSmokeTest` had to call the "extra" methods (the coverage story)

`Main.java` coverage map (what `Main.main()` actually invokes):

| Demo class | Methods Main calls | Methods Main skips |
|---|---|---|
| `MapOperationsDemo` (5 public) | `demonstrateBasicMapping`, `demonstrateStringMapping` | `demonstrateObjectMapping`, `demonstrateChainedMapping`, `demonstrateNumericMapping` |
| `transformation.FlatMapOperationsDemo` (8 public) | `demonstrateBasicFlatMap` | `demonstrateFlatMapWithStrings/WithObjects/FlatMapVsMap/ForCombinations/NestedFlatMap/WithOptional/Performance` |
| `CollectorExamplesDemo` (1 public) | `demonstrateCollectors` | — (fully covered) |
| `GroupingByDemo` (1 public) | `demonstrateGroupingBy` | — (fully covered) |
| `ComplexCollectorsDemo` (1 public) | `demonstrateComplexCollectors` | — (fully covered) |
| `ReductionOperationsDemo`, `intermediate.FlatMapOperationsDemo`, `TerminalOperationsBasicsDemo`, … | *none* | everything |

JaCoCo measures executed lines/branches per method. `new MapOperationsDemo()` +
two method calls leaves three methods at 0% — the class shows ~40% and drags the
module below the 80% gate (see `Main.java:311`: "Test Coverage Target: 80%+").
The fix is `DemoSmokeTest.testRemainingDemosRun()` (`DemoSmokeTest.java:37-70`),
whose Javadoc states it outright:

```java
/**
 * Smoke test that executes every demo entry point.
 * Main covers the primary paths; the second test covers demos
 * Main does not invoke so JaCoCo sees real coverage.
 */
```

It calls `demonstrateChainedMapping()`, `demonstrateFlatMapVsMap()`,
`demonstrateObjectMapping()`, `demonstrateNumericMapping()`, all seven
non-basic flatMap methods, plus `ReductionOperationsDemo.demonstrateReduction()`
and the intermediate/terminal/optional/filtering leftovers. Two lessons in one:

1. **Demo-orchestrator ≠ test suite.** `Main` is a showcase, not exhaustive;
   coverage must be driven by tests that enumerate the API surface.
2. **Collector demos are cheap to cover, transformation demos are not.**
   The three collector classes expose exactly one public method each, so one
   `Main` call = 100%. Any class with N public demo methods needs N calls —
   the `map`/`flatMap` demos are the long tail.

---

## 3. MATH_FOUNDATION — Complexity analysis

Let n = elements, k = distinct keys, d = downstream cost per element.

| Collector | Time | Extra space | Notes |
|---|---|---|---|
| `toList` / `toSet` / `joining` / `counting` / `summingInt` | O(n) | O(n) result (O(1) for scalar) | Single pass; `joining` amortised O(n) via `StringBuilder` vs O(n²) naive `reduce` concat |
| `toMap` (no merge) | O(n) avg | O(n) | One hash insert/element; duplicate key → throw |
| `partitioningBy(pred)` | O(n) | O(n) | Predicate is O(1); no hashing, direct boolean dispatch |
| `groupingBy(classifier)` | O(n) avg, O(n²) adversarial hash | O(n + k) | One classifier + one hash lookup per element |
| `groupingBy + counting/summing` | O(n) | O(k) | Downstream is O(1) per element; result shrinks to k entries |
| Nested `groupingBy(groupingBy(counting))` | O(n) | O(k₁·k₂) worst | Inner maps multiply key space; `GroupingByDemo:59-67` builds `Map<Integer,Map<Integer,Long>>` |
| `mapping/filtering/flatMapping` downstream | O(n·m) for flatMap (m = avg fan-out) | O(n·m) | `flatMapping(word → chars)` explodes one word into many chars |
| `teeing(c1, c2, merge)` | O(n·(d₁+d₂)) | O(result₁ + result₂) | Two full downstream passes fused into one traversal — still O(n), 2× constant |
| `collectingAndThen(toList, sort)` | O(n log n) | O(n) | Dominated by the finisher sort |
| `summarizingInt` | O(n) time, O(1) space | Single pass replaces 5 passes (count/sum/min/max/avg) | `CollectorExamplesDemo:44-51` |
| Parallel + `groupingByConcurrent` | O(n/p) ideal, p = parallelism | O(n) shared `ConcurrentHashMap` | No combiner merge phase; contention on hot keys bounds speedup (Amdahl) |
| Parallel + plain `groupingBy` | O(n/p + k·p) | O(n + k·p) | Each thread builds its own map, then merges — extra k·p merge cost |

Worked micro-example: `GroupingByDemo` groups 10 numbers by `n % 3` with
`summingInt` → 10 classifier calls + 10 hash inserts + 10 int adds = O(10);
result holds exactly k=3 entries regardless of n. Scaling to 10⁷ elements keeps
the result at 3 entries — the canonical reason `groupingBy+reduction` beats
"collect groups then loop again".

---

## 4. EXERCISES

1. **`collect`-vs-`reduce` swap**: reimplement `CollectOperationsDemo`'s
   `summingInt`/`averagingInt`/`joining` lines using only `Stream.reduce()`.
   Which ones need a different result type, and what breaks on `parallelStream()`?
2. **Downstream rewrite**: redo `GroupingByDemo`'s `lengthCounts` with
   `partitioningBy` + `counting` instead of `groupingBy`. When is the partitioned
   version wrong (hint: how many lengths exist)?
3. **Merge-function hunt**: call the 3-arg `toMap(w -> w, String::length)` (no merge)
   on `words` with a duplicate key. Observe `IllegalStateException`, then fix it
   with the 4-arg overload from `ComplexCollectorsDemo:57-63` and explain what
   `Integer::sum` vs `(a,b) -> a` chooses.
4. **Coverage replay**: comment out the `demonstrateChainedMapping()` and
   `demonstrateFlatMapVsMap()` lines in `DemoSmokeTest.java:53,58`, run
   `mvn -f 01-core-java/04-streams-api/pom.xml verify`, and read the JaCoCo report
   for `MapOperationsDemo` / `FlatMapOperationsDemo`. Restore the lines.
5. **Concurrent swap**: change `EliteStreamsTraining:399` from
   `groupingByConcurrent` to `groupingBy` inside `parallelStream()`. Correctness?
   Performance (merge phase)? Then run the same pipeline sequentially with
   `groupingByConcurrent` — what changes about ordering guarantees?

---

## 5. QUIZ

1. When must you use `collect()` instead of `reduce()`?
2. What keys does `partitioningBy` guarantee in its result map, and why does that differ from `groupingBy`?
3. What is a downstream collector? Name three used in `GroupingByDemo` / `ComplexCollectorsDemo`.
4. When does `groupingByConcurrent` beat `groupingBy`, and what do you give up?
5. `Main.main()` runs green, yet JaCoCo flags `MapOperationsDemo` as under-covered. Why, and which test/method fixes it?

<details><summary>Answers</summary>

1. When the result type differs from the element type (list/map/statistics from a stream of elements), or you need mutable accumulation (`StringBuilder`, `HashMap`, `IntSummaryStatistics`). `reduce()` folds `T×T→T`; `collect()` accumulates `T` into a separate container `A` and can express grouping, joining, and multi-shape results.
2. Exactly `{true, false}` — both keys always present, even with empty lists. It dispatches on a boolean predicate with no hashing. `groupingBy` creates one key per distinct classifier value (arbitrary `K`, HashMap-backed), so absent keys are absent.
3. A collector passed *inside* another collector to post-process each group/partition: `counting()`, `summingInt()`, `toSet()`, nested `groupingBy()`, `mapping()`, `filtering()`, `flatMapping()`, `reducing()`, `teeing()`, `collectingAndThen()` — all appear across the two demo files.
4. With a `parallelStream()` over a large splittable source: threads share one `ConcurrentHashMap` (`CONCURRENT` characteristic) and skip the per-thread-map merge phase. You give up encounter-order determinism (`UNORDERED`) and pay CAS contention on hot keys; on a sequential stream it is pure overhead.
5. `Main.demonstrateTransformations()` calls only `demonstrateBasicMapping` + `demonstrateStringMapping` (2 of 5) and `demonstrateBasicFlatMap` (1 of 8). JaCoCo counts per-method lines, so the uncalled methods (`demonstrateChainedMapping`, `demonstrateFlatMapVsMap`, …) score 0%. `DemoSmokeTest.testRemainingDemosRun()` explicitly invokes every skipped method so JaCoCo records real execution.

</details>

---

## 6. FLASHCARDS

- Q: `reduce()` vs `collect()` result type? → A: reduce folds `T×T→T` (one scalar); collect accumulates `T` into a different container `A` (list/map/stats).
- Q: Empty stream, no-identity `reduce` vs `collect(toList())`? → A: reduce → `Optional.empty`; collect → empty container (supplier always runs).
- Q: `partitioningBy` key guarantee? → A: `Map<Boolean,…>` always has both `true` and `false` keys; no hashing.
- Q: Default downstream of `groupingBy(classifier)`? → A: `toList()` into a `HashMap`.
- Q: Three downstream collectors in our demos? → A: `counting()`, `summingInt()`, `mapping()`, `filtering()`, `flatMapping()`, `reducing()`, `teeing()`, `collectingAndThen()` (any three).
- Q: `toMap` duplicate key without merge fn? → A: throws `IllegalStateException`; supply e.g. `Integer::sum` + optional map supplier (`LinkedHashMap::new`).
- Q: `groupingByConcurrent` needs what stream to pay off? → A: `parallelStream()` + large splittable source; sequential use adds contention and loses ordering.
- Q: Why did `demonstrateChainedMapping` / `demonstrateFlatMapVsMap` need explicit test calls? → A: `Main` called only the basic map/flatMap methods; JaCoCo counts per-method, so `DemoSmokeTest.testRemainingDemosRun()` invokes the rest.

---

## 7. MINI_PROJECT

**Collector kata — `EmployeeAnalytics`.** Given `List<Employee(name, dept, salary)>`:

1. `partitioningBy(e -> e.salary() >= 100_000)` → pass/fail headcount.
2. `groupingBy(Employee::dept, counting())` → headcount per dept.
3. `groupingBy(Employee::dept, averagingDouble(Employee::salary))` → avg salary per dept.
4. Nested `groupingBy(dept, groupingBy(salaryBand, counting()))` (bands via `s/50_000`).
5. `teeing(counting(), summingInt(salary), (c,s) -> …)` → one-pass headcount + payroll.
6. `toMap(name, salary, Integer::max, LinkedHashMap::new)` → dedupe by name keeping max.
7. `collectingAndThen(toList(), sorted-copy-descending)` → leaderboard.

Constraints: implement each with **one terminal `collect()`** (no post-loop fixups);
add a JUnit test per bullet; run JaCoCo and confirm every new method is invoked by
*tests*, not just a `main()` showcase — mirroring the `Main` vs `DemoSmokeTest` lesson.

---

## 8. REAL_WORLD_PROJECT

**Production pipeline: parallel transaction rollup.** Extend
`EliteStreamsTraining.processTransactionsInParallel()` into a service method that,
from a `List<Transaction>`, returns per-category count (`groupingByConcurrent` +
`counting`), per-category average (`groupingByConcurrent` + `averagingDouble`),
global `summarizingDouble` in one `teeing` pass, and an immutable
`Collector.of(...)` deduplicated audit list. Benchmark sequential `groupingBy` vs
parallel `groupingByConcurrent` at 10⁴ / 10⁶ / 10⁷ elements (measure with
`PerformanceComparisonDemo`'s timing pattern); document where parallelism wins,
where contention on a single hot category erases the gain, and why the result map
ordering is nondeterministic. Ship with a `DemoSmokeTest`-style test that invokes
**every** public demo/rollup method so the JaCoCo gate (80%+) passes without relying
on the `main()` orchestrator.
