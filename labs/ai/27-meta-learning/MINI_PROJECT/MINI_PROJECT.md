# Meta-Learning — Mini Project

**Goal**: a 2D regression meta-bench: hand-rolled model-based meta-training over
`y = m*x + n` tasks, then adaptation jailbreaks (deliberately harder held-out tasks).

## Task distribution (all fixtures hand-written in the source)

- Training set of 12 tasks; slopes drawn from a fixed list of halves-and-opposites;
  one support point each, one query point each.
- Two held-out twist tasks: same family BUT with query shifted off the line
  (3% +, then 10% +) to probe robustness of the pseudo-gradient.

## Structure

1. `Task` (slope, support, query), `MetaRunner` with two loops per epoch:
   inner forward (support), inner step with `alpha`, outer loss on query, outer
   accumulation of pseudo-gradients (first-order only, documented as such), `beta` step.
2. Controls: `alpha in {0.02, 0.05, 0.1}`, `beta = 0.1`, epochs = 20; theta0 starts 0.
3. Per-epoch output lines: accumulated outer loss vs omega; per-task adapted loss list
   rounded 3dp.
4. Eval: report the outer objective trajectory (max 3dp) and how many of the 12 tasks
   had an adapted loss below 0.02 at epoch 20.

## Twist analysis (mandatory deliverable)

- Compare twist tasks' adapted loss at epochs {1, 5, 20} against the training tasks' best;
  describe the transition from task-family learning to memorizing the 12 fixtures — what
  evidence in the trajectory supports either explanation?
- State one intervention you would try (bigger task set / regularization on theta0 /
  lower beta) and the trajectory signature you would look for. Say explicitly whether you
  ran it, and if so what happened.

## Acceptance

- `javac --release 21`, single file, fully seeded and deterministic; stdout ASCII only.
- Under 250 lines; backprop formulas commented inline at first use.
- The reproducibility header: exact command lines for compiling and running, placed as
  the first comment.
