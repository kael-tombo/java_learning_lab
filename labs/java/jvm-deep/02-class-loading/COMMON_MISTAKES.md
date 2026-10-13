# Common Mistakes: Class Loading

## 1. Drawing the extension loader

Bootstrap → extension → application describes Java 8. Since 9 the
middle rung is platform (`ClassLoader.getPlatformClassLoader()`),
and the extension mechanism is removed (JEP 220). `LoaderTree`
prints the real chain: app's parent is platform, platform's parent
is null. Update every diagram.

## 2. Expecting loadClass to run <clinit>

`loader.loadClass(name)` loads and links only. Initialization waits
for active use. The `InitVsLoad` probe proves it by absence: no
`<clinit>` line appears before the first print. Calling
`loadClass` then reading a static field and concluding "loadClass
initialized it" misattributes — the field read did.

## 3. Reflecting right after loadClass to "check" init state

`Field.get`, `Method.invoke`, even `Class.getField` on the target
can trigger initialization (active use), destroying the observation.
The probe deliberately reads no members between `loadClass` and its
print. Absence-of-side-effect is the instrument; any probe defeats it.

## 4. Casting across duplicate deployments

Two loaders, same `Widget` bytes → two `Class` objects → `w2.cast(o1)`
throws `ClassCastException` despite identical names. Identity is
(name, defining loader). "Deployed the same jar twice" incidents
(double-registered JDBC drivers, duplicated model classes in
WAR + EAR) are this picture.

## 5. Redeploying one jar for a constant change

`static final int PORT = 8080` inlines into clients (`ConstNoInit`:
`PORT` prints with no `<clinit>` line). Changing the library alone
leaves clients on the old value. Rebuild clients; treat constant
changes as API changes.

## 6. Framework code using its own loader for app classes

`javax.xml` (platform layer) cannot see classpath classes by
delegation — parents never see children. `ContextVsOwn` shows the
framework loader failing where the context loader succeeds. Library
code must use `Thread.currentThread().getContextClassLoader()` for
app resources, not `getClass().getClassLoader()`.

## 7. Overriding loadClass instead of findClass

Overriding `loadClass` replaces parent-first delegation, usually by
accident, producing sibling namespaces and `LinkageError`s. Override
`findClass` (fetch bytes, `defineClass`) and inherit delegation —
unless container-style isolation is the explicit goal.

## 8. Calling defineClass twice for one name

Each call mints a new `Class`; the second definition of the same
binary name in one loader is `LinkageError: duplicate class
definition`. Cache with `findLoadedClass` (inherited `loadClass`
already does) instead of redefining.
