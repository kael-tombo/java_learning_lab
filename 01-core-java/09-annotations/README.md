# Module 09: Annotations & Reflection API

<div align="center">

![Module](https://img.shields.io/badge/Module-09-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-green?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-31%20Passing-success?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-orange?style=for-the-badge)

**Master Custom Annotations, Meta-Annotations, and Runtime Metaprogramming**

</div>

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Learning Objectives](#learning-objectives)
3. [Module Structure](#module-structure)
4. [Architecture: How Annotations & Reflection Work](#architecture-how-annotations--reflection-work)
5. [Elite Frameworks in this Module](#elite-frameworks-in-this-module)
6. [Lab & Test Suites](#lab--test-suites)
7. [Common Traps & Edge Cases](#common-traps--edge-cases)
8. [FAANG Interview Prep](#faang-interview-prep)

---

## 🎯 Overview

Annotations provide structured metadata about program elements without altering execution logic directly. When combined with the Java Reflection API (`java.lang.reflect`), annotations form the backbone of modern Java frameworks including Spring, Hibernate, JUnit 5, and Jackson.

### Core Metaprogramming Capabilities
- 🏷️ **Declarative Semantics**: Replacing imperative boilerplate with expressive declarations (`@ValidateString`, `@Autowired`, `@JsonSerializable`).
- 🔍 **Runtime Introspection**: Inspecting classes, fields, methods, constructors, and annotations at runtime.
- ⚙️ **Dynamic Invocation**: Invoking methods, reading/modifying private fields, and instantiating types dynamically.
- 🎭 **Dynamic Proxies**: Generating runtime interceptors (`java.lang.reflect.Proxy`) for aspect-oriented cross-cutting concerns.

---

## 📖 Learning Objectives

- [x] Create custom annotations with target boundaries (`@Target`) and lifecycle retention policies (`@Retention`).
- [x] Apply meta-annotations: `@Retention`, `@Target`, `@Documented`, `@Inherited`, and `@Repeatable`.
- [x] Inspect class structures using `Class<?>`, `Field`, `Method`, `Constructor`, and `Modifier`.
- [x] Build a declarative **Validation Engine** validating string lengths, regex patterns, and numeric ranges.
- [x] Implement a lightweight **JSON Serializer** respecting `@JsonField` mappings and `@JsonIgnore` directives.
- [x] Construct a lightweight **Dependency Injection (DI) Container** resolving `@Autowired` fields and `@Component` types.
- [x] Design a custom **JUnit-style Test Runner** discovering and executing `@Test` methods with order priority and timeout constraints.

---

## 📁 Module Structure

```
09-annotations/
├── pom.xml                                    # Maven configuration & reactor registration
├── src/
│   ├── main/java/com/learning/annotations/
│   │   ├── Lab.java                           # Foundational lab: built-ins, custom annotations, inspection
│   │   └── EliteAnnotationsTraining.java      # Framework implementations (Validation, JSON, DI, Test Runner)
│   └── test/java/com/learning/annotations/
│       ├── AnnotationTests.java               # Standard lab test suite
│       └── EliteAnnotationsTrainingTest.java  # Comprehensive test suite covering all 5 engines (31 tests)
├── QUICK_REFERENCE.md                         # Cheat sheet for retention policies & reflection methods
├── DEEP_DIVE.md                               # Bytecode representation (RuntimeVisibleAnnotations)
├── EDGE_CASES.md                              # AccessibleObject setAccessible vs modules, security managers
├── EXERCISES.md                               # Hands-on challenge exercises
└── INTERVIEW_PREP.md                          # Senior Java engineer interview questions
```

---

## 🏗️ Architecture: How Annotations & Reflection Work

```
Source Code (.java)  ──[javac]──>  Bytecode (.class)
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
               RetentionPolicy.SOURCE           RetentionPolicy.CLASS
              (Stripped by compiler)          (Present in .class; stripped at load)
                         │
                         ▼
               RetentionPolicy.RUNTIME
        (Stored in RuntimeVisibleAnnotations attribute table)
                         │
                         ▼ [JVM ClassLoader]
               Loaded into Metaspace
                         │
                         ▼ [Reflection API]
          Class.getAnnotation(Class<A>) -> Dynamic Proxy implementation of A
```

---

## 💎 Elite Frameworks in [EliteAnnotationsTraining.java](./src/main/java/com/learning/annotations/EliteAnnotationsTraining.java)

1. **Validation Engine**: Validates domain objects against `@ValidateString(minLength, maxLength, regex)` and `@ValidateNumber(min, max)` without third-party libraries.
2. **JSON Serializer**: Recursively reflects over fields, renames keys according to `@JsonField(name)`, ignores fields marked with `@JsonIgnore`, and serializes objects into valid JSON strings.
3. **DI Container**: Scans and instantiates classes, builds an internal dependency graph, and injects instances into fields marked with `@Autowired`.
4. **Custom Test Runner**: Locates `@Test` annotated methods, evaluates expected exceptions, enforces timeouts, sorts by priority, and produces a structured test report.

---

## 🧪 Tests Execution

Run the complete test suite:

```bash
mvn test -f 01-core-java/09-annotations/pom.xml
```

Expected output:
```text
[INFO] Results:
[INFO] Tests run: 31, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```
