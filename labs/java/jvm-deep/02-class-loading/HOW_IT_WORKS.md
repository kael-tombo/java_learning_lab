# How It Works: Class Loading

## 1. First active use starts the pipeline

Executing `new Widget()`, calling a static method, or running
`Class.forName("Widget")` asks the app loader for the binary name.
`loadClass` checks its cache (`findLoadedClass`): a previous load
returns immediately — loading happens once per (name, loader).

## 2. Delegation walks up before looking down

The app loader asks platform; platform asks bootstrap. Bootstrap
searches `java.base` (and core modules). For `Widget` it misses, so
control returns down: platform misses, app calls its own `findClass`,
reads `Widget.class` bytes, and calls `defineClass`. For
`java.lang.String` the walk stops at bootstrap — your classpath copy
is never consulted.

## 3. Linking verifies, zeroes, and defers

`defineClass` triggers verification (bytecode type-check against
`StackMapTable`, lab 01's frames) and preparation (static storage
allocated as null/0/false — no code runs). Resolution of symbolic
references (`Fieldref`/`Methodref` pool entries) is lazy: each
resolves on first use, which is why version-skew errors surface at
first execution, not at load.

## 4. Initialization runs <clinit> once

On the triggering active use, the JVM takes the initialization lock
for `Widget`, runs its `<clinit>` (static field initializers and
static blocks, superclass first), marks it initialized. Concurrent
threads block on the lock; recursive requests are detected. A
`static final int PORT = 8080` never reaches this step — its value
was already copied into callers' bytecode at their compile time.

## 5. Identity binds name to loader

The resulting `Class` records its defining loader. A second loader
repeating steps 1–4 with identical bytes gets a distinct `Class`
object with its own statics, its own init lock, its own `<clinit>`
run. Assignment between the two fails: the verifier compares
(name, loader) pairs, not names.

## 6. Frameworks escape upward-only visibility

When platform-layer code (say, `DocumentBuilderFactory`) needs an
app-provided implementation, delegation cannot help — it only looks
up. The framework reads `Thread.currentThread().
getContextClassLoader()` (normally the app loader) and loads down
through it. The context loader is inherited per thread, which is why
fresh threads and pools need it set explicitly.
