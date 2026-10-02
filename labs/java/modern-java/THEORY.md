# THEORY — Modern Java: Lambdas, Streams, Pattern Matching (Part 3 - Migration & Quick Reference)

## 8. Migration Guide

### From Anonymous Classes to Lambdas

```java
// Before (Anonymous class)
button.addActionListener(new ActionListener() {
    public void actionPerformed(ActionEvent e) {
        System.out.println("Clicked!");
    }
});

// After (Lambda)
button.addActionListener(e -> System.out.println("Clicked!"));
```

### From Loops to Streams

```java
// Before
List<String> result = new ArrayList<>();
for (String s : names) {
    if (s.length() > 3) {
        result.add(s.toUpperCase());
    }
}

// After
List<String> result = names.stream()
    .filter(s -> s.length() > 3)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

### From If-Else to Pattern Matching

```java
// Before
String result;
if (obj instanceof Integer) {
    result = "int: " + (Integer) obj;
} else if (obj instanceof String) {
    result = "String: " + (String) obj;
} else {
    result = "unknown";
}

// After (Java 17+)
String result = switch (obj) {
    case Integer i -> "int: " + i;
    case String s -> "String: " + s;
    default -> "unknown";
};
```

---

## 9. Migration Checklist

### Java 8 → 11 Migration

- [ ] Replace anonymous classes with lambdas
- [ ] Use `var` for local variables (Java 10+)
- [ ] Use `var` in lambda parameters (Java 11+)
- [ ] Use `Collection.toArray(IntFunction)` instead of `toArray(new T[0])`

### Java 11 → 17 Migration

- [ ] Use `record` for immutable data carriers
- [ ] Use `sealed` classes for closed hierarchies
- [ ] Use pattern matching for `instanceof`
- [ ] Use text blocks for multi-line strings

### Java 17 → 21 Migration

- [ ] Use `record` patterns in `switch`
- [ ] Use `switch` expressions exhaustively
- [ ] Use virtual threads for I/O-bound tasks
- [ ] Use `String.isBlank()`, `isBlank()` instead of `trim().isEmpty()`

---

## 9. Quick Reference Card

### Lambda Syntax

```java
// No params, no return
() -> System.out.println("hi")

// One param, implicit type
s -> s.length()

// Multiple params
(a, b) -> a + b

// Block body with return
(a, b) -> {
    int sum = a + b;
    return sum * 2;
}
```

### Stream Cheat Sheet

```java
// Creation
Stream.of(a, b, c)
Stream.of(array)
list.stream()
IntStream.range(0, n)
Stream.iterate(0, n -> n + 1).limit(n)

// Intermediate (lazy)
.filter(p)
.map(f)
.flatMap(f)
.sorted()
.limit(n)
.skip(n)
.distinct()
.peek(action)

// Terminal
.collect(toList())
.reduce(identity, op)
.findFirst()
.anyMatch(p)
.allMatch(p)
.noneMatch(p)
count()
forEach(action)
```

### Collector Cheat Sheet

```java
Collectors.toList()
Collectors.toSet()
Collectors.toMap(k -> k, v -> v)
Collectors.toMap(k -> k, v -> v, (v1, v2) -> v1)  // merge
Collectors.joining(", ")
Collectors.groupingBy(f)
Collectors.partitioningBy(p)
Collectors.summarizingInt(f)
Collectors.mapping(f, downstream)
Collectors.reducing(identity, op)
```