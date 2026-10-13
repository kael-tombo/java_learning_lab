# Lab 02 — Class Loading

Loading, linking, and initialization are three separate events, and
class identity is (name, defining loader). Both facts are measured
here, not stated: the hierarchy prints itself, `<clinit>` silence is
observed positionally, and identical bytes loaded twice refuse to cast.

## What you prove in this lab

- The JDK 9+ hierarchy is bootstrap(null) ← platform ← app, printed
  by `getParent()` chains. There is no extension loader: pre-9
  diagrams with that rung describe Java 8 (JEP 220 removed it).
- `loadClass` loads and links but does not initialize; `Class.forName`
  initializes. Proof is positional: no `<clinit>` line precedes the
  first print after `loadClass`; the flag flips only after `forName`.
- Identity is (binary name, defining loader): two `DirLoader`
  instances loading the same `Widget.class` bytes produce two `Class`
  objects, and `w2.cast(o1)` throws `ClassCastException`.
- Compile-time constants (`static final int PORT = 8080`, via lab
  01's `ConstantValue`) never trigger initialization; computed
  statics do. The `<clinit>` line appears only for the latter.
- Delegation is one-directional: the platform-layer framework class
  cannot see app classes, so frameworks reach down through
  `Thread.currentThread().getContextClassLoader()`.
- Custom loaders override `findClass`, never `loadClass`; each
  `defineClass` call mints a new `Class` and runs verification.

## Linking in three sub-steps

Verification (bytecode checking, `VerifyError` on failure),
preparation (static storage zeroed, no code runs), resolution
(symbolic → direct references, lazily — `NoSuchMethodError` and
friends surface here on first use, not at load).

## Commands and snippets

All five probes run on any JDK 9+ (verified on JDK 23), no
dependencies: `LoaderTree`, `InitVsLoad`, `SplitIdentity`,
`ConstNoInit`, `ContextVsOwn` in CODE_DEEP_DIVE.md. The only
external tool is `javac` for the `Widget` fixture in snippet 3.

## File map

`THEORY.md` states the phases, hierarchy, delegation algorithm, and
loader contract. `CODE_DEEP_DIVE.md` measures each. The remaining
files examine the same five probes from complementary angles:
`HOW_IT_WORKS.md` narrates the load of one class; `ARCHITECTURE.md`
draws the tree; `DEBUGGING.md` maps each failure to its phase;
`SECURITY.md` explains why delegation is a security property.
