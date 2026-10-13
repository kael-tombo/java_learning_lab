# Mental Models: JIT Compilation

## 1. Counters as a thermostat

Invocation and back-edge counters are the thermostat; the compiler is the
furnace. Below 200 the room stays interpreted. At 200 C1 kicks in with
profiling on. At 5000 C2 takes over. Counters decay at safepoints, so the
thermostat responds to current weather, not last winter.

## 2. Tier 3 as a scout

Tier 3 (C1 with full profiling) is the scout that maps terrain for the
main force (C2). It runs the route, notes branch frequencies and receiver
types, and reports back. C2 never attacks blind — it only compiles what
the scout measured, which is why tier 4 waits for 5000 samples.

## 3. Speculation as a bet with insurance

Every C2 optimization is a bet ("this call site stays monomorphic") with
an insurance policy (the uncommon trap). The bet pays in eliminated
dispatch, checks, and allocations. The premium is one guard instruction.
When the bet loses, insurance pays out: reconstruct the interpreter frame
and continue correctly, then place a smaller bet.

## 4. Inlining as removing walls

A method call is a wall between optimizer and code. Inlining knocks the
wall down so constant propagation and escape analysis can see the whole
room at once. Walls under 35 bytes fall freely; walls up to 325 bytes
fall only where traffic (hotness) justifies the demolition.

## 5. Warmup as breaking in an engine

Cold code is a cold engine: clearances are wrong, oil is thick,
performance is poor. Each invocation is a revolution that warms the metal
and teaches the ECU (profiler) the load map. Measuring before warmup is
timing a cold engine and concluding the car is slow.

## 6. Deoptimization as a fire drill

Compiled code rehearses the common path and posts a fire exit (trap) on
every assumption. When smoke appears (a violated assumption), everyone
exits to the interpreter assembly point in order, nobody is hurt
(correctness holds), and the building is re-entered through a safer route
(recompiled code with weaker assumptions).
