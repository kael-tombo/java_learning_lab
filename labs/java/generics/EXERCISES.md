# EXERCISES — Generics

## 1. Generic Box (Beginner)

Create a generic `Box<T>` class that can hold any type. Add methods:
- `set(T value)` - set the value
- `T get()` - get the value
- `boolean isEmpty()` - check if empty

Test with `Box<String>`, `Box<Integer>`, `Box<List<String>>`.

---

## 2. Generic Method (Beginner)

Write a generic method `swap(T[] array, int i, int j)` that swaps elements at indices i and j.

Test with `Integer[]`, `String[]`, and a custom class array.

---

## 2. Bounded Type Parameters (Intermediate)

Create a class `NumberBox<T extends Number>` with:
- `T value` field
- `double doubleValue()` - returns `value.doubleValue()`
- `int intValue()` - returns `value.intValue()`

Test with `Integer`, `Double`, `BigDecimal`.

---

## 3. Wildcards (Intermediate)

Given:
```java
List<? extends Number> numbers = Arrays.asList(1, 2, 3, 4.5, 5L);
List<? super Integer> integers = new ArrayList<>();
```

Explain:
1. Why can you read from `numbers` but not add to it?
2. Why can you add to `integers` but not safely read specific types?
3. What does `? extends Number` mean vs `? super Integer`?

---

## 4. PECS Principle (Intermediate)

Complete the following methods using PECS (Producer Extends, Consumer Super):

```java
// Producer: read from collection
public void printAll(Collection<? extends Number> numbers) { ... }

// Consumer: add to collection
public void addIntegers(Collection<? super Integer> integers) { ... }

// Both: copy from source to destination
public static <T> void copy(List<? super T> dest, List<? extends T> src) { ... }
```

---

## 4. Type Erasure (Advanced)

Explain what happens at runtime to:
```java
List<String> strings = new ArrayList<>();
List<Integer> integers = new ArrayList<>();
```

Why does `strings.getClass() == integers.getClass()` return `true`?
What happens with `instanceof List<String>`?

---

## 5. Bridge Methods (Advanced)

Given:
```java
class Node<T> implements Comparable<Node<T>> {
    T value;
    
    @Override
    public int compareTo(Node<T> other) {
        return 0;
    }
}
```

What bridge method does the compiler generate? Why is it needed?

---

## 6. Recursive Type Bounds (Advanced)

Implement a `Builder<T extends Builder<T>>` pattern:

```java
class Builder<T extends Builder<T>> {
    T withName(String name) { ... return (T) this; }
    T build() { return (T) this; }
}

class PersonBuilder extends Builder<PersonBuilder> { ... }
```

Explain why `T extends Builder<T>` is needed.

---

## 8. Type Tokens (Advanced)

Implement a `TypeReference<T>` class that captures generic type at runtime:

```java
TypeReference<List<String>> ref = new TypeReference<List<String>>() {};
Type type = ref.getType(); // Should be ParameterizedType: List<String>
```

Hint: Use anonymous subclass to capture type.