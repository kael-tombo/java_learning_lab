# Why It Exists: Bytecode Generation

Bytecode editing exists because some problems live below source.
Proxies need classes that did not exist at compile time (mocking,
AOP, ORM lazy loading). Shading needs renamed references across
whole jars. Agents need probes inside running methods (profilers,
tracers). Waiting for source regeneration per case does not scale —
tools rewrite the binary struct directly.

ASM's visitor design (OW2, 2002) exists because class files are
streams more often than objects: a shading pass touches names, not
whole methods, and allocating an object per instruction for a
100,000-class build is pure overhead. Events (`visitMethod`,
`visitInsn`) with a re-emitting writer stream arbitrarily large
inputs through constant memory; the `ClassNode` tree covers the
minority needing whole-class views. `COMPUTE_MAXS`/`COMPUTE_FRAMES`
exist because hand-derived frames were the top generator-bug source —
automation moved correctness into the library.

The JDK's `java.lang.classfile` (JEP 457/22, JEP 466/23) exists
because the platform itself became a heavy generator: lambda linkage
spins adapter classes, proxies materialize interfaces, serialization
filters synthesize checks. Depending on an external library for core
runtime mechanics was untenable, and ASM's version gates lagged new
class-file versions by construction. A JDK-owned API versions with
the platform: parse, builders with always-on derivation, and
transform lambdas unifying tree and streaming roles.

Withhold-to-delete exists because immutability scales review:
selecting elements into a new builder (never mutating in place) makes
transforms diffable, order-preserving, and pool-sharing — the same
reasons persistent data structures win elsewhere. Labels exist
because byte offsets are write-only: no human should renumber jumps
after inserting an instruction, and no generator should run a layout
pass per edit.

`defineClass`-verifies exists as the closing invariant: however
bytes were produced — `javac`, ASM, builders — one gate checks them.
Generation without that gate would be an integrity hole; with it,
emitters are ordinary (testable, reviewable) code.
