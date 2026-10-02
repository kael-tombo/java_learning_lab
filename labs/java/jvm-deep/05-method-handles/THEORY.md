# THEORY — Method Handles & invokedynamic

## Overview

Method Handles (JEP 274) and `invokedynamic` (JEP 292) provide low-level, efficient mechanisms for dynamic method invocation — the backbone of lambdas, dynamic languages, and framework internals.

---

## 1. Method Handles

### What is a Method Handle?

A **MethodHandle** is a typed, directly executable reference to a method, constructor, field, or similar low-level operation. Unlike reflection, it's:
- **Directly executable** (no reflective overhead after linkage)
- **Strongly typed** (MethodType)
- **Composable** (transform, filter, combine)
- **Secure** (access checks at creation, not invocation)

---

## 2. Obtaining Method Handles

### Lookup

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();

// Static method
MethodHandle mh = lookup.findStatic(Math.class, "sqrt", 
    MethodType.methodType(double.class, double.class));

// Instance method
MethodHandle mh = lookup.findVirtual(String.class, "substring",
    MethodType.methodType(String.class, int.class, int.class));

// Constructor
MethodHandle mh = lookup.findConstructor(ArrayList.class,
    MethodType.methodType(ArrayList.class));

// Field getter/setter
MethodHandle getter = lookup.findGetter(Point.class, "x", int.class);
MethodHandle setter = lookup.findSetter(Point.class, "x", int.class);
```

### Access Modes

| Method | Access Check |
|--------|--------------|
| `findStatic` | At lookup time |
| `findVirtual` | At lookup time (receiver type) |
| `findConstructor` | At lookup time |
| `findVirtual` / `findSpecial` | At linkage time |

---

## 3. MethodType

Describes method signature: `(parameterTypes...)returnType`

```java
MethodType mt = MethodType.methodType(
    double.class,      // return type
    double.class, double.class  // parameters
);

// Factory methods
MethodType.methodType(void.class);                    // ()V
MethodType.methodType(int.class, int.class);          // (I)I
MethodType.methodType(String.class, int.class, int.class); // (II)Ljava/lang/String;
MethodType.methodType(void.class, int[].class);       // ([I)V
```

---

## 4. Method Handle Transformations

### Core Operations

| Operation | Method | Purpose |
|-----------|--------|---------|
| **Filter arguments** | `filterArguments` | Transform arguments before call |
| **Filter return** | `filterReturnValue` | Transform return value |
| **Bind argument** | `bindTo` | Bind first argument (currying) |
| **Spread arguments** | `asSpreader` | Expand array into arguments |
| **Collect arguments** | `asCollector` | Collect arguments into array |
| **Permute** | `asVarargsCollector` | Varargs support |
| **Drop args** | `dropArguments` | Ignore arguments |
| **Guard** | `guardWithTest` | Conditional execution |

### Examples

```java
// Filter arguments: double each input
MethodHandle mh = ...;
mh = mh.filterArguments(
    MethodHandles.identity(int.class),  // arg 0
    MethodHandles.constant(int.class, 2) // arg 1 = 2
);

// Bind first argument
MethodHandle bound = mh.bindTo(42); // (int x) -> f(42, x)

// Spread array to arguments
MethodHandle spreader = mh.asSpreader(int[].class, 2); // int[] -> (int, int)

// Collect arguments into array
MethodHandle collector = mh.asCollector(int[].class, 2); // (int, int) -> int[]
```

---

## 5. invokedynamic

### How It Works

```java
// Java source
Runnable r = () -> System.out.println("hello");

// Compiles to invokedynamic:
// Bootstrap: LambdaMetafactory.metafactory
// Static args: (Ljava/lang/Runnable;)V, ()V
// Dynamic args: (captured vars)
```

### Bootstrap Method

```java
CallSite bootstrap(MethodHandles.Lookup caller, 
                   String name, 
                   MethodType type, 
                   Object... staticArgs) {
    // Return CallSite with target MethodHandle
    return new ConstantCallSite(targetMethodHandle);
}
```

### Call Site Types

| Type | Behavior |
|--------|----------|
| `ConstantCallSite` | Immutable target (lambdas) |
| `VolatileCallSite` | Target can change, volatile read |
| `MutableCallSite` | Target can change, sync on access |

---

## 6. Practical Patterns

### Lambda Compilation

```java
// Java source
Runnable r = () -> System.out.println("hello");

// Becomes (simplified):
invokedynamic #0:invokeStatic(
    LambdaMetafactory.metafactory,
    (Ljava/lang/Runnable;)V,
    ()V,
    ()V
);
```

### Method Handle Composition

```java
// Compose: f(g(x))
MethodHandle composed = MethodHandles.filterArguments(f, 0, g);

// Pipeline: x -> f -> g -> h
MethodHandle pipeline = MethodHandles.filterArguments(h, 0, g)
                                   .filterArguments(0, f);
```

---

## 7. Performance Considerations

| Aspect | MethodHandle | Reflection | Direct Call |
|--------|--------------|------------|-------------|
| First call | Link + JIT | Slow | JIT compiles |
| Warm call | Inlined by JIT | Slow | Inlined |
| Memory | Low | High | Minimal |
| Security | Checks at linkage | Checks every call | None |

**Best practice**: Warm up MethodHandles before measuring; use in hot paths after warmup.