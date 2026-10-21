# Best Practices — Internal Mechanics

## How Effective Java Patterns Work

### Builder Pattern Internals

The Builder pattern uses a mutable companion class to construct an immutable target. This avoids the telescoping constructor anti-pattern and improves readability by naming each parameter. Inner builder classes have access to the outer class's private constructor.

### equals/hashCode Contract

The JVM uses `hashCode()` for hash-based collections (HashMap, HashSet). The contract requires:
1. If two objects are equal via `equals()`, they must have the same hash code
2. If two objects have the same hash code, they may or may not be equal
3. Hash code must be consistent across invocations within one execution

### try-with-resources

The compiler desugars try-with-resources into:
1. A try-finally block closing each resource in reverse order
2. Suppressed exceptions are added to the primary exception
3. Resources must implement `AutoCloseable`

### Enum Singleton

Enum singletons provide:
1. JVM guarantee of single instantiation
2. Protection against reflection-based attacks
3. Serialization safety (enum serialization is handled specially)
4. Thread-safe initialization by the class loader

### Defensive Programming

Defensive copies protect internal state by:
1. Copying mutable objects on input (constructor)
2. Copying mutable objects on output (getters)
3. Using unmodifiable wrappers for collections
4. Failing fast with `Objects.requireNonNull()`
