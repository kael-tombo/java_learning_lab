# THEORY — Java Records & Sealed Classes (Part 2)

## 6. Serialization

### Records

```java
record Point(int x, int y) implements Serializable {
    // Default: component-based serialization
    
    // Custom:
    private void writeObject(ObjectOutputStream out) throws IOException {
        out.defaultWriteObject();
    }
}
```

### Sealed Classes

```java
sealed interface Shape permits Circle, Rectangle {
    // Use explicit serialization with type discriminator
}
```

---

## 5. Pattern Matching for switch (Java 21+)

### Exhaustiveness Checking

```java
static double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        // No default needed - exhaustive!
    };
}
```

### Record Patterns

```java
static void print(Object obj) {
    if (obj instanceof Point(int x, int y)) {
        System.out.println("Point: " + x + ", " + y);
    }
}
```

---

## 5. Serialization

### Records

```java
record Point(int x, int y) implements Serializable {
    // Default: component-based serialization
    
    // Custom:
    private void writeObject(ObjectOutputStream out) throws IOException {
        out.defaultWriteObject();
    }
}
```

### Sealed Classes

```java
sealed interface Shape permits Circle, Rectangle {
    // Use explicit serialization with type discriminator
}
```

---

## 6. Best Practices

### Records

- ✅ Use for immutable data carriers
- ✅ Add validation in compact constructor
- ✅ Use for DTOs, events, map keys, cache keys
- ❌ Don't use for mutable entities
- ❌ Don't add mutable state

### Sealed Classes

- ✅ Use for closed hierarchies (known implementations)
- ✅ Enable exhaustive pattern matching
- ✅ Document `permits` clearly
- ❌ Don't seal if hierarchy must be extensible by third parties

### Pattern Matching

- ✅ Use `switch` expressions for exhaustiveness
- ✅ Use record patterns for deconstruction
- ❌ Don't mix with `instanceof` unnecessarily

---

## 6. Migration Guide

### From Classes to Records

```java
// Before
class Point {
    private final int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }
    public int getX() { return x; }
    public int getY() { return y; }
    // equals, hashCode, toString...
}

// After
record Point(int x, int y) { }
```

### From Enum to Sealed

```java
// Before: limited extensibility
enum Shape { CIRCLE, RECTANGLE }

// After: extensible with controlled hierarchy
sealed interface Shape permits Circle, Rectangle { }
record Circle(double radius) implements Shape { }
record Rectangle(double w, double h) implements Shape { }
```

---

## 6. Best Practices

### Records

- ✅ Use for immutable data carriers
- ✅ Add validation in compact constructor
- ✅ Use for DTOs, events, map keys, cache keys
- ❌ Don't use for mutable entities
- ❌ Don't add mutable state

### Sealed Classes

- ✅ Use for closed hierarchies (known implementations)
- ✅ Enable exhaustive pattern matching
- ✅ Document `permits` clearly
- ❌ Don't seal if hierarchy must be extensible by third parties

### Pattern Matching

- Use `switch` expressions for exhaustiveness
- Prefer record patterns over `instanceof` + cast
- Use `instanceof` pattern for simple checks

---

## Migration Guide

### From Classes to Records

```java
// Before
class Point {
    private final int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }
    public int getX() { return x; }
    public int getY() { return y; }
    // equals, hashCode, toString...
}

// After
record Point(int x, int y) { }
```

### From Enum to Sealed

```java
// Before: limited extensibility
enum Shape { CIRCLE, RECTANGLE }

// After: extensible with controlled hierarchy
sealed interface Shape permits Circle, Rectangle { }
record Circle(double radius) implements Shape { }
record Rectangle(double w, double h) implements Shape { }
```

---

## Best Practices

### Records

- ✅ Use for immutable data carriers (DTOs, events, keys)
- ✅ Validate in compact constructor
- ✅ Use for DTOs, events, map keys, cache keys
- ❌ Don't use for mutable entities
- ❌ Don't add mutable state

### Sealed Classes

- ✅ Use for closed hierarchies (known implementations)
- ✅ Enable exhaustive pattern matching
- ✅ Document `permits` clearly
- ❌ Don't seal if hierarchy must be extensible by third parties

### Pattern Matching

- Use `switch` expressions for exhaustiveness
- Prefer record patterns over `instanceof` + cast
- Use `instanceof` pattern for simple checks