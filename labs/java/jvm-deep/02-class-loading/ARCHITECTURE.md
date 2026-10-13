# Architecture: Class Loading

## The loader tree (measured, JDK 9+)

```text
bootstrap  (null; native code; java.base core)
    ▲  parent
platform   (name "platform"; java.sql, java.xml, ...)
    ▲  parent
app        (name "app"; classpath / module path)
```

Verified by `LoaderTree`: `app.getParent() == platform`,
`platform.getParent() == null`, `String.class.getClassLoader() ==
null`. There is no fourth rung — the pre-9 extension loader is gone
(JEP 220); `java.ext.dirs` is ignored.

## Delegation algorithm (default loadClass)

```text
loadClass(name):
  1. findLoadedClass(name)   -> return if cached
  2. parent.loadClass(name)   -> recurse to bootstrap; return if found
  3. findClass(name)          -> consult own bytes; defineClass
```

Parent-first means core classes always resolve at bootstrap: a
classpath `java.lang.String` never loads. Breaking delegation
(overriding `loadClass` to check self first, as servlet containers
do) creates sibling namespaces — same name, different loaders.

## Phase pipeline per class

```text
loading  (find bytes -> defineClass -> Class object)
   |
linking  (verify -> prepare (zero statics) -> resolve (lazy))
   |
initialization (<clinit> runs once, under JVM lock, on active use)
```

JLS §12.4 active uses: `new`, static method invoke, static
non-constant field access, reflective `forName` (default), subclass
init (parent first). Compile-time constants bypass all of it.

## Custom loader shape

```text
DirLoader extends ClassLoader
  parent: app loader (keeps delegation; null == bootstrap-only)
  findClass(name): readBytes -> defineClass(name, b, 0, len)
  loadClass: INHERITED (parent-first preserved)
```

Each `defineClass` mints a fresh `Class`; defining twice is
`LinkageError: duplicate class definition`. `defineClass` also
verifies — loaders cannot smuggle unchecked bytecode.

## Resource and module overlays

`getResource`/`getResourceAsStream` delegate parent-first like
classes. The context loader (`Thread.getContextClassLoader`) is the
documented down-channel: platform-layer framework code uses it to
see app classes delegation hides. In JPMS, `open`/`opens` directives
plus `Module.getResourceAsStream` further gate reflective and
resource access (`InaccessibleObjectException` on violation).
