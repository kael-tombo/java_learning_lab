# Model Governance & Compliance - Code Deep Dive

**Track:** mlops  |  **Lab:** lab11  |  **Level:** Advanced

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
  ModelGovernanceLab.java    driver: register, evaluate, gate, audit
  ModelCard.java            generated card: use, data, metrics, limitations
  FairnessEvaluator.java    per-group base rate, selection, TPR, FPR, disparity
  AuditLog.java             append-only hash-chained entries with policy version
  GovernancePolicy.java     versioned thresholds for fairness, drift and evidence
  PromotionGate.java        all governance checks, all reasons reported
```

ModelCard is generated from the pipeline: the group metrics come from FairnessEvaluator and the data description from the snapshot metadata. Typed numbers rot; generated ones cannot.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `ModelCard` | generated card with intended use, data, per-group metrics and limitations |
| `FairnessEvaluator` | per-group base rates and error metrics plus disparity ratios |
| `AuditLog` | append-only hash-chained entries carrying the policy version |
| `GovernancePolicy` | versioned thresholds evaluated by the promotion gate |

---

## 3.1 Fairness evaluation that always reports base rates

Base rates come first because every disparity number is uninterpretable without them, and the group matrix is returned in full.

```java
public FairnessReport evaluate(int[] y, int[] yHat, String[] group) {
    Map<String, int[]> counts = new TreeMap<>();      // per group: TP, FP, FN, TN
    for (int i = 0; i < y.length; i++)
        counts.computeIfAbsent(group[i], k -> new int[4])[index(y[i], yHat[i])]++;

    Map<String, GroupStats> stats = new LinkedHashMap<>();
    for (var e : counts.entrySet()) {
        int tp = e.getValue()[0], fp = e.getValue()[1], fn = e.getValue()[2], tn = e.getValue()[3];
        int n = tp + fp + fn + tn;
        stats.put(e.getKey(), new GroupStats(
                (tp + fn) / (double) n,                 // base rate FIRST: everything else depends on it
                (tp + fp) / (double) n,                 // selection rate
                safe(tp, tp + fn),                      // TPR / equal opportunity view
                safe(fp, fp + tn),                      // FPR
                safe(tp + tn, n)));                     // accuracy, reported but never alone
    }
    double minSel = stats.values().stream().mapToDouble(GroupStats::selection).min().orElseThrow();
    double maxSel = stats.values().stream().mapToDouble(GroupStats::selection).max().orElseThrow();
    return new FairnessReport(stats, maxSel == 0 ? 1 : minSel / maxSel, maxSel - minSel);
}
```


---

## 3.2 Hash-chained audit entries with the policy version

Tamper evidence plus the policy in force at the time, so a review months later can reconstruct which thresholds applied.

```java
public AuditEntry append(String actor, String action, String from, String to,
                           GovernancePolicy policy, List<String> evidence) {
    String canonical = String.join("|", actor, action, from, to,
            policy.versionId(),                                   // thresholds in force at the time
            evidenceHash(evidence), Instant.now().toString());
    String hash = sha256Hex(lastHash + canonical);             // chain: tamper-evident
    AuditEntry entry = new AuditEntry(canonical, hash, lastHash);
    entries.add(entry);
    lastHash = hash;
    return entry;
}

public boolean verifyChain() {
    String prev = "GENESIS";
    for (AuditEntry e : entries) {
        if (!e.hash().equals(sha256Hex(prev + e.canonical()))) return false;  // break found
        prev = e.hash();
    }
    return true;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Per-group fairness evaluation | `O(n)` | one pass grouping by attribute |
| Model card generation | `O(g x m)` | group count times metric count |
| Audit entry append | `O(evidence size)` | hash chain is linear in chain length |
| Chain verification | `O(entries)` | re-hash everything; run on export |

## 5. Correctness and Numerics

- Always print the base rate per group before any disparity ratio.
- Use BigDecimal or scaled doubles for ratios compared to the 0.8 heuristic.
- Guard divisions where a group has no positives or no negatives.
- Record the policy version in every audit entry.
- Generate card metrics from the pipeline rather than typing them.

## 6. Test Strategy

- Base rates are present in the report for every group.
- A single-group dataset produces a ratio of 1.0 and does not error.
- A group with zero positives does not produce NaN.
- Modifying any audit field breaks chain verification at that entry.
- The promotion gate fails when a fairness threshold is breached, with a named reason.
- Generated card metrics equal the metrics recomputed independently.

## 7. Extension Points

- Add threshold-sweep reporting showing how disparity moves with the decision threshold.
- Add counterfactual fairness checking by protected attribute.
- Export the audit trail and verification result in a regulator-friendly format.

## 8. Review Checklist

- [ ] Base rates reported per group before disparity metrics
- [ ] Fairness thresholds versioned and enforced by the gate
- [ ] Policy version recorded in every audit entry
- [ ] Audit log hash-chained and verifiable
- [ ] Card metrics generated from the pipeline
- [ ] Limitations written for a non-technical reader
