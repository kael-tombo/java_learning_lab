# THEORY — Class Loading

## Overview

Class loading is the JVM's mechanism for dynamically loading, linking, and initializing classes at runtime. Understanding this process is essential for debugging classloader issues, implementing plugins, and building modular applications.

---

## 1. Class Loader Hierarchy

```
Bootstrap ClassLoader (null)
    ↓
Platform ClassLoader (formerly Extension)
    ↓
Application ClassLoader (Classpath)
    ↓
Custom ClassLoaders (your code)
```

### Three Built-in Loaders

| Loader | Responsibility | Parent |
|--------|---------------|--------|
| **Bootstrap** | Core Java classes (`java.*`, `javax.*`) | null (native) |
| **Platform** | Extension modules (`jdk.*`, modules) | Bootstrap |
| **Application** | Application classpath (`-cp`, `-jar`) | Platform |

---

## 2. Delegation Model

### Parent-First Delegation (Standard)

```java
Class<?> loadClass(String name) {
    // 1. Check if already loaded
    Class<?> c = findLoadedClass(name);
    if (c != null) return c;

    // 2. Delegate to parent
    if (parent != null) {
        return parent.loadClass(name);
    } else {
        return findBootstrapClass(name);
    }
}
```

**Order**: Bootstrap → Platform → Application → Custom

### Breaking Delegation (Advanced)

```java
class ChildFirstLoader extends ClassLoader {
    @Override
    protected Class<?> loadClass(String name, boolean resolve) {
        // Try self FIRST
        Class<?> c = findClass(name);
        if (c != null) return c;
        // Then delegate
        return super.loadClass(name, resolve);
    }
}
```

Use cases: OSGi, application servers, plugin systems.

---

## 3. Class Loading Phases

| Phase | Description | Trigger |
|-------|-------------|---------|
| **Loading** | Read `.class` bytes, create `Class` object | `Class.forName()`, `new` |
| **Linking** | Verify, prepare, resolve | After loading |
| **Initialization** | Run `<clinit>`, static initializers | First active use |

### Linking Sub-phases

| Sub-phase | Action |
|-----------|--------|
| **Verification** | Bytecode validity, type safety |
| **Preparation** | Allocate static fields, zero-initialize |
| **Resolution** | Symbolic refs → direct refs (optional, lazy) |

---

## 4. Initialization Triggers

A class is initialized on **first active use**:

| Trigger | Example |
|---------|---------|
| `new` instance | `new MyClass()` |
| Static field access | `MyClass.STATIC_FIELD` |
| Static method call | `MyClass.staticMethod()` |
| Reflection | `Class.forName("MyClass")` |
| Subclass initialization | `new SubClass()` initializes parent first |

**Passive use** (no init): accessing `static final` compile-time constants.

---

## 5. Custom Class Loaders

### Use Cases

| Scenario | Example |
|----------|---------|
| Plugin systems | Load plugins from JARs |
| Hot reload | Reload classes without restart |
| Isolation | Different versions of same library |
| Encryption | Decrypt encrypted classes on load |

### Template

```java
public class MyClassLoader extends ClassLoader {
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] bytes = loadClassBytes(name); // from JAR, network, encryption
        return defineClass(name, bytes, 0, bytes.length);
    }
}
```

---

## 6. Class Loader Leaks & Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Classloader leak** | `OutOfMemoryError: Metaspace` | Null references, clear caches |
| **Duplicate classes** | `LinkageError` | Parent-first delegation |
| **Version conflicts** | `NoSuchMethodError` | Shade/relocate, classloader isolation |
| **Deadlock** | `ClassLoader.loadClass` sync | Avoid sync in `loadClass` |

---

## 6. Java 9+ Modules

### Module System Impact

- **Module class loaders**: Each module has its own loader
- **Readability**: `module A requires B` → A's loader delegates to B's
- **Encapsulation**: `exports` controls visibility
- **Layered**: `Layer.defineModules()` for multiple configurations

---

## Debugging Commands

```bash
# Verbose class loading
java -verbose:class MyApp

# Show classloader tree
java -XX:+TraceClassLoading MyApp

# Show module resolution
java --show-module-resolution MyApp
```