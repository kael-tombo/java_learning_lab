# Performance: Bytecode Introduction

## The stack model costs nothing hot

Operand-stack traffic is a specification fiction the JIT erases:
`iload/iadd/istore` sequences compile to register operations, and
`max_stack` bounds let the compiler pre-size without scanning. The
1–3 byte instruction encoding pays off cold — denser code, fewer
instruction-cache misses during interpretation and class loading —
while hot code looks like register-machine output anyway.

## Dispatch cost ranks by lookup

`invokestatic`/`invokespecial` bind at compile time (direct calls
after JIT). `invokevirtual` needs one vtable indirection, usually
devirtualized after type profiling. `invokeinterface` probes the
itable — historically the slowest OO dispatch, still costlier under
megamorphic pressure (hence the count operand and inline-cache
attention). `invokedynamic` costs one bootstrap per site, then direct
target calls; steady-state lambda invocation matches static-call
speed.

## Lambdas won by linking once

Pre-8 inner classes loaded a class per site at class-load time;
`invokedynamic` + `LambdaMetafactory` defers to first execution and
shares the adapter (`lambda$...` cached). Applications with
thousands of lambda sites start faster and hold fewer classes. The
remaining per-evaluation cost is capture allocation only —
non-capturing lambdas typically reuse a singleton instance.

## Verification scales with merges, not methods

Split verification checks frames at joins in one pass, so linear
accessors verify near-free while branch-heavy initializers pay per
merge. Keeping hot-path methods straight (early returns over nested
conditionals where readable) trims both class bytes and link time —
the same refactor as lab 01's frame-collapse item, now priced.

## Resolution laziness shapes latency profiles

First execution of each call site pays symbolic resolution; steady
state pays nothing. Microbenchmarks must warm up past first-use
resolution (and lambda bootstrapping) before measuring, or the first
iteration's linkage cost masquerades as call overhead. JMH's warmup
iterations exist partly for this.

## Descriptor and pool density aid loading

Erased descriptors and deduplicated `Utf8` entries keep the constant
pool small; resolution faults fewer pages and string-compares fewer
bytes at link. Megamorphic call sites and huge single methods fight
this (large pools, many frames) — splitting them is a load-time as
well as readability win.
