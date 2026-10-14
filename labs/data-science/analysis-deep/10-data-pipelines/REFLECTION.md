# Reflection - Data Pipelines

## Self-check prompts

- Can I state the fixed-point equation and show it in merge-by-key code?
- Do I know which delivery semantic my queue actually provides, and what
  it does not provide?
- Is my next schema change additive-compatible by the subset test, and
  can I prove it?
- Would a replay of yesterday's batch change my serving store? How do I
  know (assertion, not belief)?
- Are my quality thresholds written policy with volumes attached?

## What surprised you

Many learners assume transport guarantees exactness until the duplicate
bound (1 - (1-d)^n) lands. Write two sentences on where your own designs
relied on hope instead of idempotence.

## Replay audit

Pick a pipeline you know. Trace: keys present? Sink merge or append?
Replay path to staging or live? Write the three gaps found and the
smallest fix for each.

## Next step

Pick one: the fixed-point assertion (Exercise 1) with printed PASS, or
the compat matrix (Exercise 4) with rules cited. Mechanical proofs over
confidence - the lab's closing habit.

## Teach-back test

Explain the fixed-point equation m(m(S,b),b) = m(S,b) to a colleague
using only the elevator-button metaphor and the PipeIdem replay row
(rows stay 3). If they can say why appends fail it, the lesson stuck.

## Commitment line

Write one sentence starting "In my next pipeline I will..." naming one
guard (keyed sink, compat gate, quarantine policy). Sign and date it;
vague resolutions do not count.
