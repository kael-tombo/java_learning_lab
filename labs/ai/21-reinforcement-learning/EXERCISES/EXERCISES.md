# Reinforcement Learning — Exercises

All tasks run on plain JDK 21+; every snippet from CODE_DEEP_DIVE is your starting point.

## 1. Reproduce the bandit table

Recreate `EpsGreedyBandit` and print all 20 rows without truncation. Then verify each row
by hand: with seed 42, the first three pulls of arm 0 are exploitative (Q ties break to the
first arm), so `q[0]` must follow `0.1, 0.15, 0.175`. Confirm your output matches
`pulls = [3, 16, 1]` and `total reward = 9.4`.

## 2. Change the discount, predict first

Set `gamma = 0.5` in the grid world. Before compiling, write down your prediction for
`V(s0)` — it should be the discounted one-step entry reward. Run it, then explain in one
sentence why sweeps 2 and 3 give identical vectors (reuse of values already at their
fixed point).

## 3. Synchronous vs in-place sweeps

Modify the update so that `v` is overwritten during the sweep (Gauss-Seidel order
`s0, s1, s2`). Report how many sweeps until `maxDelta < 1e-12` for each variant, with the
reward-on-entry convention unchanged. Values at convergence must still be
`[0.9, 1.0, 1.0, 0.0]` either way.

## 4. Off-policy check

Alter the bandit so the target for the Q update incorporates the actually chosen action
rather than `max`; with noiseless rewards, argue on paper which estimate changes and by how
much, then test your claim by running the modified class.

## 5. Optimism experiment

Initialize all `q` entries to `+1` and rerun the bandit for 50 steps with `epsilon = 0.1`
and the exact sample-mean update instead of a fixed alpha. Report the pull counts; the
optimistic start should pull every arm at least once early. State your observed counts in
your notes.

## Acceptance criterion for the set

Every modified program must recompile with `javac --release 21` and every claimed number
must appear in your own captured log, not copied from this document.
