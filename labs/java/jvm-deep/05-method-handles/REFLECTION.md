# Reflection: Method Handles

## Recalling the probes

- State the three lookup descriptors and three resulting handle
  types from `LookupTrio`. Which one differs between lookup and
  handle, and what rule forces the difference (constructor void)?
- Reproduce the `Combinators` outputs: `add40` type and value,
  `addDblFirst(21, 0)`, guarded type and both routed values. Which
  combinator needed `insertArguments` instead of `bindTo`, and why?
- Sketch `Retarget`'s four printed lines and `ExactVsLoose`'s four.
  Which line in each probe states the lab's load-bearing claim?

## Checking your model

- `findSetter` on a final field: which exception, thrown when
  (lookup vs invocation), and what design change does it force on a
  config-holder update path?
- `guardWithTest(t, a, b)` where `t: (int)boolean`, `a/b:
  (int,int)int`: what is the composed type, and what does each of
  the three consume per call? What breaks if you feed the test two
  args?
- A generic helper calling `invokeExact` on a `(double)double`
  handle fails after erasure. Name the exception class, explain why
  the compiler stamped the wrong static types, and give the two
  fixes — marking which belongs in hot code.

## Connecting forward and back

- Lab 02's "checks once at creation" (verification at link) is the
  same shape as lookup-time access checks: state the parallel in one
  sentence, naming what each check buys per later call.
- Lab 03's `invokedynamic` sites are hosted in this lab's call-site
  kinds: which kind backs lambdas, and what JIT treatment follows
  from that choice?
- Lab 04 loads generated classes through `defineClass` + `findStatic`:
  why must the lookup `MethodType` match the builder's
  `MethodTypeDesc` exactly for `invokeExact`, and what adapts when
  it does not (`invoke`/`asType`)?

## What would you teach

- Explain the JSR 292 (origin) vs JEP 274 (enhancement) distinction
  in two sentences a teammate will retain. What dated evidence
  (JRuby on Java 7) anchors it?
- State the `guardWithTest` arity rule and the `bindTo`-reference
  rule as two one-line checklist items for handle code review.
