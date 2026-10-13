# Exercises: Class Loading

All probes run on any JDK 9+ (verified on JDK 23). Only `javac` on
PATH is needed for the `Widget` fixture.

## 1. Print your own hierarchy

Write `LoaderTree` (CODE_DEEP_DIVE snippet 1): print the system and
platform loaders' names, `app.getParent() == platform`, and
`platform.getParent() == null`.

Expect `platform` / `app` names and both comparisons true. Write one
sentence stating why no extension loader appears (JEP 220).

## 2. Separate load from initialization

Write `InitVsLoad` (snippet 2): a `Payload` class whose `<clinit>`
prints a line. Call `loader.loadClass("InitVsLoad$Payload")`, print
a marker, then `Class.forName("InitVsLoad$Payload")`.

Expect the marker with no `<clinit>` line before it, then the
`<clinit>` line, then `initialized=true`, then `c1 == c2` true. Now
insert a reflective field read between `loadClass` and the marker
and watch the observation collapse — then remove it.

## 3. Mint two identities from one file

Write `SplitIdentity` (snippet 3): compile `Widget.java` into a temp
dir with `javac -d`, load it through two `DirLoader` instances, and
attempt `w2.cast(o1)`.

Expect `w1 != w2` true and the cast rejected. Print both classes'
loaders and confirm neither is the system loader. Change `super(null)`
to `super(SplitIdentity.class.getClassLoader())` and confirm the
split persists (delegation only affects parent-visible names).

## 4. Show constants skipping initialization

Write `ConstNoInit` (snippet 4): `Config` with a `<clinit>` print, a
`static final int PORT = 8080`, and a computed static. Read `PORT`
first, then the computed field.

Expect `PORT = 8080` with no `<clinit>` line before it, then the
`<clinit>` line, then the computed value. Run `javap -c` on your
class and find the inlined `sipush 8080` at the use site.

## 5. Prove delegation is one-directional

Write `ContextVsOwn` (snippet 5): show the context loader loading
your own class, and the framework loader (`DocumentBuilderFactory`'s
loader) failing to.

Expect context-is-app true, context-sees-app true, framework-sees-
app false. In a fresh `new Thread(...)` with no context set, print
the context loader and explain what framework lookups would lose.

## 6. Break delegation on purpose (then revert)

Temporarily override `loadClass` in `DirLoader` to check `findClass`
first for `Widget` only. Reload twice through one loader instance
and observe `LinkageError: duplicate class definition` on the second
define. Revert to `findClass`-only and confirm single definition.
