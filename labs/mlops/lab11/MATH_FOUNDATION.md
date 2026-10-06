# Model Governance & Compliance - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `selection_rate = TP + FP over group` | Statistical parity - P(yhat=1 | group) |
| `TPR_g = TP_g / (TP_g + FN_g)` | Equal opportunity - equal true positive rates |
| `FPR_g = FP_g / (FP_g + TN_g)` | False positive disparity - the metric that moves with base rates |
| `demographic_parity_gap = max_g rate - min_g rate` | Disparate impact - the quantity a regulator measures |
| `disparate_impact_ratio = min_g rate / max_g rate` | Four-fifths style ratio - below 0.8 flags review |
| `audit_record = (actor, action, from, to, policy_version, evidence_hash)` | Audit entry - immutable and complete |

## Why the Math Matters

Fairness is constrained optimisation: base rates fix which trade-offs are available, and audit integrity is a hash chain that makes history checkable.


---

## 1. Selection and error rates per group

```text
for each group g and protected attribute a:
  base_rate(g) = positives_g / n_g
  selection(g) = (TP_g + FP_g) / n_g
  TPR(g) = TP_g / positives_g,  FPR(g) = FP_g / negatives_g
```

You cannot interpret any fairness metric without the base rate. Two groups with the same accuracy can have very different error distributions, and that difference is the whole substance of a fairness review.

**Worked example.** Group A: 1000 rows, 100 positive, 50 flagged, 40 correct. base 10%, selection 5%, TPR 40%. Group B: 1000 rows, 300 positive, 60 flagged, 55 correct. base 30%, selection 6%, TPR 18%. Group B looks similar on selection and much worse on TPR.


---

## 2. Disparate impact metrics

```text
ratio = min_g selection(g) / max_g selection(g)
gap = max_g selection(g) - min_g selection(g)
heuristic flag: ratio < 0.8
```

The ratio is scale-free and comparable to the four-fifths heuristic; the gap is absolute and meaningful when the rates are small. Report both, because a small-rate domain can show a large gap and a benign ratio.

**Worked example.** Selection 6% and 5%: ratio 0.833 (passes 0.8), gap 1 point. Selection 0.6% and 0.4%: ratio 0.667 (flags), gap 0.2 points. The second is far less impactful in absolute terms but fails the standard heuristic.


---

## 3. Why parity and equality can conflict

```text
if base_rate_A != base_rate_B and FPR is equal:
  TPR = 1 - FPR (1 + negative/positive ratio scaled)
no threshold equalises both selection rates and TPRs
```

The impossibility is structural, not a modelling failure. Any policy must therefore choose which notion of fairness to prioritise, which is why the choice belongs in a written policy rather than in a code comment.

**Worked example.** Base rates 10% and 30%. Equal FPR of 0.05 gives TPR of roughly 0.5 and 0.71. Forcing equal TPR requires raising the second group's FPR above the first's, which is the trade a reviewer must approve.


---

## 4. Audit chain integrity

```text
entry_i.hash = H(entry_{i-1}.hash + canonical(entry_i))
verifying the chain detects any modification
policy_version stored per entry so thresholds are reconstructible
```

A hash chain makes the log tamper-evident, which is what turns 'we keep an audit log' into evidence a regulator accepts. Storing the policy version per entry is what makes the trail interpretable months later.

**Worked example.** Changing entry 400's actor value changes every subsequent hash, so a reviewer verifying the chain finds the break at entry 400 rather than discovering an inconsistency months later.


---

## Cheat Sheet

- `selection_rate = TP + FP over group` - Statistical parity
- `TPR_g = TP_g / (TP_g + FN_g)` - Equal opportunity
- `FPR_g = FP_g / (FP_g + TN_g)` - False positive disparity
- `demographic_parity_gap = max_g rate - min_g rate` - Disparate impact
- `disparate_impact_ratio = min_g rate / max_g rate` - Four-fifths style ratio
- `audit_record = (actor, action, from, to, policy_version, evidence_hash)` - Audit entry

## Numerical Traps

- Reporting a fairness ratio without the group base rate.
- Comparing a disparity ratio across domains with very different rates without the absolute gap.
- Attempting to satisfy parity and equal opportunity simultaneously when base rates differ.
- Judging a model on accuracy to dismiss a fairness gate failure.

## Self-Check Problems

1. Compute base rate, selection rate, TPR and FPR per group for a given confusion-matrix breakdown.
2. Compute the disparate impact ratio and gap; compare against the 0.8 heuristic and explain the discrepancy.
3. Show with numbers why equal selection rates and equal TPR cannot both hold under differing base rates.
4. Implement an audit hash chain and demonstrate that a single modified field breaks verification.
5. Write a fairness policy choosing parity or equal opportunity, with the reasoning and the cost of the alternative.
