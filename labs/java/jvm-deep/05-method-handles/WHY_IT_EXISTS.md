# Why It Exists: Method Handles

Dynamic languages forced the issue. By 2010 JRuby, Jython, and the
Nashorn project ran expressive call semantics on a JVM whose linkage
was fixed at compile time — every dynamic call paid reflective or
megamorphic dispatch because the platform offered no late-binding
primitive. JSR 292 (Java 7, John Rose's group) supplied two: method
handles (typed, directly executable, checked-once references) and
`invokedynamic` (call sites whose target a bootstrap chooses at
first execution). One bootstrap per site replaced per-call dispatch
overhead across JRuby, Nashorn, and later Clojure.

Handles check access at creation because bootstraps run with caller
rights: a bootstrap handed an untrusted lookup cannot mint handles
beyond it. Per-call checks would have taxed every invocation for a
decision that never changes — the lookup/invoke split prices the
check once and execution at direct-call speed. `invokeExact`'s
link-time strictness extends the same philosophy to types: prove the
wiring when linking, run unchecked (but correctly) when hot.

Combinators (`bindTo`/`insertArguments`, `filterArguments`,
`guardWithTest`, spreaders/collectors) exist so dynamic runtimes
build calling conventions without emitting bytecode: currying,
argument adaptation, and guarded dispatch express CPU-cheap handle
graphs the JIT inlines as units. JEP 274 (Java 9) filled the gaps
(loops, try-finally, more filters) once real runtimes showed which
shapes they composed daily.

The three call-site kinds exist because linkage lifetimes differ:
lambdas link once and never change (constant — folds to direct),
inline caches and guards relink under load (mutable/volatile with
publication semantics). One instruction, three contracts, chosen per
site instead of per platform.

`findConstructor`'s void rule and `findSetter`'s final rejection are
not quirks but boundary statements: construction initializes rather
than returns (the handle adapts the outcome), and final fields are
handle-immutable from lookup — the language's integrity promises
restated at the lowest API that could break them.
