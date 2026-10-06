# REAL_WORLD_PROJECT — Revenue Driver Model with Governed Claims

**Track:** statistics  |  **Lab:** lab05  |  **Level:** Intermediate

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

## 1. Scenario

A commerce team fits weekly revenue to traffic, price, promotion and macro indicators, then presents coefficients as 'what drives revenue' in a planning meeting. The model has 0.88 R², two coefficients that flip sign between runs, and no one can say what it predicts on new data.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Data | 104 weekly observations, 6 predictors, 2 years |
| Current state | R² 0.88 reported as accuracy; sign flips between refits |
| Problem | multicollinearity, no validation, causal language in planning |
| Consumers | revenue planning meeting, finance forecast, pricing review |
| Requirement | validated model with diagnostics and claim boundaries |

## 3. Target Architecture

```text
 weekly fact table --> scatter matrix + correlation review
     |
 [1] collinearity census (VIF) --> drop or regularise, with justification
 [2] least squares with SE and intervals per coefficient
 [3] diagnostics: residual vs fitted, leverage vs e^2, Cook's D
     |
 [4] form check: curvature -> term or transform
     |
 [5] validation: rolling-origin backtest, not in-sample R^2
     |
 [6] claim register: association stated, causal claims refused
     |
 consumers: planning (interval), pricing (no causal claim), finance (validated forecast)
```

## 4. Component Responsibilities

### 4.1 Model build

- Weekly fact table with promotion and macro features joined before analysis, never after
- Collinearity census per predictor with VIF, and a documented decision to drop or regularise
- Coefficient table with standard errors, intervals and a stability measure across refits
- Nonlinearity handled with terms or transforms validated by backtest rather than by in-sample fit

### 4.2 Diagnostics and validation

- Residual, leverage and influence plots published with every model version
- Rolling-origin backtest rather than a random split, because weeks are ordered
- Validated error reported alongside R², with the model version recorded
- Coefficient sign-stability tracked across refits as a drift signal

### 4.3 Claim governance

- Claim register distinguishing association from causation for every published statement
- Consumers told explicitly what questions the model cannot answer
- Pricing review gets association language only, with the confounding risk named
- Any causal claim requires a designed experiment, not this model

### 4.4 Operations

- Model versioned with its data snapshot and coefficient table
- Refit schedule with automated sign-stability alerting
- Consumer-specific views: planning gets intervals, finance gets validated forecasts
- Documented response when a coefficient sign flips or validation error degrades

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Rebuild the fact table; scatter matrix and correlation review with the team |
| Week 2 | Collinearity census; drop or regularise with a recorded decision |
| Week 3-4 | Diagnostics published; rolling-origin backtest replacing in-sample R² as the headline |
| Week 5 | Claim register and consumer views; pricing review reframed around association |
| Week 6 | Sign-stability alerting and refit schedule; first quarterly model review |

## 6. Runbook (copy-paste)

```bash
# Coefficient table with standard errors and intervals
curl -s 'localhost:8085/models/revenue/v7/coefficients' | jq '.[] | {term,estimate,se,ciLow,ciHigh,vif}'

# Diagnostics for a model version
curl -s 'localhost:8085/models/revenue/v7/diagnostics' | jq '{curvature,maxLeverage,maxCook,signStable}'

# Rolling-origin validation versus in-sample fit
curl -s 'localhost:8085/models/revenue/v7/validation' | jq '{r2InSample,rmseBacktest,weeks}'

# Coefficient sign stability across recent refits
curl -s 'localhost:8085/models/revenue/sign-stability' | jq '.[] | {term,flips,lastFiveSigns}'

# What the model may and may not be used to claim
curl -s localhost:8085/models/revenue/claims | jq '{allowed,refused,reasons}'
```

## 7. Observability and SLOs

- Validation: rolling-origin backtest error reported with every version; R² labelled in-sample.
- Stability: coefficient sign flips per quarter, expected zero after the collinearity fix.
- Diagnostics: influence and curvature published with every model version.
- Governance: published claims audited against the claim register (target 100%).
- Use: consumers stating questions the model cannot answer, tracked in review notes.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Coefficients flip sign every quarter | Residual collinearity | VIF census, drop or regularise, and alert on sign flips |
| Backtest error far worse than in-sample R² suggests | Overfitting or time-ordered structure ignored | Use rolling-origin backtest as the headline metric and add regularisation |
| Planning cites the model as causal | Model used for attribution | Claim register refuses causal language; causal questions require an experiment |
| A high-leverage week changes the whole coefficient table | Influential point not handled | Influence diagnostics published; refit with robust weighting and report both |
| The model is refit monthly and quietly replaces itself | No versioning of model or data | Version the model with its snapshot and coefficient table; changes reviewed |

## 9. Prevention Backlog

- Regularised variants evaluated on the same rolling backtest.
- Hierarchical model by category so global coefficients stop being averages of opposites.
- Automated curvature detection proposing terms before refit.
- Counterfactual and experimental designs for the questions the model refuses.
- Quarterly model review with sign-stability and validation as standing agenda items.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **NIST/SEMATECH e-Handbook of Statistical Methods**: https://www.itl.nist.gov/div898/handbook/
  Authoritative reference for estimators, measures of central tendency and dispersion, with the guidance on when each is appropriate.
- **SciPy — statistics module documentation**: https://docs.scipy.org/doc/scipy/reference/stats.html
  Reference implementations of distributions, hypothesis tests and descriptive statistics; the semantics this lab re-implements in plain Java.

> The deliverable is a revenue model whose diagnostics are published, whose validation is out of sample, and whose claims register stops a planning meeting from reading association as causation.
