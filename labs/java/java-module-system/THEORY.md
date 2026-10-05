# THEORY — Java Module System (JPMS)

## Overview

The Java Platform Module System (JPMS, JSR 376) introduces **strong encapsulation** and **explicit dependencies** via `module-info.java`. It replaces the fragile classpath with a reliable module graph.

---

## 1. Module Declaration

```java
module com.example.app {
    // Exports: public API accessible to other modules
    exports com.example.api;
    exports com.example.spi to com.example.impl; // qualified export
    
    // Requires: dependencies on other modules
    requires java.sql;
    requires transitive java.logging; // transitive: consumers get it too
    requires static java.xml;         // optional at runtime
    
    // Services
    uses com.example.spi.Service;
    provides com.example.spi.Service with com.example.impl.ServiceImpl;
    
    // Opens for reflection (deep reflection)
    opens com.example.internal to com.example.test;
}
```

---

## 2. Module Directives

| Directive | Purpose |
|-----------|---------|
| `exports pkg` | Public API, accessible to all modules |
| `exports pkg to M` | Qualified export (only module M) |
| `requires M` | Depends on module M |
| `requires transitive M` | Consumers also get M |
| `requires static M` | Optional at runtime |
| `uses S` | Declares service consumer |
| `provides S with I` | Service provider registration |
| `opens pkg` | Deep reflection access |
| `opens pkg to M` | Qualified deep reflection |

---

## 2. Module Resolution

### Module Graph

```
App Module
    requires → Logging Module
    requires → Database Module
    requires → Config Module
        requires → Logging Module (transitive)
```

**Resolution**: JVM builds module graph at startup. Fails fast on:
- Missing modules
- Circular dependencies
- Split packages (same package in multiple modules)

---

## 2. Readability & Accessibility

| Keyword | Readability | Deep Reflection |
|---------|-------------|-----------------|
| `requires` | ✅ | ❌ |
| `requires transitive` | ✅ (transitive) | ❌ |
| `opens` | ✅ | ✅ (deep) |
| `exports` | ✅ | ❌ |

| Access | `exports` | `opens` |
|--------|-----------|---------|
| Public types | ✅ | ✅ |
| Public members | ✅ | ✅ |
| Protected/private | ❌ | ✅ (via `setAccessible`) |

---

## 3. Services (SPI)

### Service Provider Interface

```java
// API module
public interface PaymentProcessor {
    void process(Payment p);
}
```

### Provider Module

```java
module com.example.paypal {
    requires com.example.api;
    provides com.example.api.PaymentProcessor
        with com.example.paypal.PayPalProcessor;
}
```

### Consumer Module

```java
module com.example.app {
    requires com.example.api;
    uses com.example.api.PaymentProcessor;
}

// Usage
ServiceLoader.load(PaymentProcessor.class)
    .forEach(p -> p.process(payment));
```

---

## 3. ServiceLoader & SPI

### Service Provider Interface

```java
// API module
public interface PaymentProcessor {
    void process(Payment p);
}
```

### Provider Registration

```java
// Provider module
module com.example.paypal {
    requires com.example.api;
    provides com.example.api.PaymentProcessor
        with com.example.paypal.PayPalProcessor;
}
```

### Consumer Usage

```java
module com.example.app {
    requires com.example.api;
    uses com.example.api.PaymentProcessor;
}

// Runtime
ServiceLoader.load(PaymentProcessor.class)
    .forEach(p -> p.process(payment));
```

---

## 4. Migration Strategies

### Bottom-Up (Leaf First)

1. Convert leaf modules first (no dependencies)
2. Add `module-info.java`
3. Fix split packages
3. Move up dependency chain

### Automatic Modules

```java
// Automatic module from JAR (no module-info.java)
module "com.google.guava" { }

// Usage
requires com.google.guava; // automatic module name = JAR name
```

### Unnamed Module

- Classpath JARs → unnamed module
- Reads all modules, exports all packages
- **Cannot** be required by named modules

---

## 4. Migration Patterns

### Split Package Resolution

```java
// Problem: com.util in both module A and B
// Solution 1: Merge into one module
// Solution 2: Use single module, export once
// Solution 3: Rename packages (refactor)
```

### Automatic Modules

```java
// JAR on module path without module-info.java
// Automatic module name = JAR name (sanitized)
module "com.google.guava" { }
```

### Unnamed Module

- Classpath JARs → unnamed module
- Reads all modules, exports all packages
- **Cannot** be required by named modules

---

## 4. Migration Patterns

### Split Package Resolution

```java
// Problem: com.util in both module A and B
// Solution 1: Merge into one module
// Solution 2: Use single module, export once
// Solution 3: Rename packages (refactor)
```

### Automatic Modules

```java
// JAR on module path without module-info.java
// Automatic module name = JAR name (sanitized)
module "com.google.guava" { }
```

### Unnamed Module

- Classpath JARs → unnamed module
- Reads all modules, exports all packages
- **Cannot** be required by named modules

---

## 5. Testing Module Boundaries

### JUnit 5 with JPMS

```java
// Test module
module com.example.test {
    requires junit.jupiter.api;
    requires com.example.app;
    requires org.mockito;
}
```

### Testing Internal APIs

```java
// Test module opens to test
module com.example.app {
    opens com.example.internal to com.example.test;
}
```

---

## 5. Common Pitfalls

| Issue | Solution |
|-------|----------|
| Split package | Merge modules or rename packages |
| Missing `requires` | Add `requires module.name` |
| Reflection fails | Add `opens pkg to test.module` |
| Split package in automatic modules | Rename packages or merge JARs |
| `ClassNotFoundException` at runtime | Missing `requires` or `requires transitive` |

---

## 5. Tools

| Tool | Purpose |
|------|---------|
| `jdeps` | Analyze dependencies (`jdeps --print-module-deps app.jar`) |
| `jdeprscan` | Scan for deprecated APIs |
| `jlink` | Create custom runtime image |
| `jmod` | Create JMOD files |
| `jar --describe-module` | Inspect module info |
| `jmod` | Create JMOD files for `jlink` |