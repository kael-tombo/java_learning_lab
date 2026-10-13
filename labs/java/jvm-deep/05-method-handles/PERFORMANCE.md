# Performance: Method Handles

## Warm handles match direct calls

After linkage, the JIT inlines through handles and constant call
sites: `invokeExact` on a warmed `(double)double` sqrt handle
compiles comparably to a static call. Primitives travel unboxed end
to end (no `Object[]`, no per-call access check) — the two taxes
reflection pays every invocation. Measure warm (thousands of calls
before timing); cold linkage is a one-time tariff, not a rate.

## Constant sites delete indirection

`ConstantCallSite` folds: the JIT treats the target as a direct call
and inlines through it. Lambda bodies and concatenated strings
therefore run at hand-written speed in steady state — the
`invokedynamic` in the dump costs one bootstrap historically, zero
per call currently. Prefer constant sites for every linkage that is
genuinely fixed; mutability has a real (if small) cost.

## Mutable sites cost volatility, not dispatch

`MutableCallSite`/`VolatileCallSite` targets re-read with volatile
semantics — safe publication for guards and caches, priced as a
volatile load per invocation (negligible next to a call, visible in
nanosecond-scale loops). Keep relinkable sites for genuinely
relinkable logic (megamorphic caches, live replacement); freezing
stable targets into constant sites is the standard promotion.

## Combinators inline as units

`guardWithTest`/`filterArguments` compositions optimize as single
units: test + arms inline together, redundant checks eliminated
across the boundary. The alternative (bytecode if-else calling
separate methods) splits profiling and inlining budgets three ways.
Branching-via-combinator is a code-shape optimization the JIT
rewards — provided the composed type is exact (`invokeExact`
throughout), so no adaptation barrier sits inside.

## Lookup cost is construction-only — batch it

`findStatic`/`findVirtual`/`findSetter` pay access checks, type
parsing, and (for virtuals) receiver validation once. Caching
handles in `static final` fields (initialized in `<clinit>`, itself
once-per-class per lab 02) amortizes lookup to zero per call.
Re-looking-up per invocation recreates reflection's cost profile
with extra steps — the handle equivalent of compiling a regex per
match.

## invoke vs invokeExact in hot paths

`invoke` inserts `asType` adaptation per call site (casts, unboxing)
— correct where static types vary, but a per-call conversion chain
the JIT must then dissolve. `invokeExact` with exactly-matching
static types carries no adaptation at all. Monomorphic hot paths
earn `invokeExact`; generic helpers accept `invoke` (or a prebuilt
`asType` view held in a constant) as the documented trade.
