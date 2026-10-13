# Debugging: Class Loading

## ClassNotFoundException vs NoClassDefFoundError

```text
ClassNotFoundException: com.example.Widget      // load-time: bytes not found
NoClassDefFoundError: com/example/Widget        // link-time: found at compile,
                                                // missing now (resolve phase)
```

The first means the loader's `findClass` failed (wrong classpath,
wrong module path, context loader unset). The second means loading
succeeded earlier and resolution failed later — a split-version
deploy. Fix the first with classpath inspection; the second with
dependency alignment.

## ClassCastException on identical names

```text
java.lang.ClassCastException: Widget cannot be cast to Widget
```

Same simple name both sides is the signature of a loader split:
`o1.getClass() != Widget.class` because the loaders differ. Confirm:

```java
System.out.println(o1.getClass().getClassLoader());
System.out.println(Widget.class.getClassLoader());
```

Different loaders → unify deployment (remove the duplicated jar) or
share the type through a common parent loader. This is the
`SplitIdentity` probe in production.

## <clinit> ran (or didn't) unexpectedly

- Static initializer side effects missing after `loadClass`: normal —
  `loadClass` never initializes. Trigger with `Class.forName(name)`
  or an active use.
- `<clinit>` missing when reading `static final int X = 3`: normal —
  compile-time constants inline (`ConstantValue`), no init per
  JLS §12.4. Check with `javap -c` on the *use* site for the literal.
- `<clinit>` deadlock at startup: two classes initializing each
  other under the JVM init lock (recursive-request detection +
  thread lock). Thread-dump the `<clinit>` frames; break the cycle
  with lazy holders or explicit ordering.

## Linkage errors from version skew

```text
NoSuchMethodError / NoSuchFieldError / IllegalAccessError
LinkageError: duplicate class definition
```

The first group resolves lazily: compiled against library A,
running against library B. `javap` both jars and diff descriptors.
The duplicate-definition error means one loader defined the same
binary name twice — find the double-`defineClass` path.

## Resource not found though it's on the classpath

`SomeFramework.class.getResourceAsStream("app.xml")` returns null
while the file sits in `src/main/resources`. Cause: framework class
lives in the platform layer; its loader delegates up, never down to
app. Fix: load through the context loader:

```java
Thread.currentThread().getContextClassLoader()
      .getResourceAsStream("app.xml");
```

## InaccessibleObjectException (modules)

```text
InaccessibleObjectException: Unable to make field accessible:
module java.base does not "opens java.lang" to unnamed module
```

JPMS enforcement at the reflection/resource boundary. Fix with
`--add-opens` or `opens` directives.
