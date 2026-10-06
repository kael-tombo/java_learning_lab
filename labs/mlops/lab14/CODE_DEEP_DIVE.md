# AutoML Pipelines - Code Deep Dive

**Track:** mlops  |  **Lab:** lab14  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Module Map

```text
src/
  AutoMLLab.java             driver: runs grid, random and Bayesian searches
  SearchSpace.java           bounded, optionally log-transformed parameter space
  Objective.java             single-scalar objective on a fixed evaluation protocol
  GridSearch.java            exhaustive product, with pruning
  RandomSearch.java          seeded sampling with optional pruning
  BayesianTuner.java         surrogate model plus expected-improvement acquisition
  SuccessiveHalving.java     multi-rung budget allocation and promotion
```

Objective is a single method taking the parameter map and returning one number computed by the same evaluation protocol every time. Changing the protocol mid-search invalidates the whole comparison.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `SearchSpace` | bounded, optionally log-scaled parameters with pruning |
| `Objective` | parameter map to a single score on a fixed protocol |
| `BayesianTuner` | surrogate model plus expected-improvement acquisition |
| `SuccessiveHalving` | multi-rung allocation promoting the top fraction |

---

## 3.1 Log-scaled search space with pruning

Transform skewed parameters and remove dominated configurations before spending a single trial.

```java
public Optional<double[]> sample(SearchSpace space, SplittableRandom rnd) {
    double[] point = new double[space.size()];
    for (int i = 0; i < space.size(); i++) {
        Param p = space.get(i);
        if (p.logScale()) {
            double u = rnd.nextDouble();                      // log-scale sampling
            point[i] = Math.exp(Math.log(p.low()) + u * (Math.log(p.high()) - Math.log(p.low())));
        } else {
            point[i] = p.low() + rnd.nextDouble() * (p.high() - p.low());
        }
    }
    return space.prune(point) ? Optional.empty() : Optional.of(point);  // free pruning
}
```


---

## 3.2 Expected improvement over a simple surrogate

The acquisition function is where the search decides where to look next; mean and uncertainty are traded explicitly.

```java
double expectedImprovement(double[] x, double bestSoFar, double xi) {
    double mean = surrogate.mean(x);            // exploitation: predicted value
    double sigma = surrogate.uncertainty(x);    // exploration: predicted std dev
    double z = (mean - bestSoFar - xi) / Math.max(sigma, 1e-12);
    return (mean - bestSoFar - xi) * normalCdf(z) + sigma * normalPdf(z);
    // EI = (mu - f* - xi) Phi(z) + sigma phi(z), the standard closed form
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| One trial | `O(train cost)` | the objective dominates; search overhead is small |
| Random search | `O(trials)` | the same per trial, better coverage |
| Bayesian surrogate fit | `O(T x d^2 to O(T d^3))` | negligible until trials get expensive |
| Successive halving | `O(trials x log r)` | extra bookkeeping, no extra model |

## 5. Correctness and Numerics

- Log-transform skewed parameters; restrict to plausible decades.
- Prune the space before launching so trials are not spent on dominated points.
- Stop on a smoothed metric, and repeat seeds to estimate variance.
- Estimate the final number on data not used for selection.
- Log every trial with configuration, code version and data version.

## 6. Test Strategy

- Grid search visits exactly the Cartesian product size, with pruning accounted for.
- Two identical seeds produce identical trial sequences.
- Pruned points are never evaluated.
- Successive halving promotes exactly the top fraction at each rung.
- The reported final score comes from a holdout not used for selection.
- Trials logged with full configuration are reproducible from the log.

## 7. Extension Points

- Add Hyperband brackets to hedge the resource schedule.
- Add a multi-objective variant with a Pareto front over accuracy and latency.
- Add warm-starting from a previous tuning run's trials.

## 8. Review Checklist

- [ ] Search space log-scaled and plausibly bounded
- [ ] Objective is one method on a fixed evaluation protocol
- [ ] Budget fixed and allocated with early stopping
- [ ] Final estimate on data not used for selection
- [ ] Every trial logged with configuration, code and data version
- [ ] Baseline reported for comparison
