# Class Loading — Theoretical Foundation

## Core Concept

Loading a class is three phases — **loading** (find bytes, build `Class`),
**linking** (verify, prepare, resolve), **initialization** (run
`<clinit>`, JLS §12.4) — executed lazily on first *active use*. And class
identity is **name + defining loader**: the same bytes loaded twice are two
different, mutually uncastable classes. Everything surprising about
classloading (use the wrong `getResource`, `ClassCastException` on
identical names, containers isolating apps) reduces to one of these two
facts.

## The Loader Hierarchy (JDK 9+, measured on JDK 23)

```
bootstrap (null — native code, java.base core)   String.class.getClassLoader() == null
    ▲ parent
platform ("platform" — java.sql, java.xml, ...)  getPlatformClassLoader()
    ▲ parent
app ("app" — classpath / module path)            getSystemClassLoader()
```

Measured: `system parent=platform`, `platform parent=null`. The pre-9
**extension classloader is gone** — `java.ext.dirs` ignored, extensions
mechanism removed (JEP 220 modularized the JDK; platform loader covers the
old extension domain). Any doc diagramming bootstrap→extension→application
describes Java 8.

## Delegation: Parent First, Always by Default

`ClassLoader.loadClass(name)` delegates to the parent *before* attempting
`findClass` itself:

```
loadClass(name):
    1. check already-loaded cache
    2. parent.loadClass(name)   (recurses to bootstrap)
    3. only if parent failed: findClass(name)  (your bytes)
```

Consequences:

- Core classes can't be shadowed: your classpath `java.lang.String` never
  loads (bootstrap wins first). This is a *security* property, not just
  tidiness.
- Breaking delegation (override `loadClass` to check self first, as servlet
  containers and OSGi do for webapp isolation) creates *sibling namespaces*
  — same name, different loaders, `ClassCastException` on assignment.
- `getParent()` chains are inspectable at runtime; a `null` parent means
  "delegate to bootstrap."

## loadClass vs Class.forName: Initialization Is the Difference

| Call | Loads? | Links? | Initializes (`<clinit>`)? |
|---|---|---|---|
| `loader.loadClass(name)` | yes | yes (verify+prepare; resolve lazy) | **no** |
| `Class.forName(name)` | yes | yes | **yes** |
| `Class.forName(name, false, loader)` | yes | yes | no (explicit) |

JLS §12.4 initialization triggers (active use): `new`, static method
invoke, static (non-constant) field read/write, reflection (`Class.forName`
default), subclass initialization (parent first). Compile-time constants
(`static final int X = 3`) do **not** trigger initialization — they're
inlined at the *use* site (lab 01's `ConstantValue` attribute is the
mechanism).

`<clinit>` runs under an initialization lock with recursive-request
detection: circular static initializers across classes deadlock or observe
defaults — the classic `static A a = new A()` puzzles. The JVM guarantees
`<clinit>` runs exactly once (thread-safe by specification, not by your
synchronization).

## Linking in Three Sub-Steps

1. **Verification** — bytecode type-checking (StackMapTable-checked since
   50.0, lab 01). Failure = `VerifyError`/`ClassFormatError` at link time,
   before any code runs.
2. **Preparation** — static field storage allocated, set to defaults
   (`null`/`0`/`false`). No Java code executes here.
3. **Resolution** — symbolic references (pool `Fieldref`/`Methodref`) turned
   into direct references, lazily (first use) or eagerly at HotSpot's
   discretion. Failure modes you know by name: `NoSuchMethodError`,
   `NoSuchFieldError`, `IllegalAccessError` — all *linkage* errors from
   compiling against a different library version than runtime.

## Custom Loaders: The Minimal Correct Shape

```java
class DirLoader extends ClassLoader {
    DirLoader() { super(DirLoader.class.getClassLoader()); }  // keep delegation
    @Override protected Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] b = readBytes(name);          // your source: dir, jar, network, generated
        if (b == null) throw new ClassNotFoundException(name);
        return defineClass(name, b, 0, b.length);   // + optional ProtectionDomain
    }
}
```

Rules: override `findClass`, never `loadClass` (unless you mean to break
delegation); each `defineClass` call mints a *new* `Class` (define twice →
`LinkageError: duplicate class definition`); classes define package
membership on first define (sealing checks). `defineClass` also runs
verification — a loader can't smuggle unverifiable bytecode past the
verifier.

## Resources Follow the Same Delegation

`getResource(name)` / `getResourceAsStream` delegate parent-first too —
which is why `Thread.currentThread().getContextClassLoader()` exists:
framework code (JNDI, JDBC drivers, logging) loaded high in the hierarchy
needs to see *application* resources below it. Forgetting the context loader
(manifesting as "resource not found though it's on the classpath") is the
`ClassNotFoundException`-adjacent classic. In modules (JPMS),
`Module.getResourceAsStream` + `open`/`opens` directives further gate
reflective and resource access (`InaccessibleObjectException` is the
enforcement you meet first).

## Key Invariants

1. Identity = (binary name, defining loader). Same bytes ≠ same class.
2. Delegation is parent-first by default; shadowing `java.*` is impossible
   through delegation.
3. Loading/linking never runs application code; only initialization does.
4. `<clinit>` executes exactly once, under JVM-held locking.
5. Compile-time constants never trigger initialization.
