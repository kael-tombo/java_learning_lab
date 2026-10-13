# Security: JIT Compilation

## Speculative compilation and side channels

C2 emits different machine code per profile: inlined versus virtual
dispatch, eliminated versus retained bounds checks. An attacker who can
influence profiling input (request shapes that train a branch one way)
and then time responses may infer which path compiled. Keep
 attacker-controlled inputs out of security decisions that rely on
uniform timing; use constant-time primitives for secrets regardless of
what the JIT does.

## Deoptimization as a timing oracle

An uncommon trap round-trips through the interpreter and recompiles —
microseconds to low milliseconds per event. Code that deoptimizes on
secret-dependent values (a type check that fails only for one key class)
leaks the secret through latency. Structure secret handling so success
and failure paths share compiled shape, and never branch on secrets into
differently optimized callees.

## Code-cache and log exposure

`PrintCompilation`, `PrintInlining`, and especially `PrintAssembly`
disclose method hotness, inline structure, and generated addresses. Leave
them off in production; compilation logs are diagnostic output with
layout information. Similarly, `TieredStopAtLevel` experiments belong in
staging — capping tiers in production trades away the profiled defenses
(range checks, type guards) posture for no security gain.

## Integer and bounds speculation

Range-check and overflow eliminations are guarded speculations: correct
because the trap exists. They are not a substitute for validation of
untrusted lengths and offsets at trust boundaries. Validate once on
entry with explicit checks; let the JIT remove the redundant inner ones.
A missing entry check is a vulnerability no compiler pass repairs.

## Supply-chain note

JIT behavior differs across vendors and versions (C2 versus Graal via
JVMCI where enabled). Security-sensitive timings must be re-measured per
runtime you ship, not carried over from a blog's numbers.
