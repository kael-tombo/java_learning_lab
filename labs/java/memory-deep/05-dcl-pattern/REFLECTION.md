# Reflection: DCL Pattern

## Which element surprised you

Of the three (volatile, outer check, recheck), which one's failure mode
did you previously underestimate — the invisible reorder, the
deterministic double-init, or the "pointless but correct" collapse?
What code of yours relies on the element you trusted least?

## The green run that proves nothing

Deleting `volatile` still prints 1 instance in casual runs. After this
lab, how do you argue such a finding — from the missing edge rather than
from observation? Name a review comment you would now write on a
keyword-less DCL that "passes all tests."

## Determinism as a debugging tool

The 50 ms wedged window turns a race into a certainty
(`constructions == 2`). Where else in your testing could a deliberate
sleep-plus-gate replace timing hope with proof? Sketch one race in your
codebase that deserves the wedge treatment.

## Holder-first as a habit

The holder gives laziness with no subtlety under JLS 12.4.2. What
stops you from defaulting to it — parameters, scope, framework shape?
Pick one DCL in your experience and state concretely why the holder did
or did not fit.

## Enum's two immunities

Reflection-proof plus serialization-identical, at the price of
eagerness. Which singleton in your systems actually crosses
serialization — and does it have `readResolve`, or is it silently
forking identity today?

## What you will enforce

Name the DCL review checklist you will now apply (volatile present,
canonical monitor, recheck under lock, Bloch local, holder-considered)
and the one alternative you will demand justification for not using.
