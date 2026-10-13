# Visual Guide: JIT Compilation

## The tier ladder

Imagine a ladder with five rungs labeled 0 to 4. Every method starts on
rung 0 (interpreter). Small counter weights hang off each method; at 200
invocations the weight trips the latch to rung 3 (profiling C1). At 5000
it trips the latch to rung 4 (C2). Loop-heavy methods climb via the
back-edge side ropes instead (60000 toward tier 3, 40000 toward tier 4).

## What each rung looks like

Rung 0: a chef reading a recipe card for every single step, slowly.
Rung 1-2: the chef has memorized the dish but still checks notes.
Rung 3: the chef cooks fluently while a sous-chef tallies which
ingredients get used most (profiling).
Rung 4: the kitchen has been rearranged around the actual orders —
ingredients pre-chopped (constants folded), stations merged (inlined),
unused tools removed (dead code gone).

## The guard-and-trap sketch

Draw the compiled fast path as a straight highway. At each speculation
draw a side ramp labeled "uncommon trap" leading down to a local road
(the interpreter). A barrier gate (guard instruction) sits at each ramp
entrance. Normal traffic never exits; violating traffic is diverted,
re-routed, and the highway is later rebuilt with that exit made
permanent (recompile without the assumption).

## Reading PrintCompilation

Each log line is a plaque on the ladder: timestamp, compile id, tier
number, method name. A `%` badge means on-stack replacement — the method
was swapped mid-loop, like changing tires on a moving car at the
back-edge trigger. Watching `burn` gain a tier-3 plaque then a tier-4
plaque is watching one method climb two rungs.

## The inline diagram

Draw caller `main` as a box and callee `tiny` as a small box beside it.
Inlining erases the wall between them: the small box's contents are
copied inside the big box, the call arrow disappears, and the optimizer
draws new arrows (propagated constants) that were impossible across the
wall. Methods over 325 bytes stay walled except in extraordinary heat.
