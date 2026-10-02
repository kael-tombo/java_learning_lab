# THEORY — Java Generics

## Overview

Generics enable types (classes and interfaces) to be parameters when defining classes, interfaces, and methods. They provide **compile-time type safety** and eliminate casts.

---

## 1. Generic Types

### Generic Classes

```java
public class Box<T> {
    private T value;
    
    public void set(T value) { this.value = value; }
    public T get() { return value; }
}

// Usage
Box<String> stringBox = new Box<>();
stringBox.set("hello");
String s = stringBox.get(); // Type-safe, no cast
```

### Generic Interfaces

```java
public interface Repository<T> {
    T findById(ID id);
    List<T> findAll();
    void save(T entity);
}
```

---

## 2. Type Parameters

### Naming Conventions

| Convention | Meaning |
|------------|---------|
| `T` | Type |
| `E` | Element (collections) |
| `K` | Key (maps) |
| `V` | Value (maps) |
| `N` | Number |
| `R` | Return type |
| `S, T, U` | Multiple type params |

---

## 2. Generic Methods

```java
// Generic method
public static <T> void swap(T[] array, int i, int j) {
    T temp = array[i];
    array[i] = array[j];
    array[j] = temp;
}

// With bounds
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) > 0 ? a : b;
}

// Multiple bounds
public static <T extends Number & Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) > 0 ? a : b;
}
```

---

## 3. Bounded Type Parameters

### Upper Bounds (`extends`)

```java
// T must be Number or subclass
public class NumberBox<T extends Number> {
    private T value;
    
    public double doubleValue() {
        return value.doubleValue(); // Safe: Number has doubleValue()
    }
}

// Multiple bounds: T extends A & B
public static <T extends Comparable<T> & Serializable> void sort(List<T> list) {
    Collections.sort(list);
}
```

### Lower Bounds (`super`)

```java
// Consumer: accepts T or supertype
public void addAll(List<? super Number> list, Number n) {
    list.add(n); // Can add Number or subtype
}

// PECS: Producer Extends, Consumer Super
// List<? extends T> - read only (producer)
// List<? super T> - write only (consumer)
```

---

## 4. Wildcards

### Unbounded Wildcard `?`

```java
public void printList(List<?> list) {
    for (Object obj : list) {
        System.out.println(obj);
    }
}
```

### Upper Bounded Wildcard `? extends T`

```java
// Producer: can READ T or subtypes
public double sum(List<? extends Number> numbers) {
    double sum = 0;
    for (Number n : numbers) {
        sum += n.doubleValue(); // read only
    }
    return sum;
}
```

### Lower Bounded Wildcard `? super T`

```java
// Consumer: can WRITE T or supertypes
public void addNumbers(List<? super Integer> list) {
    list.add(1);      // OK: Integer is Integer
    list.add(42);     // OK
    list.add(3.14);   // ERROR: Double not Integer
}

// PECS: Producer Extends, Consumer Super
```

---

## 4. Type Erasure

### What Gets Erased

```java
// Compile time
List<String> list = new ArrayList<>();

// Runtime (after erasure)
List list = new ArrayList(); // Raw type
```

### Erasure Rules

1. Replace type parameters with bounds (or `Object` if unbounded)
2. Insert casts where needed
3. Bridge methods for polymorphism

```java
// Source
class Box<T> { void set(T t) {} }

// Erased
class Box {
    void set(Object t) {}
}
```

### Bridge Methods

```java
class Node<T> implements Comparable<Node<T>> {
    T value;
    
    @Override
    public int compareTo(Node<T> other) {
        return 0;
    }
}

// Compiler generates bridge:
public int compareTo(Comparable other) {
    return compareTo((Node<T>) other);
}
```

---

## 3. Type Erasure Consequences

### Cannot Do With Generics

| Operation | Example |
|-----------|---------|
| `new T()` | `new T()` — compile error |
| `new T[]` | `new T[10]` — compile error |
| `instanceof T` | `obj instanceof T` — compile error |
| `T.class` | `T.class` — compile error |
| Primitive types | `List<int>` — compile error |

### Workarounds

```java
// Class token
public <T> T create(Class<T> clazz) throws ReflectiveOperationException {
    return clazz.getDeclaredConstructor().newInstance();
}

// Array creation
T[] array = (T[]) Array.newInstance(clazz, size);

// Class literal
Class<String> clazz = String.class;
```

---

## 4. Reifiable Types

### Reifiable Types

Types where type info is fully available at runtime:
- Primitive types
- Non-generic types
- Unbounded wildcards: `List<?>`, `Map<?, ?>`
- Raw types (raw types are reifiable)

### Non-Reifiable Types

Parameterized types with type arguments erased:
- `List<String>`
- `Map<String, Integer>`
- `List<T>`

```java
// Legal
List<?> list1 = new ArrayList<String>();

// Illegal
// List<String> list2 = new ArrayList<Object>(); // Error
// list instanceof List<String> // Error: non-reifiable
```

---

## 4. Generics and Arrays

### Arrays Are Covariant, Generics Are Invariant

```java
// Arrays: covariant (covariance)
Number[] numbers = new Integer[10]; // OK
numbers[0] = 3.14; // Runtime ArrayStoreException!

// Generics: invariant
List<Number> numbers = new ArrayList<Integer>(); // Compile error!
```

### Why Invariance?

```java
List<Number> numbers = new ArrayList<Integer>(); // If allowed...
numbers.add(3.14); // Integer list now has Double!
Integer i = integers.get(0); // ClassCastException at runtime
```

---

## 4. Advanced Patterns

### Recursive Type Bounds (F-Bounded Polymorphism)

```java
// Self-referential bound
public interface Comparable<T> {
    int compareTo(T other);
}

class Employee implements Comparable<Employee> { ... }

// Builder pattern
class Builder<T extends Builder<T>> {
    T withName(String name) { ... return (T) this; }
}
```

### Type Tokens (Super Type Tokens)

```java
// Capture generic type at runtime
TypeReference<List<String>> ref = new TypeReference<List<String>>() {};

Type type = ref.getType(); // ParameterizedType: List<String>
```

---

## 5. Generic Best Practices

### Do's

```java
// Use generics everywhere
List<String> list = new ArrayList<>(); // Diamond operator

// Use bounded wildcards for flexibility
public void process(Collection<? extends Number> numbers) { ... }

// Prefer generic methods for type inference
public static <T> List<T> asList(T... elements) { ... }
```

### Don'ts

```java
// Don't use raw types
List list = new ArrayList(); // Raw type - loses type safety

// Don't mix generics and varargs unsafely
@SafeVarargs // Suppresses warning if safe
public static <T> void addAll(List<T> list, T... elements) { ... }

// Avoid raw types in new code
// List list = new ArrayList(); // Raw type - avoid
```

---

## 5. Type Tokens (Super Type Tokens)

```java
// Capture generic type at runtime
TypeReference<List<String>> ref = new TypeReference<List<String>>() {};

Type type = ref.getType(); // ParameterizedType: List<String>

// Usage in libraries like Jackson
ObjectMapper mapper = new ObjectMapper();
List<String> list = mapper.readValue(json, new TypeReference<List<String>>() {});
```

---

## 6. Migration & Migration Compatibility

### Raw Types

```java
// Legacy code
List list = new ArrayList(); // Raw type

// Migration
List<String> list = new ArrayList<>(); // Parameterized
```

### Migration Strategy

1. Add type parameters gradually
2. Use `@SuppressWarnings("unchecked")` sparingly
3. Enable `-Xlint:unchecked` for warnings
4. Prefer generic methods over raw types