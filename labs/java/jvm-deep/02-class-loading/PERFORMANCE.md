# Performance: Class Loading

## Lazy loading bounds startup work

Classes load on first active use, not at launch. A service with
50,000 classpath classes but a 3,000-class hot path links roughly
the hot path at startup; the rest wait for first touch. Eager
`Class.forName` sweeps and static-heavy graphs defeat this — audit
startup with `-Xlog:class+load` and defer what the first request
does not need.

## The loaded-class cache makes repeat loads free

`findLoadedClass` short-circuits every cached `loadClass` to a map
hit. Frameworks that defensively call `loadClass` per invocation
pay one hash lookup, not I/O. The cost concentrates in first loads:
`findClass` byte I/O plus verification plus preparation.

## Verification is the dominant per-class link cost

Split verification (lab 01: single checked pass over `StackMapTable`
frames) keeps this linear in code size, but verification still
touches every method body. Code-generation-heavy startup (proxies,
script engines) should reuse generated `Class` objects rather than
redefining equivalents — each `defineClass` re-verifies from scratch.

## Resolution laziness defers — and scatters — cost

Symbolic references resolve on first use, so a class can link cheaply
and pay resolution across its lifetime. First-request latency often
includes a resolution burst (`NoSuchMethodError` risk included).
Warmup routines that touch hot paths before serving absorb this
deterministically instead of charging it to real traffic.

## Duplicate loading multiplies metaspace

N isolating loaders × M shared names = N·M `Class` objects with
separate statics, constant pools, and JIT profiles (`SplitIdentity`
times containers). Each copy verifies, links, initializes, and
compiles independently — the JIT cannot share code across loader
boundaries. Deduplicate shared libraries into a common parent loader
wherever isolation is not required.

## Initialization locks serialize startup

`<clinit>` runs under a per-class lock with superclass-first
ordering. Deep static-initializer graphs (constants computed via
`Integer.parseInt`, registries filling in static blocks) serialize
threads at class-init barriers. Prefer compile-time constants
(`ConstantValue`, zero init cost) and lazy holders over eager static
graphs; keep `<clinit>` bodies trivial and acyclic.

## Context-loader lookups are map walks, not I/O

`getResource` delegation and context-loader fetches resolve through
cached loader tables. The performance failure is not speed but
misses: a wrong context loader turns a cache hit into a null that
triggers exception paths, retries, or fallback scans. Set contexts
once per thread-pool worker, not per lookup.
