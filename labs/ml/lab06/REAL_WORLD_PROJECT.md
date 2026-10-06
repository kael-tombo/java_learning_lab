# REAL_WORLD_PROJECT — Inbound Spam and Phishing Filter

**Track:** ml  |  **Lab:** lab06  |  **Level:** Intermediate

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

A mid-size business mail provider filters 6M messages a day. A legitimate message lost to the spam folder costs a customer; a phishing message delivered costs far more. You own the filter, its false-negative budget and the explanation shown to an end user who disputes a decision.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Daily volume | ~6M messages/day, peak 1,400 msg/s |
| Positive rate | 4–8% spam, 0.2–0.5% phishing, both rising during campaigns |
| Latency budget | p99 < 25 ms per message, including reputation lookups |
| Contractual constraint | false positives must be under 0.05% with a one-click restore |
| Success metric | phishing delivery rate and per-message compute cost |

## 3. Target Architecture

```text
 MTA --> auth results (SPF/DKIM/DMARC) + reputation (cached)
            |
        NB scorer (multinomial over headers/body/URL tokens)
            |                                 |                      +--> per-token contribution log (explanations)
            v
        NB-SVM / boosted challenger (shadow)
            |
   Policy layer: bayes + reputation + campaign rules + tenant overrides
            |
  +--------+---------+------------+-----------+
  |        |         |            |           |
deliver  spam folder  quarantine  restore    appeal
 (95%)     (4.2%)     (0.5%)    request     service
                                     |
                        explain endpoint + one-click allowlist
```

## 4. Component Responsibilities

### 4.1 Feature and scoring tier

- Three token views: headers, visible body text, and URL host/path tokens
- Separate weights per view, tuned on a held-out split rather than assumed
- NB scores every message; the score plus top tokens are stored for 30 days for appeals
- Challenger model scores 100% of traffic in shadow; weekly comparison on matured labels

### 4.2 Policy layer

- Bayes threshold per tenant, with an approval workflow for changes
- Reputation and authentication results act as overrides in both directions
- Campaign rules (known phishing infrastructure) bypass the model entirely
- Every decision records score, threshold version, token contributions and rule hits

### 4.3 Feedback and reputation

- User restore requests are the strongest available label and arrive within minutes
- Phishing confirmations arrive in hours; blocklist propagation in minutes
- Restore requests beyond a per-tenant budget trigger an automatic review
- Confirmed phish propagate to the blocklist before the next retry attempt

### 4.4 Operations and compliance

- p99 latency budget enforced with a timeout that falls back to header-only scoring
- Per-tenant false-positive tracking against the contractual 0.05% ceiling
- Appeal service exposing the top contributing tokens in plain language
- Full decision log retained 12 months for contractual and regulatory requests

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship header-only Bayes with logging and the restore request flow |
| Week 2 | Add body and URL views with tuned weights; watch the FP rate against the ceiling |
| Week 3 | Platt calibration and per-tenant thresholds with approval workflow |
| Week 4 | Challenger in shadow; confirm no regression on confirmed phish |
| Week 5 | Appeal explanations live; postmortem drill with a simulated campaign |

## 6. Runbook (copy-paste)

```bash
# Filter health, threshold set, model version
curl -s localhost:8080/admin/filter | jq '{version,thresholdSet,ageHours}'

# Spam and quarantine rates vs the 7-day baseline
curl -s 'localhost:8080/admin/rates?window=1h' | jq '{spam,quarantine,baseline}'

# Temporary safe mode: header-only scoring, stricter threshold
curl -XPOST localhost:8080/admin/mode -d '{"mode":"HEADER_ONLY_STRICT"}'

# Tenant override (allow a sender/domain) with audit logging
curl -XPOST localhost:8080/admin/tenant-override -d '{"tenant":"acme","allow":"acme-mail.example"}'

# Explain one quarantined message for an appeal
curl -s 'localhost:8080/admin/explain?messageId=m-4471' | jq '.score,.topTokens,.rules'
```

## 7. Observability and SLOs

- SLO: p99 < 25 ms; availability 99.95%; a scoring outage degrades to header-only, never to deliver-all.
- Security: phishing delivery rate, measured against confirmed phish per 100k messages.
- Contract: false-positive rate per tenant, hard ceiling 0.05%.
- Model: macro-F1 on matured labels; calibration error by tenant tier.
- Business: restores per 1,000 messages (a proxy for user trust) trending down.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A phishing campaign gets through at volume | Novel infrastructure unseen in training | Emergency blocklist propagation from confirms; add campaign rules; retrain on the confirmed set |
| Spam folder complaints spike | Threshold push or a tenant-specific vocabulary problem | Restore to the last approved threshold set, inspect per-tenant scores, add tenant tokens |
| p99 breaches 25 ms | Synchronous reputation lookup added to the hot path | Enforce cached-only lookups with a hard timeout; degrade to header-only scoring |
| A legitimate bulk sender is filtered | New sending domain with unfamiliar tokens | Add a tenant override with audit logging; retrain with the sender's vocabulary |
| Calibration drifts after a large retrain | New class mix in the training window | Re-fit the calibrator on a fresh validation split before promotion |

## 9. Prevention Backlog

- NB-SVM challenger promoted once it beats Bayes on matured labels at equal FP rate.
- Per-view weight tuning automated as part of the retrain job.
- Appeal explanation service translated into user-facing language with a quality review.
- Campaign-response drill: a simulated phishing wave timed end to end each quarter.
- Contractual FP ceiling enforced as an automated release gate, not a dashboard.

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

> The deliverable is a filter that loses phishing, explains every quarantine, keeps its contractual false-positive ceiling, and can degrade safely when a dependency is down.
