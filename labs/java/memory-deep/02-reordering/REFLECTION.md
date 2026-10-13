# Reflection: Reordering

## Prompt 1: your machine's signature

Record your three snippet-1 counts (bad/20000) here. How wide is the
spread, and what does the width tell you about scheduling and power
state rather than about your code? What would you need to believe to
treat the *lowest* of the three as "the" number — and why is that
belief wrong?

## Prompt 2: a green run you distrust now

Recall production code that "works" without edges (a flag protocol, an
unsynchronized handoff, a startup publish). Which TSO table row has
been protecting it, and on which platform (ARM server? low-core
container?) does that row stop applying? What is the cheapest edge that
converts its accident into a verdict?

## Prompt 3: mechanism vs verdict

State the elimination argument for the store buffer in your own words
(same bytecode, 1 ns drain, ~79% to zero). Then distinguish the two
sentences: "the buffer caused this anomaly" (mechanism, x86) from
"the program is racy" (verdict, everywhere). Which sentence licenses a
fitness-for-shipping claim, and which merely explains the symptom?

## Prompt 4: the fix you would ship

Volatile (ordering) vs monitor (exclusion) both read 0/20000. For a
two-flag protocol in *your* codebase, which do you choose — and what
fact about contention, readability, or platform cost decides it? Write
the decision rule you will reuse (e.g., "flags: volatile; shared
updates: lock/atomic; chains: release/acquire").

## Prompt 5: chains that hold vs chains that do not

Snippet 4's release/acquire chain holds over 50000 while snippet 5's
cousin (lab 03) races at 61-90% with the same modes. Draw both shapes
(message-passing arrow vs Dekker cross) and mark where the missing
constraint is. What new code will you now check for "pairwise reasoning
about a total-order problem"?

## Prompt 6: teaching the pistol

Explain to a teammate why the volatile-flag rendezvous is not
"test scaffolding" but the instrument: pistol vs marathon, window width
vs jitter, rates vs verdicts. If they propose replacing it with a
barrier "for cleanliness," what two-sentence reply preserves both the
cleanliness instinct and the measurement?
