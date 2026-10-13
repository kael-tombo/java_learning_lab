# Internals: Class Loading

## Loader object facts

- Bootstrap has no `ClassLoader` object: `String.class.
  getClassLoader()` returns null. Null parent in `getParent()`
  chains means "delegate to bootstrap", not "no delegation".
- `ClassLoader.getPlatformClassLoader()` ("platform") and
  `getSystemClassLoader()` ("app") are both `BuiltinClassLoader`
  instances in HotSpot (names "platform"/"app" are the API).
- Every `Class` answers `getClassLoader()` with its *defining*
  loader (the one that called `defineClass`), not the initiating
  loader that was first asked.

## loadClass vs forName matrix

```text
loader.loadClass(name)              loads + links,   NO init
Class.forName(name)                 loads + links + initializes
Class.forName(name, false, loader)  loads + links,   NO init
Class.forName(name, true, loader)   loads + links + initializes
```

Linking covers verify + prepare; resolution inside linking is lazy
either way. Initialization is the only column that varies.

## <clinit> locking rules (JLS §12.4)

One JVM-held initialization lock per class. Exactly-once execution.
Superclass initializes before subclass. Recursive initialization
requests for the same class by the same thread return immediately
(observing defaults); across threads they block — circular static
dependencies between classes deadlock. Exceptions from `<clinit>`
mark the class erroneous: later uses throw
`NoClassDefFoundError`, not a retry.

## defineClass contract

- One call mints one `Class`; same binary name twice in one loader
  → `LinkageError: duplicate class definition`.
- First definition of a package establishes package membership and
  sealing checks for that loader.
- Verification runs inside `defineClass` — malformed bytes fail
  here with `ClassFormatError`/`VerifyError`, before the `Class`
  is returned.
- Optional `ProtectionDomain`/`CodeSource` parameters feed the
  security manager / module checks.

## Resolution failure taxonomy

`NoSuchMethodError`, `NoSuchFieldError`, `NoSuchMethodException`
(reflective variant), `IllegalAccessError`, `IncompatibleClassChangeError`
— all linkage errors from compiling against different library
versions than runtime. They surface at first *use* of the reference,
not at class load, because resolution is lazy.

## Resource lookup paths

`loader.getResource(name)` delegates parent-first (same walk as
classes). `Class.getResource` resolves relative names against the
class's package; leading `/` makes them absolute. Module-aware:
`Module.getResourceAsStream` respects `open`/`opens`; unnamed
modules (classpath) read everything.
