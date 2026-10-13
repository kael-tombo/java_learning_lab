# History: Method Handles

## JSR 292: dynamic languages need linkage (Java 7, 2011)

JRuby, Jython, Nashorn, and later Clojure ran dynamic call semantics
on a statically-linked JVM, paying reflective dispatch per call.
JSR 292 ("Supporting Dynamically Typed Languages on the Java
Platform", led by John Rose) added two primitives: `invokedynamic`
(linkage deferred to a first-run bootstrap) and method handles
(typed, directly executable, access-checked-once references the
bootstrap returns). Java 7 shipped both; dynamic languages adopted
them immediately (JRuby's dispatch, Nashorn's call sites).

## JSR-202/133 context (2004–2006)

Split verification (JSR-202) and the finalized memory/`clinit` model
(JSR-133) preceded handles and shaped them: handle invocation had to
verify under the frame-checked rules and initialize under the
exactly-once lock. `WrongMethodTypeException` as a *link-time*
failure mirrors `VerifyError`'s link-time placement deliberately.

## Lambdas ride the substrate (Java 8, 2014)

Project Lambda compiled `() -> ...` to `invokedynamic` bootstrapped
by `LambdaMetafactory` instead of per-site anonymous classes. The
bootstrap returns a `ConstantCallSite` folding to a cached
`lambda$...` adapter — the constant-site economics of snippet 4
applied at language scale. String concatenation followed in Java 9
via `StringConcatFactory` on the same instruction.

## JEP 274: enhancements, not origin (Java 9, 2017)

JEP 274 ("Enhanced Method Handles") added combinators and loop
support (`loop`, `tryFinally`, `arrayConstructor`, improved
`guardWithTest` shapes, `filterArguments` extensions). It extended
the JSR 292 API — frequently misread as introducing handles. This
lab records the distinction explicitly because the error appeared in
its own earlier materials: 292 is the origin (7), 274 the
enhancement (9).

## Clojure, JRuby, and framework adoption (2011–present)

Clojure's function dispatch, JRuby's runtime, Jackson/serialization
fast-paths, and Mockito's inline mocking all stand on handles and
call sites. `MutableCallSite` guards back megamorphic caches and
live-redefinition hooks; `VolatileCallSite` backs safely-published
mutable targets. The combinator table in THEORY.md §4 is the working
vocabulary those codebases share.

## Present: stable substrate, active use

Handles have not needed a linkage redesign since: `invokeExact`
strictness, `invoke` adaptivity, and the three call-site kinds cover
the space. Current work builds *atop* (pattern-matching linkage,
record deconstruction bootstraps) rather than replacing — the sign
of a primitive that found its level.
