# Exercises — Streams & Optional (10 hands-on)

## E1 — Map/Filter/Reduce
```java
int sum = list.stream().filter(i -> i > 0).mapToInt(i -> i*2).sum();
```
Tasks: rewrite loop → stream; measure with JMH-lite (nanoTime loop).

## E2 — Lazy + Short-Circuit
Tasks: `filter(...).findFirst()` with peek logging — prove downstream not run.

## E3 — Collectors
```java
Map<String,List<Order>> by = orders.stream().collect(groupingBy(Order::region));
```
Tasks: groupingBy + counting + partitioningBy examples.

## E4 — Custom Collector
Tasks: top-K collector (supplier/acc/combiner/finisher); test parallel correctness.

## E5 — flatMap
Tasks: `List<List<String>>` → distinct sorted words; handle null inner lists.

## E6 — Optional Chaining
```java
String city = Optional.ofNullable(user).map(User::addr).map(Addr::city).orElse("N/A");
```
Tasks: replace 3 nested null-checks; orElse vs orElseGet demo (eager pitfall).

## E7 — Optional Misuse Fix
Tasks: find `isPresent+get`, `Optional` field/param smells; refactor to orElseThrow/map.

## E8 — Parallel Streams
Tasks: sum 10M longs sequential vs parallel; try ArrayList vs LongStream.range (spliterator!).

## E9 — Gatherers (JDK 22+)
Tasks: sliding-window gatherer; compare vs manual loop.

## E10 — Capstone: Log Stats
Tasks: stream 1GB log → status counts + p99 latency per endpoint.
Flags: `-Xmx1g`. Checklist: no OOM, single pass, parallel validated.
