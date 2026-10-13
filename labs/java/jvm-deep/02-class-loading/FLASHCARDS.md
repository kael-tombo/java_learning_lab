# Flashcards: Class Loading

## Q: What are the three phases of class use, and which runs code?
**A:** Loading (find bytes, build `Class`), linking (verify, prepare,
resolve), initialization (run `<clinit>`). Only initialization runs
application code.

## Q: What is the JDK 9+ loader hierarchy?
**A:** bootstrap (null, native, java.base) ← platform ("platform")
← app ("app"). Measured: app's parent is platform, platform's parent
is null. No extension loader (removed, JEP 220).

## Q: What is the default loadClass algorithm?
**A:** Check loaded cache → delegate to parent (recursing to
bootstrap) → only on parent failure, `findClass` locally.
Parent-first, always by default.

## Q: Why can't a classpath class shadow java.lang.String?
**A:** Delegation reaches bootstrap first, which already provides it.
Shadowing is blocked by ordering — a security property, not tidiness.

## Q: loadClass vs Class.forName — what differs?
**A:** Both load and link; only `forName` (default) initializes.
`forName(name, false, loader)` loads without initializing. Proof is
the absent `<clinit>` line after `loadClass` in `InitVsLoad`.

## Q: What is class identity?
**A:** (binary name, defining loader). Same bytes via two loaders are
two classes; cross-loader casts throw `ClassCastException`.

## Q: Which uses trigger initialization (JLS §12.4)?
**A:** `new`, static method invoke, static non-constant field access,
default `Class.forName`, subclass init (parent first). Compile-time
constants do not.

## Q: Why don't compile-time constants initialize?
**A:** They inline at the use site via `ConstantValue` at
client-compile time. `ConstNoInit` prints `PORT` with no `<clinit>`
line; only the computed field triggers it.

## Q: What does a correct custom loader override?
**A:** `findClass` (fetch bytes, `defineClass`). Never `loadClass`
unless breaking delegation deliberately. Each `defineClass` mints a
new `Class`; redefining is `LinkageError`.

## Q: What are the three linking sub-steps and their failures?
**A:** Verify (`VerifyError`/`ClassFormatError`), prepare (zero
statics, no code), resolve lazily (`NoSuchMethodError`,
`NoSuchFieldError`, `IllegalAccessError` on version skew).

## Q: Why does the context class loader exist?
**A:** Delegation is one-directional (parents never see children), so
platform-layer frameworks use the thread-context loader as the
down-channel to app classes and resources.

## Q: Null parent in `new DirLoader(dir)` with super(null) — what does it mean?
**A:** Bootstrap-only delegation: `java.lang.Object` still resolves
(bootstrap provides it) while the target class stays loader-local.
Total isolation for the `SplitIdentity` demonstration.
