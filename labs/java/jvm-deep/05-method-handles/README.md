# Lab 05 — Method Handles & invokedynamic

Typed, directly executable references plus the dynamic call site they
link: method handles (JSR 292, Java 7; JEP 274 added Java 9
enhancements — not the origin), composed with combinators and hosted
in relinkable call sites. Lambdas (Java 8 via `LambdaMetafactory`)
are the flagship user; this lab holds the substrate directly.

## What you prove in this lab

- Lookup trio, exact shapes: `findStatic(Math, "sqrt",
  (double)double)` → `(double)double`; `findVirtual(String,
  "substring", (String,int,int)String)`; `findConstructor(ArrayList,
  (int)V)` at lookup becomes handle type `(int)ArrayList` — the
  constructor descriptor is always `(params)V`, adapted on return
  (a prior THEORY revision showed a return type at lookup — wrong).
- Field handles without reflection: getter `(Point)int`, setter
  `(Point,int)void`, baked offsets, no per-call checks or boxing.
  Final field `y`: getter yes, `findSetter` rejected at lookup with
  `IllegalAccessException`.
- Combinators: `insertArguments` (not `bindTo`) for the primitive
  first arg (`add40: (int)int`, `add40(2) = 42`); `filterArguments`
  preprocessing (`addDblFirst(21, 0) = 42`); `guardWithTest(isBig,
  add, mul)` where the test takes a leading prefix and both branches
  take the FULL arg list (`guarded(200,1) = 201`, `(1,3) = 3`).
- Call sites: `MutableCallSite` relinks (`one` → `two` through the
  same invoker); `ConstantCallSite` folds permanently (lambda sites
  use this; the JIT treats it as a direct call).
- Invocation strictness: `invokeExact` stamps static types at the
  call site — a statically-`Object` receiver is rejected with
  `WrongMethodTypeException` at link time. `invoke` adapts
  (casts/unboxes, `asType` rules); erased generics make the two
  behave differently inside generic helpers.

## Snippets (any JDK 9+, verified on 23, no dependencies)

`LookupTrio`, `FieldHandles`, `Combinators`, `Retarget`,
`ExactVsLoose` in CODE_DEEP_DIVE.md. THEORY.md's table of
transformations (`filterArguments`, `bindTo`, `asSpreader`,
`asCollector`, `guardWithTest`, ...) is exercised, with the arity
and receiver corrections noted above.

## Origin correction

Method handles and `invokedynamic` are JSR 292 (Java 7). JEP 274
(Java 9) enhanced handles (new combinators, loop support) — it did
not introduce them. Any text dating handles to Java 9 confuses the
enhancement with the origin.
