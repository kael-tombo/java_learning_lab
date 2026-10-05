# THEORY — Records, Sealed Classes & Pattern Matching

## Overview

Modern Java (14-21) introduces data-oriented features: **Records** for immutable data carriers, **Sealed Classes** for restricted hierarchies, and **Pattern Matching** for expressive deconstruction.

---

## Records (Java 16+)

### Basic Syntax

```java
public record Person(String name, int age, Address address) { }

// Equivalent to:
final class Person {
    private final String name;
    private final int age;
    private final Address address;
    
    public Person(String name, int age, Address address) { ... }
    public String name() { return name; }
    public int age() { return age; }
    public Address address() { return address; }
    public boolean equals(Object o) { ... }
    public int hashCode() { ... }
    public String toString() { ... }
}
```

### Compact Constructors & Validation

```java
public record Person(String name, int age) {
    // Compact constructor - validation without boilerplate
    public Person {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Name required");
        }
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("Invalid age");
        }
    }
}

// Factory methods
public static Person of(String name, int age) {
    return new Person(name.trim(), age);
}

public static Person newborn(String name) {
    return new Person(name, 0);
}
```

### Record Serialization

```java
// Records serialize as their components
// No serialVersionUID needed
// Deserialization calls canonical constructor

public record Person(String name, int age) implements Serializable {
    private static final long serialVersionUID = 1L;
}
```

### Records with Generics

```java
public record Pair<T, U>(T first, U second) { }
public record Result<T>(T value, String error) { }
public record Page<T>(List<T> content, int page, int size, long total) { }
```

---

## Sealed Classes (Java 17+)

### Basic Syntax

```java
public sealed interface Shape 
    permits Circle, Rectangle, Triangle { }

// Final implementation
public final class Circle implements Shape {
    private final double radius;
    public Circle(double radius) { this.radius = radius; }
}

// Sealed subclass (further restricted)
public sealed class Polygon implements Shape 
    permits Triangle, Pentagon { }

// Non-sealed (open for extension)
public non-sealed class Rectangle implements Shape { }
```

### Exhaustive Pattern Matching

```java
// Compiler verifies all permitted subtypes handled
public double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> t.base() * t.height() / 2;
        // No default needed - exhaustive!
    };
}
```

### Sealed + Records = Algebraic Data Types

```java
// Option/Maybe pattern
public sealed interface Option<T> permits Some<T>, None<T> { }

public record Some<T>(T value) implements Option<T> { }
public record None<T>() implements Option<T> { }

// Usage
public <T> T getOrElse(Option<T> opt, T defaultValue) {
    return switch (opt) {
        case Some(var value) -> value;
        case None() -> defaultValue;
    };
}

// Result/Either pattern
public sealed interface Result<T, E> 
    permits Success<T, E>, Failure<T, E> { }

public record Success<T, E>(T value) implements Result<T, E> { }
public record Failure<T, E>(E error) implements Result<T, E> { }
```

---

## Pattern Matching (Java 16-21+)

### instanceof Pattern Matching (Java 16+)

```java
// Old way
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.toUpperCase());
}

// New way
if (obj instanceof String s) {
    System.out.println(s.toUpperCase());
}

// Scope: s only in true branch
```

### Switch Expressions (Java 14+)

```java
// Expression form (returns value)
String dayType = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "Weekday";
    case SATURDAY, SUNDAY -> "Weekend";
    default -> throw new IllegalStateException("Invalid day: " + day);
};

// Statement form (Java 12+)
switch (day) {
    case MONDAY -> System.out.println("Start of week");
    case FRIDAY -> System.out.println("TGIF!");
    default -> System.out.println("Regular day");
}
```

### Switch Pattern Matching (Java 21+)

```java
// Type patterns in switch
static String format(Object obj) {
    return switch (obj) {
        case Integer i -> "int: " + i;
        case Long l -> "long: " + l;
        case Double d -> String.format("double: %.2f", d);
        case String s -> "string: " + s;
        case List<?> list -> "list of size " + list.size();
        case null -> "null";
        default -> "unknown: " + obj.getClass().getSimpleName();
    };
}
```

### Record Patterns (Java 21+)

```java
record Point(int x, int y) { }
record Rectangle(Point topLeft, Point bottomRight) { }

// Deconstruct records
static void printRect(Rectangle rect) {
    if (rect instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) {
        System.out.printf("Rect: (%d,%d) to (%d,%d)%n", x1, y1, x2, y2);
    }
}

// Nested patterns
record Employee(String name, Address address) { }
record Address(String city, String zip) { }

static String city(Employee e) {
    return switch (e) {
        case Employee(var name, Address(var city, _)) -> city;
        case null -> "unknown";
    };
}
```

### Guarded Patterns (Java 21+)

```java
static String categorize(int score) {
    return switch (score) {
        case int s when s >= 90 -> "A";
        case int s when s >= 80 -> "B";
        case int s when s >= 70 -> "C";
        case int s when s >= 60 -> "D";
        default -> "F";
    };
}

// Combined with type patterns
static String describe(Number n) {
    return switch (n) {
        case Integer i when i > 0 -> "positive int: " + i;
        case Integer i when i < 0 -> "negative int: " + i;
        case Double d when d.isNaN() -> "NaN";
        case Number num -> "number: " + num;
        default -> "zero or other";
    };
}
```

---

## Real-World Patterns

### Domain Modeling with Records + Sealed

```java
// Event sourcing
public sealed interface DomainEvent permits OrderPlaced, OrderShipped, OrderCancelled { }

public record OrderPlaced(String orderId, List<OrderItem> items, Instant timestamp) 
    implements DomainEvent { }

public record OrderShipped(String orderId, String trackingNumber, Instant timestamp) 
    implements DomainEvent { }

public record OrderCancelled(String orderId, String reason, Instant timestamp) 
    implements DomainEvent { }

// Event handler - exhaustive
public void handle(DomainEvent event) {
    switch (event) {
        case OrderPlaced e -> orderService.place(e);
        case OrderShipped e -> orderService.ship(e);
        case OrderCancelled e -> orderService.cancel(e);
    }
}
```

### Parser Combinators

```java
sealed interface ParseResult<T> permits Success<T>, Failure<T> { }

record Success<T>(T value, String remaining) implements ParseResult<T> { }
record Failure<T>(String error, String remaining) implements ParseResult<T> { }

ParseResult<AST> parse(String input) {
    return switch (parseExpression(input)) {
        case Success(var ast, var rest) when rest.isBlank() -> new Success<>(ast, "");
        case Success(var ast, var rest) -> new Failure<>("Trailing input: " + rest, rest);
        case Failure(var err, var rest) -> new Failure<>(err, rest);
    };
}
```

---

## Migration Guide

| Before | After |
|--------|-------|
| POJO with getters/setters | `record` |
| `instanceof` + cast | `instanceof Type var` |
| `if-else` chains | `switch` expressions |
| Visitor pattern | Sealed + switch |
| `Optional` for nullable | Sealed `Option<T>` |
| Exception for control flow | `Result<T, E>` sealed |