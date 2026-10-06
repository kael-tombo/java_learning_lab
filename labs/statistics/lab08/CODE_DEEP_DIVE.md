# Experimental Design - Code Deep Dive

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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
  ExperimentalDesign.java   driver: designs, powers and simulates studies
  Design.java              factors, levels, replication, blocking, estimand
  SampleSize.java          n for means and proportions from alpha, power, MDE
  FactorialAnalyzer.java   main effects and interaction contrasts
  BlockingAnalyzer.java    blocked variance reduction and analysis
  Randomiser.java          seeded randomisation with an assignment audit
```

Design carries the estimand as a field. A design object without a written estimand cannot be constructed, which is the cheapest way to prevent the most expensive mistake.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Design` | factors, levels, replication, blocking and the estimand string |
| `SampleSize` | n per arm for means and proportions with the inputs recorded |
| `FactorialAnalyzer` | main effects and interaction contrasts from cell means |
| `Randomiser` | seeded assignment with an audit of realised arm sizes |

---

## 3.1 A design that cannot exist without an estimand

The estimand is a required constructor field, so the ambiguity is caught at design time rather than in the write-up.

```java
public record Design(List<String> factors, int[] levels, int replication,
                    List<String> blockVariables, String estimand) {
    public Design {
        if (estimand == null || estimand.isBlank())
            throw new IllegalArgumentException(
                    "an estimand must be written before the design is fixed; "
                    + "'the effect of X' is not an estimand");
        if (replication < 1)
            throw new IllegalArgumentException("at least one replicate per cell is required "
                    + "to separate the interaction from residual variation");
    }
}
```


---

## 3.2 Seeded randomisation with an assignment audit

Randomisation is seeded and reproducible, and the realised arm sizes are checked so a broken assignment is caught immediately.

```java
public Assignment randomise(Design d, int nPerCell, long seed) {
    SplittableRandom rnd = new SplittableRandom(seed);       // reproducible
    List<Integer> units = IntStream.range(0, totalUnits(d, nPerCell)).boxed().toList();
    List<Integer> shuffled = new ArrayList<>(units);
    Collections.shuffle(shuffled, new Random(seed));        // assignment independent of input order
    int[] armSizes = assignByShuffledUnits(d, shuffled, nPerCell);
    // audit: realised sizes must match the design, or randomisation was not honoured
    for (int i = 0; i < armSizes.length; i++)
        if (armSizes[i] != expectedArmSize(d, nPerCell))
            throw new RandomisationFailure("arm " + i + " received " + armSizes[i]
                    + " units, expected " + expectedArmSize(d, nPerCell));
    return new Assignment(shuffled, armSizes, seed);        // seed recorded with the data
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Sample size calculation | `O(1)` | closed-form arithmetic with quantile lookups |
| Power for a given n | `O(1)` | non-central distribution evaluation |
| Factorial analysis | `O(N)` | cell means then contrasts |
| Randomisation audit | `O(N)` | one pass counting realised arm sizes |

## 5. Correctness and Numerics

- Inflate pilot variance before computing sample size.
- Record the randomisation seed with the data.
- Compute power with the specified alternative, not the null.
- Report the estimand alongside the design and the analysis.
- Use blocking correlations in the power formula rather than assuming independence.

## 6. Test Strategy

- A design without an estimand is rejected at construction.
- A design without replication is rejected.
- Seeded randomisation is reproducible and produces the expected arm sizes.
- Factorial main effects and interaction match hand calculations on a 2x2 design.
- Blocking reduces the estimated variance relative to the unblocked analysis.
- Computed sample size yields approximately the target power in simulation.

## 7. Extension Points

- Add Latin square and Graeco-Latin designs for positional blocking.
- Add cluster randomisation with an intra-cluster correlation.
- Add response surface methodology for continuous factor levels.

## 8. Review Checklist

- [ ] Estimand written before the design is fixed
- [ ] Sample size from alpha, power and an inflated variance estimate
- [ ] Blocking variables chosen in advance
- [ ] Randomisation seeded, recorded and audited
- [ ] Interactions tested before main effects interpreted
- [ ] Analysis pre-specified with planned contrasts
