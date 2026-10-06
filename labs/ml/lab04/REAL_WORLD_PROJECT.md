# REAL_WORLD_PROJECT — Inbound Email Threat Triage

**Track:** ml  |  **Lab:** lab04  |  **Level:** Advanced

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

An enterprise mail provider must decide, per message, whether to deliver, quarantine or route to a security analyst. The scoring budget is 12 ms per message, the analyst queue is fixed at 400 per hour, and a false negative means a phishing click in a customer's inbox.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Daily volume | ~40M inbound messages/day, peak 900 msg/s |
| Positive rate | 0.4% malicious, rising during incident windows |
| Analyst capacity | 400 messages/hour = 9,600/day |
| Latency budget | p99 < 12 ms, including envelope and body features |
| Hard constraint | quarantine decisions must be explainable to the customer on request |

## 3. Target Architecture

```text
 MTA --> Header/URL/reputation features (cached, precomputed)
            |
      Streaming classifier (SVM or gradient-boosted alternative)
            |                        |             +--> shadow score (challenger) --> offline comparison
            |
   Policy engine (rules + threshold + customer overrides)
            |
   +--------+----------+-----------+
   |        |          |           |
 deliver  quarantine  analyst   customer
 (99%)    (0.35%)    queue      override
                                     |
                          appeal/explanation service <-- decision log

   Feedback: analyst verdicts (minutes) + user reports (hours) --> labels
```

## 4. Component Responsibilities

### 4.1 Feature service

- Envelope and authentication results (SPF/DKIM/DMARC) precomputed by the MTA
- Reputation lookups for sender IP, sending domain and URL host with local caching
- Attachment and link features computed in a streaming stage under 3 ms
- Feature contract versioned; a schema change triggers a shadow period before enforcement

### 4.2 Model tier

- Linear SVM first: at 900 msg/s a kernel model is unnecessary and unprovable at scale
- RBF kernel retained only for the low-volume analyst-facing re-scoring path
- Model and calibrator loaded from the registry with hot reload and rollback
- Shadow challenger scores 100% of traffic and is compared weekly on matured labels

### 4.3 Policy engine

- Threshold per customer tenant, with the highest-sensitivity tenants receiving the lowest threshold
- Overrides: allowlists, brand impersonation rules and known-safe senders
- Every decision writes score, threshold version, feature snapshot id and rule hits
- Fail-safe default: on model or feature outage, escalate to a stricter static rule set

### 4.4 Feedback and monitoring

- Analyst verdicts arrive in minutes; user reports in hours — both become labels
- Daily precision/recall at the analyst cut, reported by tenant tier
- Drift on reputation features (a new sending domain can shift everything)
- Weekly red-team corpus scored as a fixed regression check before promotion

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship the static rule set with explanations and full decision logging |
| Week 2 | Linear SVM in shadow; compare against rules for 7 days on live traffic |
| Week 3 | Calibration and per-tenant thresholds; security review of false-negative paths |
| Week 4 | Canary at 5% of traffic with a one-command revert; verify analyst queue depth |
| Week 5 | Ramp to 50%, then 100% of scoring decisions; keep the rule set as the documented fallback |

## 6. Runbook (copy-paste)

```bash
# Which model and threshold are live?
curl -s localhost:8080/admin/model | jq '{version,thresholdSet,ageHours}'

# Quarantine rate vs the 7-day baseline
curl -s 'localhost:8080/admin/rates?window=1h' | jq '{quarantine,baseline,delta}'

# Force the stricter static rule set (safe mode)
curl -XPOST localhost:8080/admin/mode -d '{"mode":"RULES_SAFE"}'

# Roll back the model, keep the policy engine
curl -XPOST localhost:8080/admin/rollback -d '{"to":"threat-svm-2026-09-18"}'

# Explain one decision for a customer appeal
curl -s 'localhost:8080/admin/explain?messageId=m-9931' | jq '.score,.rules,.features'
```

## 7. Observability and SLOs

- SLO: p99 scoring < 12 ms; availability 99.99% (a scoring outage quarantines or escalates, never silently delivers).
- Security: false-negative rate on the analyst-reviewed set; true-positive rate on the red-team corpus.
- Operations: analyst queue depth vs capacity, and median time-to-verdict.
- Customer: false-quarantine rate per 10k messages, and appeal overturn rate.
- Model: calibration by tenant tier; shadow challenger delta on matured labels.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Reputation cache misses flood the feature path | cache eviction storm after a config change | Serve the stale-but-bounded cache, degrade to authentication-only features, page on p99 |
| Quarantine rate doubles overnight | a new sending domain is being scored as malicious | Roll back the model, inspect the top changed features, keep the static rules |
| Latency breaches the 12 ms budget | synchronous DNS or reputation lookups on the hot path | Enforce cached-only lookups with a hard timeout and fail closed to a neutral feature value |
| Customer appeal cannot be answered | decision log missing the feature snapshot id | Every decision stores the snapshot id; without it the appeal stalls |
| Analyst queue exceeds 400/hour | threshold loosened by a config push | Restore the last approved threshold set and page the security duty manager |

## 9. Prevention Backlog

- Red-team corpus as a scheduled regression job gating every promotion.
- Per-tenant threshold model with an approval workflow instead of direct config edits.
- Shadow-to-promotion automation with a two-week minimum shadow period.
- Explainability endpoint for appeals with a customer-readable reason list.
- Quarterly rollback drill measuring detection-to-mitigation time.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **scikit-learn — Linear Models user guide**: https://scikit-learn.org/stable/modules/linear_model.html
  Canonical OLS/ridge/lasso derivation and the least-squares objective; the reference for what a closed-form solution actually guarantees.
- **NumPy — linalg module reference**: https://numpy.org/doc/stable/reference/routines.linalg.html
  `linalg.solve`, `lstsq`, `pinv`, SVD — how practitioners avoid forming XᵀX explicitly and what conditioning means in practice.

> The deliverable is a 12 ms decision plus an explanation a customer can be shown, backed by a static fallback that keeps the system safe when the model is unavailable.
