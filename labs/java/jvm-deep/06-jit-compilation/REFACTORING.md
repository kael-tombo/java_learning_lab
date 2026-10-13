# Refactoring: JIT Compilation

## Make hot callees inline-friendly

Before: a 200-byte helper called in the request loop, full of branches
and secondary calls. `PrintInlining` says `too big` and the call boundary
blocks escape analysis.

After: extract the hot 20-byte fast path into its own method; leave the
cold branches in the out-of-line helper. The fast path inlines (under
`MaxInlineSize=35`), constants propagate through it, and the cold path
stays a call nobody measures. One split, two budgets satisfied.

## Stabilize call sites toward monomorphic

Before: `handler.handle(event)` with six implementations rotating through
one site. The inline cache gives up, every dispatch is virtual, and C2
declines to speculate.

After: route by type once upstream (a switch that selects a
per-type-specialized loop), so each inner site sees one receiver. The
profile turns monomorphic, the guard holds, and the call dissolves. The
branch moved outward where prediction is cheap.

## Hoist what the JIT cannot prove invariant

Before: `for (...) { use(config.getTimeout()); }` where the getter is
opaque to the compiler. Range and null checks repeat per iteration.

After: `int t = config.getTimeout(); for (...) { use(t); }`. The local
lets C2 eliminate repeated checks and unroll cleanly. Manual hoisting of
genuinely loop-invariant values complements, not fights, loop transforms.

## Shrink allocation out of the hot path

Before: `new Point(x, y)` per iteration, escaping into a list. Escape
analysis cannot help because the object genuinely escapes.

After: accumulate into reused primitives or a preallocated buffer, and
allocate the wrapper once outside the loop. Where the object truly cannot
escape (scratch formatting), keep the allocation — scalar replacement
already removes it, and manual pooling would only add complexity.

## What not to refactor

Do not hand-inline everything: oversized methods defeat the instruction
cache and the 325-byte hot budget. Do not add `final` hoping to force
inlining — hotness and size decide, not modifiers.
