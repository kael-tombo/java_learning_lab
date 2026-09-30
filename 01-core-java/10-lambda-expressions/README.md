# Module 10: Lambda Expressions & Functional Programming

<div align="center">

![Module](https://img.shields.io/badge/Module-10-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-green?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-22%20Passing-success?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-orange?style=for-the-badge)

**Master Java Lambda Expressions, Functional Interfaces, and Higher-Order Patterns**

</div>

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Learning Objectives](#learning-objectives)
3. [Module Structure](#module-structure)
4. [Deep Dive: JVM Internals (`invokedynamic`)](#deep-dive-jvm-internals-invokedynamic)
5. [Elite Functional Patterns](#elite-functional-patterns)
6. [Lab & Test Suites](#lab--test-suites)
7. [Common Traps & Edge Cases](#common-traps--edge-cases)
8. [FAANG Interview Prep](#faang-interview-prep)

---

## 🎯 Overview

Lambda expressions introduced in Java 8 revolutionized Java programming by enabling functional paradigms on top of the object-oriented foundation. Rather than syntactic sugar for anonymous inner classes, Java lambdas leverage JVM-level bytecode instructions (`invokedynamic`) for near-zero allocation overhead.

### Key Advantages
- 🚀 **Zero Anonymous Class Proliferation**: Lambdas do not generate separate `.class` files on disk.
- ⚡ **Lazy Translation via `invokedynamic`**: The JVM emits a `CallSite` dynamically linked via `LambdaMetafactory`.
- 🧩 **Higher-Order Composition**: Functions can be passed as arguments, returned, curried, and decorated.
- 🛡️ **Predictable Concurrency**: Pure functions without side effects guarantee thread safety.

---

## 📖 Learning Objectives

- [x] Master lambda syntax: parameter elision, type annotations, and expression vs block bodies.
- [x] Standardize on Single Abstract Method (`@FunctionalInterface`) contracts.
- [x] Master core built-ins: `Predicate`, `Function`, `Consumer`, `Supplier`, `BiFunction`, and primitive variants.
- [x] Leverage Method References (`String::toUpperCase`, `System.out::println`, `ArrayList::new`).
- [x] Implement **Currying** and **Partial Application** for multi-argument functions.
- [x] Build resilient functional pipelines with checked exception lifting (`Result<T>` monad pattern).
- [x] Achieve **Tail-Call Optimization (TCO)** in Java using the **Trampoline pattern** ($O(1)$ stack usage).
- [x] Implement context-injected services using the **Reader Monad**.
- [x] Design reactive fault-tolerance decorators with functional **Circuit Breakers**.

---

## 📁 Module Structure

```
10-lambda-expressions/
├── pom.xml                                    # Maven reactor module definition
├── src/
│   ├── main/java/com/learning/lambda/
│   │   ├── Lab.java                           # Foundational lab & syntax demos (8 parts)
│   │   ├── MathOperation.java                 # Custom package-level SAM interface
│   │   └── EliteLambdaTraining.java           # Production-grade functional patterns (TCO, Monads, Decorators)
│   └── test/java/com/learning/lambda/
│       ├── LambdaTests.java                   # Basic syntax & operation test suite
│       └── EliteLambdaTrainingTest.java       # Comprehensive JUnit 5 nested test suite (22 tests)
├── QUICK_REFERENCE.md                         # Syntax cheat sheet & decision tree
├── DEEP_DIVE.md                               # Theory, closure mechanics, and compiler lowering
├── EDGE_CASES.md                              # Variable capture, shadowing, and exception pitfalls
├── EXERCISES.md                               # Practice problem sets
└── INTERVIEW_PREP.md                          # Behavioral and technical interview questions
```

---

## 🔬 Deep Dive: JVM Internals (`invokedynamic`)

Anonymous inner classes instantiate a new object every time (`new Runnable() { ... }`), consuming heap and polluting the ClassLoader. 

Java lambdas compile to `invokedynamic` (INDY):
1. **Bytecode Emission**: The compiler places an `invokedynamic` instruction pointing to `LambdaMetafactory.metafactory`.
2. **First Invocation**: The JVM invokes the bootstrap method, generating a dynamic `CallSite` backed by an anonymous VM-anonymous class or method handle.
3. **Subsequent Calls**: Direct dispatch at native CPU speeds without reflection overhead.
4. **Non-capturing Lambdas**: Stateless lambdas (referencing no outer variables) are cached as singletons, incurring **zero heap allocations** per invocation.

---

## 💎 Elite Functional Patterns in [EliteLambdaTraining.java](./src/main/java/com/learning/lambda/EliteLambdaTraining.java)

### 1. Stack-Safe Recursion via Trampoline
Java does not natively support Tail-Call Optimization (TCO), causing `StackOverflowError` on deep recursion. Our `Trampoline<T>` pattern converts recursive calls into an iterative loop on the heap:

```java
Trampoline<Long> sum = sumRecursively(100_000L, 0L);
long result = sum.run(); // Executes 100,000 steps with O(1) stack frames!
```

### 2. Functional Context Injection (Reader Monad)
Eliminates mutable config passing by treating dependencies as pure functional mappings:

```java
Reader<Environment, String> dbReader = env -> env.dbUrl();
Reader<Environment, Integer> timeoutReader = env -> env.timeoutSec();

Reader<Environment, String> client = dbReader.flatMap(db ->
    timeoutReader.map(to -> "Connect to " + db + " [timeout=" + to + "s]")
);
```

### 3. Functional Circuit Breaker Decorator
Stateful higher-order wrapper managing `CLOSED`, `OPEN`, and `HALF_OPEN` states without external framework dependencies:

```java
CircuitBreaker breaker = new CircuitBreaker(failureThreshold = 3, resetTimeoutMs = 1000);
Supplier<Result<Data>> resilientCall = breaker.decorate(() -> remoteRpcService.fetch());
```

---

## 🧪 Tests Execution

Run the complete test suite:

```bash
mvn test -f 01-core-java/10-lambda-expressions/pom.xml
```

Expected output:
```text
[INFO] Results:
[INFO] Tests run: 22, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```
