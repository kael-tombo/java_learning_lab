# History - Experimentation

Only widely documented facts; uncertain details are omitted.

## Roots in field trials

- Fisher's Rothamsted work (1920s) and "The Design of Experiments"
  (1935) made randomized comparison with significance reasoning the
  scientific standard - the ancestor of every A/B test.
- Clinical trials (Hill's 1948 streptomycin trial onward) added ethics,
  blinding, and pre-registration - all imported into online testing.

## Industrial quality

- Shewhart's control charts (1920s) and Deming's quality movement
  taught guardrail thinking: watch the process, not just the target.
- Box's response-surface methods (1950s) framed experiments as
  sequential learning - the philosophical parent of iterative testing.

## Online controlled experiments

- Web-scale A/B testing grew with e-commerce and search in the late
  1990s-2000s; Kohavi and colleagues systematized pitfalls (peeking,
  SRM, novelty, carryover) across industry publications.
- Kohavi, Tang, and Xu's "Trustworthy Online Controlled Experiments"
  (2020) is the field manual (see REFERENCES.md).

## Lesson

A century of practice converges on this lab's checklist: randomize,
pre-register, guard the split, hold the horizon, report intervals.

## Reading the lineage

Fisher (randomize and test), Shewhart/Deming (watch the process),
Box (learn sequentially), Kohavi (name the online pitfalls). Each era
added one guardrail the previous era lacked - the modern checklist is
their union, not anyone's invention.

## What the web changed

Scale turned weeks into hours and multiplied metrics a hundredfold -
which multiplied peeking and multiplicity failure modes. The old books
supply the logic; the online literature supplies the failure catalog.
