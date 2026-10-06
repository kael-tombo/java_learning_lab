# Model Registry & Versioning - Code Deep Dive

**Track:** mlops  |  **Lab:** lab03  |  **Level:** Intermediate

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
  ModelRegistryLab.java      driver: register, shadow, gate, promote, roll back
  ModelRegistry.java         versions, stages, aliases, atomic promotion with CAS
  Stage.java                 enum of stages with legal transitions
  ModelVersion.java          immutable entry: hash, artifact, lineage, metrics
  PromotionGate.java         declarative checks, all must pass
  ShadowEvaluator.java       champion vs challenger on matured labels
  RetentionSweeper.java      archive unreachable versions by policy
```

Promotion is a single CAS on the stage pointer; everything else (gate, shadow, lineage check) runs before it. Keeping the write narrow means the concurrency story is auditable.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `ModelRegistry` | register, promote(stage, expected, next), rollback, get |
| `ModelVersion` | immutable: name, version, artifactHash, lineage, metrics, approvals |
| `PromotionGate` | declarative checks returning pass/fail with reasons |
| `ShadowEvaluator` | champion versus challenger comparison on matured labels |

---

## 3.1 Atomic promotion with compare-and-set

The narrow write that makes concurrent promotions safe. A failed CAS throws rather than overwriting.

```java
public ModelVersion promote(String stage, ModelVersion expected, ModelVersion next) {
    synchronized (lock) {                       // CAS on the stage pointer
        ModelVersion current = stagePointers.get(stage);
        if (!current.equals(expected))
            throw new ConcurrentPromotionException(
                "stage " + stage + " moved to " + current.version() + " while promoting");
        PromotionResult result = gate.evaluate(next);          // all checks before the write
        if (!result.passed())
            throw new GateFailedException(stage, result.reasons());
        audit.record(stage, expected.version(), next.version(), result);
        stagePointers.put(stage, next);                        // the single write
        return next;
    }
}

public ModelVersion rollback(String stage) {
    return promote(stage, current(stage), previousChampion(stage));   // same safe path
}
```


---

## 3.2 A promotion gate that explains itself

Every check returns a reason. A gate that only says 'failed' teaches people to bypass it.

```java
public PromotionResult evaluate(ModelVersion v) {
    List<String> reasons = new ArrayList<>();
    if (!v.lineage().complete()) reasons.add("lineage incomplete: missing " + v.lineage().missing());
    if (v.lineage().dataVersion() == null) reasons.add("no data version");
    if (v.metrics().valAuc() < toleranceFloor) reasons.add("val AUC " + v.metrics().valAuc() + " below floor");
    if (v.shadow().maturedDelta() < -shadowTolerance)
        reasons.add("shadow delta " + v.shadow().maturedDelta() + " beyond tolerance");
    if (v.approvals().fairnessReview() == null) reasons.add("fairness review not signed off");
    if (v.metrics().p99LatencyMs() > latencyBudgetMs) reasons.add("p99 latency over budget");
    if (v.artifactHash() == null || !artifactStore.verify(v.artifactHash()))
        reasons.add("artifact hash missing or corrupt");
    return new PromotionResult(reasons.isEmpty(), List.copyOf(reasons));
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Register a version | `O(artifact size)` | content hash plus one metadata write |
| Promotion gate evaluation | `O(number of checks)` | microseconds; not a bottleneck |
| Atomic promotion | `O(1)` | one compare, one write, one audit entry |
| Shadow evaluation window | `O(traffic x window)` | the real cost of the safety net |

## 5. Correctness and Numerics

- Content-hash every artifact; a registry entry without a hash is not trustworthy.
- Make stage transitions a service-only operation; no direct database writes.
- Publish a reason for every gate failure; gates that only say 'no' get bypassed.
- Cache the current champion artifact locally so rollback needs no network.
- Log every transition with actor, timestamp, expected and actual versions.

## 6. Test Strategy

- Two concurrent promotions: exactly one succeeds and the other throws.
- Promotion is refused when lineage is incomplete.
- Rollback restores the previous champion in a single operation.
- A version reachable via an alias is never archived or deleted.
- A failed gate returns every reason, not just the first.
- Registering the same artifact hash twice returns the existing version.

## 7. Extension Points

- Add per-region aliases so rollback can be scoped geographically.
- Implement shadow evaluation with a minimum-matured-label threshold.
- Add a retention sweeper that archives only unreachable versions.

## 8. Review Checklist

- [ ] Promotion is a CAS on the stage pointer
- [ ] Gates are declarative and return all failure reasons
- [ ] Lineage completeness is a gate, not documentation
- [ ] Artifacts are content-hashed and locally cached for rollback
- [ ] Every transition is audited with actor and versions
- [ ] Retention respects reachability
