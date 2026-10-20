# Reinforcement Learning — Real-World Project

**Goal**: a Java-led design for a content-ranking service that learns from a bandit
feedback signal — scoped as a design + prototype, not a production rollout.

## Scenario

A stream of incoming items (use any identifier scheme you like) is scored and shown;
the environment answers with a binary engagement event. Model it as a contextual bandit:
each item has a small feature vector, and arms correspond to ranking slots or variants.

## Prototype requirements

1. `TrafficSource` interface returning simulated events from a seeded `java.util.Random`
   so runs are reproducible; two strategy modes: uniform and biased-with-latent-truth.
2. `Learner` implementing epsilon-greedy over estimated per-variant rates with
   exponential-averaging updates (fixed alpha is fine); expose `pulls[]` counters.
3. `ExperimentRunner` sweeping `epsilon in {0.05, 0.1, 0.3}` over 10,000 seeded rounds,
   printing per-arm totals and the cumulative reward trajectory summarized at checkpoints
   every 2,000 rounds.
4. An evaluation overlay computing a simple regret proxy: `bestTrueArm * t - realized`.

## Ethical and operational notes (must appear in your write-up)

- If deployed against live users, exploration spends real attention; state how you would
  bound the fraction of exploratory traffic and log it.
- Non-stationarity: user taste drifts; describe a sliding-window or restarting mechanism
  and what signals would trigger one.
- Keep feedback loops in mind: showing only past winners can hide regression in other
  arms — that is why epsilon stays nonzero on purpose.

## Deliverables

- Runnable classes, `javac --release 21`, one summary table from a full sweep.
- A half-page design memo: assumptions, the exploration budget, what you would measure
  in production, and honest uncertainty about generalizing beyond the simulation.
