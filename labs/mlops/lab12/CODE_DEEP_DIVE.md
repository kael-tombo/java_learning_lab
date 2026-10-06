# Infrastructure as Code for ML - Code Deep Dive

**Track:** mlops  |  **Lab:** lab12  |  **Level:** Intermediate

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
  InfrastructureAsCodeLab.java   driver: renders HCL, runs plan, reports drift
  TerraformConfigGenerator.java emits HCL for buckets, pools, IAM, networking
  PlanDiff.java                 typed plan: creates, updates, destroys with reasons
  DriftDetector.java            desired vs actual, classifying drift per resource
  CostModel.java                tagged cost allocation and idle-quota detection
  Workspace.java                per-team state isolation and credential scoping
```

PlanDiff classifies each line as intended or drift at render time. That is what makes a plan reviewable rather than a wall of text a human skims for the creates.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `TerraformConfigGenerator` | emits HCL for pools, buckets, IAM and networking |
| `PlanDiff` | typed create/update/destroy list with reasons and risk flags |
| `DriftDetector` | compares desired to actual and attributes each divergence |
| `CostModel` | tagged cost allocation plus idle-quota detection |

---

## 3.1 A plan that makes destroys impossible to miss

Destroys are separated, risk-flagged, and stateful destroys fail validation without an explicit recovery acknowledgement.

```java
public void validate(PlanDiff plan) {
    List<String> blockers = new ArrayList<>();
    for (Change c : plan.changes()) {
        if (c.action() != Action.DESTROY) continue;
        if (!c.stateful()) continue;
        // a stateful destroy must state its recovery properties, not just that it happens
        if (c.restoreSource() == null)
            blockers.add("DESTROY of stateful " + c.address() + " has no restore source");
        else if (c.snapshotAgeHours() > policy.maxRpoHours)
            blockers.add("DESTROY " + c.address() + " snapshot is " + c.snapshotAgeHours()
                    + "h old, exceeds RPO " + policy.maxRpoHours() + "h");
    }
    if (!blockers.isEmpty())
        throw new PlanRejected(String.join("; ", blockers));   // review cannot wave this through
}
```


---

## 3.2 Drift classification with an owner

Drift is reported and attributed, not silently corrected, because a manual change may be an intentional emergency fix.

```java
public DriftReport detect(DesiredState desired, ActualState actual) {
    Map<String, Ownership> owners = registry.owners();
    List<DriftItem> items = new ArrayList<>();
    for (var e : desired.byAddress().entrySet()) {
        if (!actual.exists(e.getKey()))
            items.add(new DriftItem(e.getKey(), DriftKind.MISSING, owners.get(e.getKey())));
    }
    for (var e : actual.byAddress().entrySet()) {
        if (!desired.exists(e.getKey()))
            items.add(new DriftItem(e.getKey(), DriftKind.EXTRA,   // manual creation
                    owners.getOrDefault(e.getKey(), Ownership.UNKNOWN)));
        else if (!e.getValue().equals(desired.get(e.getKey()).attributes()))
            items.add(new DriftItem(e.getKey(), DriftKind.MODIFIED, owners.get(e.getKey())));
    }
    return new DriftReport(items, actual.collectedAt());   // reported, not auto-corrected
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Plan render | `O(resources)` | fast; the review artifact is cheap to produce |
| Plan diff | `O(resources)` | dominant cost is the cloud API reads |
| Drift detection | `O(resources)` | same reads as plan, so schedule it with plan |
| Cost allocation | `O(cost entries)` | aggregation by team tag over a billing period |

## 5. Correctness and Numerics

- Classify every plan line as intended or drift at render time.
- Fail plan validation on a stateful destroy without a recovery acknowledgement.
- Report drift; do not auto-correct, since manual fixes can be intentional.
- Require cost and purpose tags at plan time rather than after deployment.
- Quantify idle quota from tagged usage rather than from a bill.

## 6. Test Strategy

- A plan containing a stateful destroy without a restore source is rejected.
- A stale snapshot beyond the policy RPO blocks the plan.
- Drift classification correctly labels missing, extra and modified resources.
- An extra manually created resource is attributed to UNKNOWN rather than silently deleted.
- Generated HCL is deterministic for the same input.
- Cost allocation sums to the total for the period.

## 7. Extension Points

- Add a policy-as-code check set for tagging, encryption and public access.
- Add plan-time cost estimation compared with the previous month's actuals.
- Add a destroy-and-recreate rehearsal in a sandbox environment.

## 8. Review Checklist

- [ ] No console-created resources in production
- [ ] Topology and environment configuration separated
- [ ] Every apply reviewed with a named reviewer
- [ ] Cost and purpose tags mandatory
- [ ] Drift detected on a schedule and reported
- [ ] Stateful destroys blocked without recovery acknowledgement
