# Common Mistakes: Method Handles

## 1. Dating method handles to Java 9

Handles and `invokedynamic` are JSR 292, Java 7. JEP 274 (Java 9)
added combinators and loop support — enhancements, not the origin.
Dating them to 9 misattributes a decade of dynamic-language work
(JRuby, Nashorn) that shipped on 7/8.

## 2. Constructor MethodType with a return type

```java
lookup.findConstructor(ArrayList.class,
    MethodType.methodType(ArrayList.class, int.class));  // WRONG
```

Constructors carry `(params)V` — always void at lookup (snippet 1;
this lab's own THEORY once showed otherwise). The *returned handle*
adapts to `(int)ArrayList`. The lookup descriptor and the handle
type differ by rule, not by accident.

## 3. bindTo with a primitive value

`bindTo` binds the first argument but requires a *reference*
receiver/value. Binding `40` to an `(int,int)int` handle via
`bindTo(40)` fails — use `MethodHandles.insertArguments(add, 0, 40)`
(it boxes the bound primitive), giving `(int)int` and `add40(2) =
42`. Reserve `bindTo` for reference receivers (the substring-style
`(String,...)` first args).

## 4. guardWithTest arity confusion

The test takes a *prefix* of the arguments; target and fallback take
the *full* list. `guardWithTest(isBig(int), add(int,int),
mul(int,int))` composes to `(int,int)int`: `big(200)` routes
`add(200,1)`, `big(1)`-false routes `mul(1,3)`. Giving branches the
tail (or the test the full list) mismatches the composed type — read
the printed `guarded type:` line, it states the contract.

## 5. Setting final fields via handles (at runtime)

```java
lookup.findSetter(Point.class, "y", int.class);  // y is final
```

rejected at *lookup* with `IllegalAccessException`, not at
invocation (snippet 2). Final-field reads work (`findGetter`);
writes never reach a call site. Design configuration holder updates
around this: finals are handle-immutable by construction.

## 6. Relinking a ConstantCallSite

`constant.setTarget(h2)` is forbidden/ignored — the site folds to
its target permanently so the JIT treats it as a direct call (what
lambda sites rely on). Mutability needs `MutableCallSite`
(`setTarget` relinks all callers, volatile semantics). Choosing
constant-by-default and mutable-only-for-guards/caches is the
correct split.

## 7. invokeExact inside generic helpers

Erasure stamps `Object` static types where the handle wants
primitives; `invokeExact` rejects at link time
(`WrongMethodTypeException`), never inside. Prefer `invoke` or an
explicit `asType` view in generic code (snippet 5's
`(Object,Object)Object` view), keeping `invokeExact` for
monomorphic hot paths where strictness is the optimization.
