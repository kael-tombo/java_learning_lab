# How It Works: JIT Compilation

A call to `burn()` starts in the interpreter. Each entry bumps the
invocation counter; each loop iteration bumps the back-edge counter.
Nothing is compiled yet.

Around 200 invocations the method crosses `Tier3InvocationThreshold` and
C1 compiles it with full profiling (tier 3). Execution continues in C1
code that records which branches take and which receiver types arrive.

The profiled C1 code keeps running. Branch frequencies stabilize, the
call targets prove monomorphic, loop bounds look constant. The invocation
counter keeps climbing toward `Tier4InvocationThreshold=5000`.

At ~5000 the compile system queues a C2 task. C2 reads the tier-3
profile and speculates: inline the hot callee (it is 3 bytes, far under
`MaxInlineSize=35`), fold the constant stride, unroll the loop, drop the
range check the profile says never fires.

The C2 version installs and traffic shifts to it. If a guard ever fails
(a second receiver type appears, an index goes out of the assumed range),
the uncommon trap fires: the compiled frame reconstructs interpreter
state, execution resumes in the interpreter, and a recompile without the
failed assumption is queued.

Counters decay across safepoints, so a method that goes cold loses its
compiled status claim honestly instead of staying compiled forever.

Loop-heavy methods often promote through on-stack replacement instead of
plain entry counters: the back-edge thresholds (60000 toward tier 3,
40000 toward tier 4) trip while the method is still running, and the
`%` marker in the log records the mid-loop swap. Size scaling applies
throughout (`Tier3CompileThreshold=2000`, `Tier4CompileThreshold=15000`),
so small kernels like `burn()` promote promptly while large methods wait
for proportionally more evidence before C2 spends its compile budget.

Deoptimization closes the loop rather than ending it: each trap narrows
the next speculation, so repeated cycles converge on assumptions the
workload actually keeps. Steady state is not trap-free by luck but
trap-free by learning — profiles stabilize because uncommon paths stay
uncommon and the compiler stops betting against them.
