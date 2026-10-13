# Why It Matters: Method Handles

## Frameworks stand on this substrate

Jackson's fast paths, Spring's invocation chains, Mockito's inline
mocks, JRuby/Clojure dispatch, and every lambda in every Java 8+
codebase execute through handles and call sites. Engineers who hold
the lookup/combinator/callsite model read those internals directly;
those who don't treat framework dispatch as uninspectable. The five
probes are the smallest complete tour of the machinery underneath
daily work.

## The strictness boundary prevents production surprises

`WrongMethodTypeException` at link time — during development and
testing — instead of a `ClassCastException` in production is a trade
worth taking deliberately: `invokeExact` in monomorphic hot paths,
`invoke`/`asType` at genuine variability points. Teams that default
everything to `invoke` pay adaptation per call and hide wiring bugs
until load; teams that default to exact get link-time proof and
direct-call speed.

## Combinators replace generated glue

Currying, guard dispatch, argument reshaping — each historically
meant a synthetic class or a reflective adapter. As handle graphs
they are allocation-free, single-unit-optimized, and type-checked at
link. Hot-path branching without bytecode (guards) and call shaping
without wrappers (filters/spreaders) simplify both performance
profiles and stack traces.

## Call-site choice is a performance decision

Constant-vs-mutable is the difference between a folded direct call
and a volatile re-read per invocation, multiplied by every execution
of the site. Lambda-scale traffic makes the wrong default cost real.
Choosing constant for fixed linkage (and promoting stable mutable
sites, per REFACTORING.md §5) is a one-line decision with
JIT-visible consequences.

## The origin correction guards design judgment

Knowing JSR 292 (Java 7) is the origin and JEP 274 (Java 9) the
enhancement prevents "handles are new/unproven" reasoning in 2026:
the substrate has carried dynamic languages and lambdas for over a
decade. Design reviews can recommend handles for dispatch internals
with that history behind them — stable primitive, active atop-work —
rather than re-deriving dynamic dispatch per project.
