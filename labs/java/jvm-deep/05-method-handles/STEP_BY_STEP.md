# Step by Step: Method Handles

## Step 1 — Run the lookup trio

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle sqrt = lookup.findStatic(Math.class, "sqrt",
    MethodType.methodType(double.class, double.class));
MethodHandle sub = lookup.findVirtual(String.class, "substring",
    MethodType.methodType(String.class, int.class, int.class));
MethodHandle ctor = lookup.findConstructor(ArrayList.class,
    MethodType.methodType(void.class, int.class));  // void ALWAYS
```

Print all three `.type()`s. Expect `(double)double`,
`(String,int,int)String`, `(int)ArrayList`. State aloud why the
lookup said void but the handle shows a class.

## Step 2 — Touch fields without reflection

Write `FieldHandles` (CODE_DEEP_DIVE snippet 2): getter/setter on
`Point.x`, read/set/reread, then `findGetter` on final `y` (works)
and `findSetter` on `y` (expect `IllegalAccessException` at lookup).

Confirm types `(Point)int` and `(Point,int)void`.

## Step 3 — Compose three combinators

Write `Combinators` (snippet 3): `insertArguments(add, 0, 40)` →
`(int)int`, `add40(2) = 42`; `filterArguments(add, 0, dbl)` →
`addDblFirst(21, 0) = 42`; `guardWithTest(isBig, add, mul)` →
`(int,int)int`, `(200,1) = 201`, `(1,3) = 3`.

For each, write the consumed-args sentence: who takes the prefix,
who takes the full list.

## Step 4 — Relink one site, freeze another

Write `Retarget` (snippet 4): `MutableCallSite(h1)` → `one`, then
`setTarget(h2)` → `two` through the same invoker;
`ConstantCallSite(h1)` → `one`, relink rejected-or-ignored, still
`one`. Name which kind backs lambdas and why (folds to direct call).

## Step 5 — Feel the strictness boundary

Write `ExactVsLoose` (snippet 5): `invokeExact("a","b")` → `ab`;
statically-`Object` receiver rejected (`WrongMethodTypeException`
at link); `invoke("a","c")` adapts → `ac`; `asType` view type
`(Object,Object)Object`. Decide for your own hot path: exact or
adapting, and write the reason in one sentence.
