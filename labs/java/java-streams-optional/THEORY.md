# THEORY — Streams & Optional

## Overview

Functional-style operations on collections: **Streams** for pipeline processing, **Optional** for null-safety.

---

## Stream API

### Creation

```java
// From collections
list.stream()
set.stream()

// From arrays
Arrays.stream(array)
Stream.of("a", "b", "c")

// Infinite streams
Stream.iterate(0, n -> n + 2)           // 0, 2, 4, 6...
Stream.generate(() -> random.nextInt()) // random ints

// From I/O
Files.lines(path)
BufferedReader.lines()
Pattern.compile(",").splitAsStream(input)
```

### Intermediate Operations (Lazy)

| Operation | Description | Short-circuit |
|-----------|-------------|---------------|
| `filter(predicate)` | Keep matching | No |
| `map(mapper)` | Transform | No |
| `flatMap(mapper)` | Flatten nested | No |
| `distinct()` | Remove duplicates | No |
| `sorted()` / `sorted(comp)` | Sort | No |
| `peek(action)` | Side-effect debugging | No |
| `limit(n)` | First n elements | **Yes** |
| `skip(n)` | Skip first n | No |
| `takeWhile(pred)` | Until false (Java 9) | **Yes** |
| `dropWhile(pred)` | Skip while true (Java 9) | No |

### Terminal Operations (Eager)

| Operation | Returns | Short-circuit |
|-----------|---------|---------------|
| `forEach(action)` | void | No |
| `forEachOrdered(action)` | void | No |
| `toArray()` | Object[] | No |
| `reduce(identity, accumulator)` | T | No |
| `collect(collector)` | R | No |
| `min/max(comparator)` | Optional<T> | No |
| `count()` | long | No |
| `anyMatch/allMatch/noneMatch` | boolean | **Yes** |
| `findFirst/findAny` | Optional<T> | **Yes** |
| `iterator()` | Iterator | No |

### Collectors

```java
// To collections
.toList()           // List (Java 16+)
.toSet()
.toCollection(ArrayList::new)
.toMap(keyMapper, valueMapper)
.toMap(k, v, mergeFn)           // handle collisions
.toMap(k, v, mergeFn, TreeMap::new)

// Grouping
.groupingBy(classifier)
.groupingBy(classifier, downstream)
.groupingBy(classifier, () -> TreeMap::new, downstream)

// Partitioning
.partitioningBy(predicate)
.partitioningBy(predicate, downstream)

// Joining
.joining()
.joining(delimiter)
.joining(delim, prefix, suffix)

// Reduction
.reducing(identity, mapper, combiner)
.summarizingInt(mapper)  // IntSummaryStatistics
.averagingInt(mapper)

// Custom
Collector.of(
    ArrayList::new,           // supplier
    List::add,                // accumulator
    (l1, l2) -> { l1.addAll(l2); return l1; }, // combiner
    Characteristics.IDENTITY_FINISH
)
```

### Parallel Streams

```java
// Enable parallelism
list.parallelStream()
stream.parallel()

// ForkJoinPool.commonPool() used by default
// Custom pool:
ForkJoinPool pool = new ForkJoinPool(4);
pool.submit(() -> list.parallelStream().forEach(...)).join();

// When parallel helps:
// - Large datasets (>10k elements)
// - CPU-intensive operations
// - No shared mutable state

// When parallel hurts:
// - Small datasets
// - I/O bound (use CompletableFuture instead)
// - Synchronized/stateful operations
```

### Primitive Streams

```java
IntStream.range(0, 10)           // 0..9
IntStream.rangeClosed(1, 10)     // 1..10
LongStream.of(1L, 2L, 3L)
DoubleStream.generate(Math::random)

// Conversions
stream.mapToInt(String::length)
intStream.boxed()                // IntStream -> Stream<Integer>

// Operations
intStream.sum(), average(), min(), max()
intStream.summaryStatistics()    // count, sum, min, avg, max
```

---

## Optional (Java 8+)

### Creation

```java
Optional.empty()
Optional.of(value)        // NPE if null
Optional.ofNullable(value) // empty if null
```

### Transformation

```java
optional.map(x -> x.getName())           // Optional<String>
optional.flatMap(x -> x.getAddress())    // Optional<Address>
optional.filter(x -> x.length() > 3)     // Optional<String>
```

### Consumption

```java
// Functional
optional.ifPresent(System.out::println);
optional.ifPresentOrElse(
    System.out::println, 
    () -> System.out.println("empty")
);

// Value retrieval
String name = optional.orElse("default");
String name = optional.orElseGet(() -> computeDefault());
String name = optional.orElseThrow(() -> new NotFoundException());

// Stream conversion (Java 9+)
Stream<String> stream = optional.stream();
```

### Best Practices

| Do | Don't |
|----|-------|
| Return `Optional` from methods | Use `Optional` as field/parameter |
| `orElseGet` for lazy default | `orElse(expensive())` eager |
| `flatMap` for chaining | Nested `Optional<Optional<T>>` |
| `ifPresent` for side effects | `get()` without `isPresent()` |
| Use as return type | Serialize `Optional` |

---

## Stream Patterns

### Grouping & Aggregation

```java
// Group employees by department, count each
Map<Department, Long> counts = employees.stream()
    .collect(groupingBy(Employee::getDept, counting()));

// Group by dept, collect names
Map<Department, List<String>> names = employees.stream()
    .collect(groupingBy(Employee::getDept, 
        mapping(Employee::getName, toList())));

// Partition by salary > 100k
Map<Boolean, List<Employee>> partitioned = employees.stream()
    .collect(partitioningBy(e -> e.getSalary() > 100_000));
```

### Reduction

```java
// Sum salaries
double total = employees.stream()
    .mapToDouble(Employee::getSalary)
    .sum();

// Find max salary employee
Optional<Employee> top = employees.stream()
    .max(Comparator.comparingDouble(Employee::getSalary));

// Concatenate names
String names = employees.stream()
    .map(Employee::getName)
    .collect(joining(", "));
```

### FlatMap Patterns

```java
// Flatten list of lists
List<Order> orders = customers.stream()
    .flatMap(c -> c.getOrders().stream())
    .toList();

// Optional chaining
Optional<String> zip = customerStream
    .flatMap(Customer::getAddress)
    .flatMap(Address::getZipCode)
    .findFirst();
```

---

## Performance Considerations

| Aspect | Recommendation |
|--------|----------------|
| Boxed vs primitive | Use `IntStream`, `LongStream`, `DoubleStream` |
| Parallel threshold | > 10k elements for CPU-bound |
| Collector choice | Prefer built-in over custom |
| Short-circuit | Use `limit`, `findFirst`, `anyMatch` early |
| Stateful ops | Avoid in parallel (sort, distinct) |
| Lambda capture | Avoid capturing mutable state |