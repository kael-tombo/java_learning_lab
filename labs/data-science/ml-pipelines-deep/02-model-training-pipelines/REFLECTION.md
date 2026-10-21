# Model Training Pipelines — Reflection

## What surprised you?
That the most valuable pipeline component produces nothing: the gate
that stops a run. Learners expect value from training; production gets
its value from the runs that never happen because validation refused
bad data.

## Check your understanding
- Can you recompute the 0.3 null rate and explain why the flag trips
  at threshold 0.25 but would clear at 0.35?
- Can you explain why seed 42 repeating [2, 6, 3, 1, 4, 0, 7, 5] is a
  correctness property, not a statistical one?
- Can you list the five mandatory tracking fields and say which
  question each answers?

## Connect to your own work
Recall a time your results changed between reruns. Which of the three
pins (seed, code, data) was missing? What would the incident have
looked like with all three recorded?

## What to do next
- Convert one of your own scripts into the six-stage shape with an
  explicit gate function that returns pass/fail plus reasons.
- Add a tracking record writer to it; refuse to finish a run with any
  field empty.
- Read the Breck et al. rubric's data-validation checks and map each
  to your gate function.

## One-sentence takeaway
A training pipeline is a reproducibility machine: versioned inputs,
gated checks, seeded compute, and registered outputs — so every number
it produces can be explained and rerun.
