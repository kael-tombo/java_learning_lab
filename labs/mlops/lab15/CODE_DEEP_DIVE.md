# Production ML Architecture - Code Deep Dive

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

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
  ProductionMLArchitectureLab.java   driver: builds and validates the architecture
  ArchitectureSpec.java             three paths, dependencies, owners, SLOs
  ReadPath.java                    serving dependencies with per-term latency budgets
  DegradationLadder.java            ordered fallbacks with quality cost per rung
  DependencyEdge.java               arrow with metric, SLO, owner and failure mode
  RolloutPlan.java                  shadow, canary, ramp with guardrails and rollback
  ConsistencyChoice.java            per-interaction consistency level with a reason
```

DependencyEdge requires a failure mode. A diagram edge with no stated behaviour when it breaks is not an architecture, it is a drawing.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `ArchitectureSpec` | the three paths with nodes, edges, owners and SLOs |
| `ReadPath` | serving dependencies with per-term latency budgets and timeouts |
| `DegradationLadder` | ordered fallbacks with the quality cost of each rung |
| `RolloutPlan` | shadow, canary and ramp stages with guardrails and rollback |

---

## 3.1 An architecture edge that must state its failure mode

Every dependency declares what happens when it breaks, so the diagram is also the failure playbook.

```java
record DependencyEdge(String from, String to, String metric, double slo,
                        String owner, FailureMode failure) {}

enum FailureMode {
    DEGRADE(new String[]{"cached model", "baseline model", "rules engine"}),
    STALE_TOLERATED(new String[]{"serve last known good"}),
    REJECT(new String[]{"fail closed with a clear message"}),
    RETRY_BOUNDED(new String[]{"2 retries, 200 ms budget"})
}

// an edge with no failure mode is an unfinished edge
void requireFailureMode(DependencyEdge e) {
    if (e.failure() == null)
        throw new IllegalStateException("edge " + e.from() + "->" + e.to()
                + " has no failure behaviour; the architecture is incomplete");
}
```


---

## 3.2 Budget enforcement with a bulkhead and a degradation ladder

Per-dependency timeouts and bounded pools mean a slow dependency degrades one rung rather than exhausting everything.

```java
Decision decide(Features f, Model m) {
    for (int rung = 0; rung < ladder.size(); rung++) {
        try {
            double[] features = featurePool.withTimeout(budget.features(), () -> f.fetch(entity));
            double score = inferencePool.withTimeout(budget.inference(), () -> m.score(features));
            return new Decision(entity, score, m.version(), ladder.rungUsed(rung));
        } catch (TimeoutException | ResourceExhaustedException ex) {
            ladder.recordDegradation(rung, ex);       // logged, metered, visible
            continue;                                  // next rung down, bounded by the ladder
        }
    }
    return Decision.reject(entity, "all model rungs unavailable; rules fallback disabled");
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Read path per decision | `O(feature read + inference)` | the only path with a strict latency budget |
| Batch training | `O(epochs x dataset)` | amortised into cost per decision |
| Feedback join | `O(predictions in window)` | bounded by label lag |
| Degradation traversal | `O(rungs)` | must stay shorter than the detection cycle |

## 5. Correctness and Numerics

- Allocate the latency budget per dependency and enforce with timeouts.
- Give every dependency a bounded pool so one slow call cannot exhaust the service.
- Meter and log every degradation rung so degraded mode is visible, not silent.
- Cache the model locally so rollback and startup do not depend on the registry.
- Track cost per 1,000 decisions including amortised training.

## 6. Test Strategy

- An architecture edge without a failure mode fails validation.
- A feature store timeout degrades one rung within the budget and logs it.
- All rungs exhausted produces the documented terminal behaviour, not a hang.
- Latency budget violations are detected per dependency, not only in aggregate.
- Rollback completes within the documented time using the local model cache.
- Cost per 1,000 decisions is computed and reported for a given traffic profile.

## 7. Extension Points

- Add multi-region read paths with a documented failover order.
- Add exploration budgeting so the feedback loop can learn new behaviour.
- Add chaos scenarios for each dependency edge with a measured response.

## 8. Review Checklist

- [ ] Training, serving and feedback drawn as separate paths
- [ ] Every dependency edge has a metric, an SLO, an owner and a failure mode
- [ ] Degradation ladder ordered by quality cost and shorter than detection
- [ ] Per-dependency timeouts and bounded pools
- [ ] Rollout stages with guardrails and a rehearsed rollback
- [ ] Unit economics on the dashboard
