# Performance: Bytecode Generation

## Lazy views make inspection O(touched), not O(class)

`parse` does not deserialize: iterating method names walks the table
once, reading `majorVersion` touches two bytes. Large-scale scanners
(shading plugins, annotation indexers) can triage thousands of
classes touching headers only, paying full walks solely for matches.
Eager object models (BCEL-style) allocate per entry regardless —
the visitor/lazy-view design exists to avoid exactly that.

## Derivation is cheaper than analysis

ASM's `COMPUTE_FRAMES` re-derives types by walking finished bytecode
against hierarchy lookups (classpath I/O per merge). Builder-tracked
types are free: the state already exists at emit time, so frames
fall out with no second pass and no hierarchy access. Generated-code
throughput (proxy farms, test-mock generation) scales with emission,
not with a post-pass.

## Withhold-transforms preserve pool sharing

`transform` passes kept elements through byte-identically: shared
`Utf8` entries stay shared, ordering stays stable. Output size
tracks the kept subset (snippet 3: strictly smaller after dropping
`main`), and downstream ZIP/JAR compression sees the same repeated
strings. Copying transforms that re-intern every entry bloat
pools — prefer select/withhold over rebuild where possible.

## Generated code runs at javac speed

Builder output verifies and JIT-compiles through identical paths as
`javac` bytes: same `max_stack`-sized frames, same frame-annotated
merges, same inline caches at call sites. `Gen.add(40, 2)` compiles
to the same machine code as a hand-written `add`. Generation cost is
paid once at build/transform time; steady-state performance has no
"generated" penalty.

## Labels eliminate offset-recomputation passes

Hand-assembled jumps need distance fixups after every insertion (or a
dedicated layout pass). Labels defer resolution to `build`, which
resolves all distances in one pass over the final graph. Branch-heavy
generators (state machines, parser tables via `tableswitch`) avoid
quadratic re-layout by construction.

## Version pinning avoids preview-churn rebuilds

The `--release 23 --enable-preview` rig (JEP 466) is the current
stability anchor: snippets pinned to it neither chase latest-JDK
behavior nor rot on old majors. Transformation pipelines should pin
identically — mixed-toolchain builds produce mixed majors (61 vs 67)
that fail deployment gates long after generation succeeded.
