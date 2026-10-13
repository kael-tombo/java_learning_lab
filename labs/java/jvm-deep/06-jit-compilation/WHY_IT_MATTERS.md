# Why It Matters: JIT Compilation

Throughput of server code is dominated by a small hot set: request loops,
serializers, collection internals. The JIT decides whether that set runs
as dispatch-per-bytecode or as register-allocated native code, and the
measured gap here (~29x on the reference run, asserted as >3x for noise
margin) dwarfs most source-level micro-tweaks.

Startup versus peak is the daily trade this lab quantifies. Frameworks
pay interpreter plus C1 cost during bootstrap, then C2 kicks in past
~5000 invocations and steady-state latency drops. Benchmarks that skip
warmup measure the interpreter, not the system they will operate.

Inlining is the highest-leverage single optimization because it unlocks
the rest: a 3-byte callee like `tiny()` disappears into its caller, and
only then can constant propagation, dead-code elimination, and escape
analysis see through the call boundary. Missing inlines (oversized
methods past `FreqInlineSize=325`, megamorphic sites) silently forfeit
all downstream wins.

Deoptimization explains production mysteries: a latency spike after a
config change or a new code path is often an uncommon trap plus
recompile, not GC. Knowing the `TraceDeoptimization` flag turns that
spike from "JVM magic" into a readable event with a cause.

Capacity planning inherits the same numbers. Code-cache sizing
(`ReservedCodeCacheSize=240M`), tier caps for short-lived batch jobs,
and `-Xint` contrasts for diagnosis all come from this lab's flags.
Anyone tuning the JVM without reading `PrintCompilation` output is
guessing about which code is even compiled.

The `ExecutorService.close()` detail (since 19) matters here too: probe
harnesses that spawn observation subprocesses should use
try-with-resources shutdown, because a harness that leaks its own threads
contaminates the very warmup curve it tries to measure. Clean measurement
rigs are part of the performance story, not scaffolding outside it.
