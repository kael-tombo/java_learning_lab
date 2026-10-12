# Exercises: Volatile Semantics

## 1. Stale-flag demo (15 min)
Non-volatile `stop` flag + spinning reader: show the reader missing the write (add a print cap, or reason from JLS 17.4 if the JIT cooperates). Add `volatile`, show prompt visibility. One sentence: which edge fixed it.

## 2. volatile++ loses (20 min)
8 threads x 250k `volatileCounter++`; compare final value vs 2,000,000 across 5 runs (it falls short). Replace with `AtomicLong`/`LongAdder`, show exact. APIs: `AtomicLong.incrementAndGet`, `LongAdder.increment/sum`.

## 3. Safe publication piggyback (20 min)
Publish `{data, meta}` through one trailing volatile `ready` write; readers check `ready` first. Show readers always see both payload fields. Then move the flag write first and show the break; draw the hb chain.

## 4. DCL fixed three ways (20 min)
Implement lazy singleton as (a) broken DCL (plain field), (b) volatile DCL, (c) holder idiom, (d) enum singleton (Bloch Item 3). State which are correct and which you would ship.

## 5. Array trap + tearing (15 min)
`volatile int[]` with concurrent element writes vs `AtomicIntegerArray.set/get`: show which gives per-element visibility. Declare why `volatile long` (not plain `long`) is the portable atomic-access answer per JLS 17.7.

## Submission checklist
- [ ] Each task ran on your JVM with output pasted. [ ] Predictions written before runs. [ ] One deliberate break-and-fix per lab recorded.

## 6. Hoisting vs fence, measured (20 min)
Task: run the StaleSpin harness (CODE_DEEP_DIVE.md snippet 1) on your JVM; record plainSpins (expect run-to-bound) vs volSpins (expect early exit).
Check: explain in two sentences why the same loop shape diverges — hoisted plain read (compiler-legal) vs fenced volatile read — citing JLS 17.4, not hardware.
APIs: plain vs `volatile` boolean flags, `Thread.onSpinWait`; success = both assertions true plus the edge named.

## 7. Transitivity across three threads (20 min)
Task: implement the A -> B -> C chain (snippet 5): A writes plain x then volatile v; B spins on v then writes volatile w; C spins on w then reads x.
Check: C must observe A's value on every run; then break one link (make v plain) and characterize the failure — which hop vanished and why.
APIs: `volatile` flags, `Thread.onSpinWait`, `CountDownLatch`; success = intact-chain proof plus the broken-link diagnosis in edge symbols.

## 8. VarHandle mode ladder (20 min)
Task: rewrite the safe-publication flag three ways — `volatile`, `VarHandle` acquire/release pair, `VarHandle` opaque pair — and state which orderings each guarantees.
Check: identify which variant still publishes correctly (volatile, acquire/release) and which only guarantees progress without ordering (opaque); say when you would descend from volatile.
APIs: `VarHandle.getVolatile/setVolatile/getAcquire/setRelease/getOpaque/setOpaque`; success = the three guarantees stated without conflating visibility with ordering.

## Submission additions
- [ ] StaleSpin numbers (plainSpins vs volSpins) pasted with the BOUND stated.
- [ ] Piggyback chain drawn in -po-/-hb- symbols for exercise 3 and 7.
- [ ] DCL verdict table (broken/volatile/holder/enum) with the shipped choice justified.
- [ ] Array-trap comparison output (volatile-ref vs AtomicIntegerArray) quoted.
- [ ] One deliberately broken link per lab with the missing hop named.
