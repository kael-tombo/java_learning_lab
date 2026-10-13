# Why It Exists: JIT Compilation

Java compiles to bytecode once, ahead of time, so one artifact runs on
every platform. The price is that `javac` cannot know which branches are
hot, which call sites are monomorphic, or which loops dominate — that
information only exists at runtime, on real inputs, on the target CPU.

An interpreter alone pays dispatch cost per bytecode forever: fetch,
decode, switch, execute. Loop-heavy integer code measured here runs
roughly an order of magnitude slower interpreted (`-Xint`) than compiled,
which matches the structural gap between per-bytecode dispatch and
unrolled native code with registers allocated.

Ahead-of-time native compilation of Java would recover speed but lose
portability and dynamic loading: classes arrive over the network, agents
redefine them, profiles shift with input. A static compiler must stay
conservative everywhere because it cannot retract a decision.

The JIT resolves the tension by deferring optimization until profiles
exist, then speculating and keeping a way back. C1 buys quick wins with
cheap compiles for startup; C2 spends more compile time only where
counters prove it pays. Deoptimization (uncommon trap plus recompile) is
the safety net that makes speculation sound in a dynamic language.

Without this design, every Java method would run at interpreter speed or
require platform-specific binaries. The tiered JIT is how portable
bytecode closes most of the gap to native code on the paths that matter.
Tier 3 exists specifically to feed C2 trustworthy profiles rather than
guesses, which is why C2 waits until ~5000 invocations instead of
compiling blind at 200.

Escape analysis sharpens the same point: only runtime observation proves
an object never escapes, so only a runtime compiler can dissolve it.
Static ahead-of-time compilers must allocate conservatively wherever
escape is merely possible; C2 allocates only where profiling plus
analysis prove escape actually happens, and deoptimizes when later
behavior contradicts the proof.
