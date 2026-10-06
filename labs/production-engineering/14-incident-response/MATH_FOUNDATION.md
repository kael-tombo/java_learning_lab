# Lab 14: Production Incident Response & RCA — Math Foundation

Incident response is quantified by time budgets, blast radius, and trend metrics. You cannot improve what you have not measured, and you cannot measure what you never timed.

---

## 1. The incident time decomposition

```
T_total = T_detect + T_acknowledge + T_assess + T_decide + T_mitigate + T_verify + T_restore
MTTD    = T_detect
MTTA    = T_detect + T_acknowledge
MTTM    = T_detect + T_acknowledge + T_assess + T_decide + T_mitigate
MTTR    = MTTM + T_verify + T_restore
```

Worked example from a real incident:

| Phase | Duration | Notes |
|---|---|---|
| Detect (customer report, no alert) | 17 min | the only detection path was a complaint |
| Acknowledge | 6 min | on-call saw the page |
| Assess | 11 min | "which service?" |
| Decide | 14 min | debated rollback safety |
| Mitigate | 21 min | applied the forward fix |
| Verify | 8 min | watched metrics |
| Restore | 29 min | full resolution |

```
MTTD = 17 min     (33% of the total — the cheapest to improve)
MTTM = 69 min     T_total = 106 min
MTTR = 106 min
```

**Conclusion**: detection was the largest single lever and required zero incident skill. Had alerting caught it at 60 s, MTTR would have been ~90 minutes with the same responders. **Conclusion 2**: without the decomposition, a team would have concluded "we need better runbooks" and bought nothing.

---

## 2. Detection time from threshold choice

For a metric with daily range σ, a threshold of `k·σ` above the mean gives:

```
P(false positive per day) ≈ N × (1 − Φ(k))         (N = number of independent evaluation windows/day)
P(true detection within t) = 1 − (1 − p_detect)^n    (n = windows in t)
```

`N = 288` (5-minute evaluation), `k = 3`:
```
false positives/day ≈ 288 × 0.00135 = 0.39/day  →  ~11 per month: too many for a pager
k = 4: 288 × 3.2e-5 = 0.009/day  →  0.28/month: acceptable
```

Detection sensitivity for a regression of 2σ lasting 30 minutes (`n = 6` windows):
```
p_detect per window ≈ 1 − Φ(2) = 0.023
P(detect within 30 min) = 1 − (1 − 0.023)^6 = 12.9%     →  usually missed
```

For a 4σ regression, 30 minutes:
```
p = 1.3e-4 → P(detect) = 1 − (1−0.00013)^6 = 0.08%      →  effectively never
```

**Conclusion**: threshold alerts detect only very large, very long regressions. This is the quantitative argument for burn-rate alerts over SLOs — a burn-rate alert is sensitive to the *fraction of budget consumed*, which is far more sensitive than a deviation threshold on a noisy metric. The 17-minute detection in the scenario above is not a monitoring-luck problem; it is the expected behaviour of threshold alerting.

---

## 3. Blast radius accumulation

```
users_affected(t) = Σ_over_time affected_fraction × user_traffic(t)
```

A service at 40% of requests affected for 46 minutes, 2M daily users arriving roughly uniformly:
```
affected_requests = 0.40 × 46/1440 × 2,000,000 = 25,556 requests
customers_impacted ≈ 25,556 × 0.8 (some retry/succeed) ≈ 20,400 distinct customers
```

Scaled to the incident's stated duration (46 min) and severity (payment timeouts):
```
revenue_at_risk = affected_fraction × peak_rps × duration × value_per_request
```

**Conclusion**: the cost of a detection improvement is directly computable:
```
cost_saving_from_MTTD_reduction = Δminutes × peak_rps × 0.4 × value_per_request
Δ 16 min at 300 rps peak, $18/request  →  16/60 × 300 × 0.4 × 18 = $576 per incident, per occurrence
```
Annualised at 20 incidents/year: ~$11,500 in direct revenue, plus reputational and support cost. Compare to a one-off alerting investment. This is how you fund detection work.

---

## 4. Mitigation effectiveness and the observability of a mitigation

```
error_rate(t) = baseline + contribution_from_cause(t)
mitigation_effective iff error_rate(t + Δ) ≤ baseline + ε
```

Baseline `0.05%`, incident `18%`, mitigation applied at t=38 min:
```
required drop = 17.95 pp
observed at t=46: 0.12%  →  Δ = 17.88 pp recovered of 17.95 (99.6%)
```

The detection of a mitigation's success has its own latency:
```
T_confirm = 3 × metric_window_length + scrape_interval + evaluation_delay
3 × 1 min + 15 s + 30 s ≈ 3.75 min
```

**Conclusion**: confirm mitigations over a window long enough to see the effect — verifying after 30 seconds of a 1-minute aggregation is how teams "fix" something that was never fixed and then re-break it with the next change.

---

## 5. Change failure rate and the DORA measures

```
change_failure_rate      = failed_deployments / total_deployments
deployment_frequency     = deploys per day per service
lead_time_for_changes    = commit_to_production (median, p85)
time_to_restore          = detect + decide + restore, per incident
```

Scenario baseline: 340 deployments/90 days, 19% failure:
```
failed_deployments = 65
deployments_per_day = 3.8
```

After progressive delivery catching ~70% of user-visible regressions at ≤ 25% traffic:
```
failures_reaching_100% = 65 × (1 − 0.7) ≈ 19  →  CFR ≈ 5.6%
incidents_reduced ≈ 46 over 90 days ≈ 15 per quarter
```

Cost per prevented incident:
```
direct_cost_per_incident = revenue_at_risk + support_hours × rate + engineering_hours × rate
```

**Conclusion**: CFR is the metric that justifies release-engineering investment, and it is computable from data you already have (deploy records and incident records) — no new instrumentation needed to start.

---

## 6. Alert-to-action rate

```
actionable_fraction = pages_that_caused_an_action / total_pages
pages_per_shift     = pages_per_day / shifts_per_day
```

Estate: 6 pages/shift, 3.1 shifts/day → `18.6 pages/day`; 40% actionable:
```
actionable = 7.4/day   unactionable = 11.2/day
cost of unactionable = 11.2 × (interruptions × context_switch_cost)
                     ≈ 11.2 × 4 min = 45 min of focus time per engineer-day
```

Target: `actionable_fraction > 0.8` and `pages_per_shift ≤ 2`:
```
pages/day = 2 × 3.1 = 6.2   →  actionable ≈ 5.0/day
focus time returned ≈ (18.6 − 6.2) × 4 min = 50 min/engineer-day
```

**Conclusion**: alert quality has a quantified productivity cost, which is the argument that gets leadership attention — more persuasive than "people are tired of alerts".

---

## 7. Incident class recurrence

```
recurrence_rate(class) = occurrences_of_class_after_action / occurrences_before_action
```

Class "database connection exhaustion", 6 occurrences in 12 months before a pooler + budget gate:
```
occurrences_before = 6 in 12 months
after: 6 months elapsed, 1 occurrence
rate before = 0.5/month;  rate after = 0.167/month
reduction = 67%  →  effective (but continue measuring)
```

Class "post-deploy 502s from in-flight requests", 11 occurrences before adding `preStop` + grace period:
```
before: 11 in 12 months = 0.92/month
after: 0 in 4 months
upper bound on the after-rate (95% confidence) ≈ 3/4 = 0.75/month
→  observed zero is consistent with a rate up to 0.75/month: NOT yet proof
```

**Conclusion**: the statistics of small samples matter. "Zero incidents since the fix" is only evidence after enough exposure time has accumulated — use a Poisson-style bound rather than declaring victory.

---

## 8. Action item completion

```
completion_rate = completed_actions / total_actions
overdue_rate    = actions_past_due / total_actions
```

24 actions raised over 6 months, 15 completed, 6 past due, 3 not started:
```
completion_rate = 15/24 = 62.5%   overdue = 6/24 = 25%
```

Target: completion > 70%, overdue < 10%. At 62.5%:
```
expected_incident_class_reduction = completion × action_effectiveness
if each completed action removes 40% of its class:
effective_reduction = 0.625 × 0.40 = 25%   →  well below the 60% the postmortems implied
```

**Conclusion**: this is the single most useful postmortem statistic, because it converts "we learned something" into "our learning produced a 25% risk reduction, which we can compare against the target".

---

## 9. Rollout-risk assessment

```
expected_damage(change) = P(change_is_bad) × damage_if_bad_at_full_rollout
expected_damage_with_canary = P(bad) × [P(undetected_at_canary) × damage_full + P(detected) × damage_at_canary]
```

`P(bad) = 0.02`, `damage_full = $500k`, `damage_at_25% = $125k`, `P(detect at 25%) = 0.8`:
```
without canary: 0.02 × 500,000 = $10,000 expected
with canary:    0.02 × [0.2 × 500,000 + 0.8 × 125,000]
             = 0.02 × [100,000 + 100,000] = 0.02 × 200,000 = $4,000 expected
reduction = 60%
```

At 340 deployments/90 days (≈ 76 bad releases/year at 2%):
```
without canary: 76 × 10,000 = $760,000/yr expected damage
with canary:    76 × 4,000   = $304,000/yr
annual saving   ≈ $456,000  →  this is the business case for canary infrastructure
```

---

## 10. Escalation and acknowledgement latency

```
P(no acknowledgement in t) = (1 − ack_rate)^n    n = notification attempts
```

Ack rate per notification 0.85, escalate after 1 notification, again after 5 min, again after 10 min:
```
P(acked by 5 min) = 1 − 0.15 = 85%
P(acked by 10 min) = 1 − 0.15² = 97.75%
P(acked by 15 min) = 1 − 0.15³ = 99.66%
```

Add a human escalation (a named person is actually called) at 10 min:
```
P(acked within 10 min) rises to ~0.995 (a called human acknowledges far more reliably)
```

**Conclusion**: escalation ladders are a probability cascade; the design question is how many attempts, at what intervals, and with what channel escalation. The numbers justify an explicit "call a human" step rather than an unbounded sequence of pings.

---

## 11. On-call load and sustainability

```
pages_per_shift × mean_time_per_page = interruption_hours_per_shift
weekly_oncall_hours = pages_per_shift × 7 × mean_time / 60
```

6 pages/shift × 12 min each × 7 shifts:
```
weekly = 6 × 12 × 7 / 60 = 8.4 h/week of pure interruption
plus incident time (MTTM): 2 SEV-2/week × 1.2 h = 2.4 h
total ≈ 10.8 h/week
```

At 2 pages/shift with a 20% actionable rate:
```
weekly = 2 × 8 min × 7 / 60 = 1.9 h/week interruption
+ incident time unchanged = 4.3 h/week
```

**Conclusion**: the on-call burden is dominated by unactionable pages, not by real incidents. Reducing page count improves sustainability more than speeding up incident response.

---

## 12. Game day effectiveness

```
coverage   = (incident classes with a recent game day) / (total declared incident classes)
findings_per_game_day = defects found / game days run
time_to_hypothesis = time from injection to the first correct explanation
```

8 declared classes, 3 exercised in the last 6 months:
```
coverage = 37.5%
```

Findings over 4 game days: 23 (7 broken runbook commands, 5 missing dashboard links, 4 escalation gaps, 3 permission problems, 4 missing alerts)
```
findings_per_game_day = 5.75
```

If a game day costs 4 person-hours:
```
cost_per_finding = 4 / 5.75 = 0.70 person-hours per defect
```

**Conclusion**: game days are the cheapest defect-discovery mechanism available per finding, which is the argument for scheduling them routinely rather than after an incident.

---

## 13. Quick drills

1. Incident timeline: detect 17, ack 6, assess 11, decide 14, mitigate 21, verify 8, restore 29 min. MTTD / MTTM / MTTR? **Answer: 17 / 69 / 106 min. Detection was the biggest lever.**
2. `N=288` windows/day, threshold 3σ. False positives/month? **Answer: ~11 — too many to page on. Use 4σ or a burn-rate alert.**
3. 4σ regression lasting 30 min. Probability of detection? **Answer: ~0.08% — effectively never. Threshold alerts cannot see this.**
4. 40% of 2M daily users affected for 46 min. Distinct customers? **Answer: ~20,400.**
5. 340 deploys, 19% failure, canary catches 70%. Failures reaching 100% after? **Answer: ~19 (CFR 5.6%).**
6. 6 pages/shift, 40% actionable. Focus time lost per engineer-day? **Answer: ~45 min.**
7. 6 monthly occurrences → 1 in 6 months. Rate reduction? **Answer: 67%.**
8. 0 incidents in 4 months after a fix. Proved? **Answer: no — consistent with a rate up to ~0.75/month; keep measuring.**
9. 24 actions, 15 completed, each worth 40% class reduction. Effective risk reduction? **Answer: 62.5% × 40% = 25%, versus ~60% implied.**
10. `P(bad)=2%`, full-rollout damage $500k, 25% damage $125k, 80% detection. Expected damage with/without canary? **Answer: $4,000 vs $10,000 — 60% reduction, ~$456k/year at 76 bad releases.**
11. Ack rate 0.85 per ping, human called at 10 min. P(ack by 10 min)? **Answer: 99.5% with a called human.**
12. 3 of 8 incident classes exercised, 23 findings in 4 game days. **Answer: coverage 37.5%, 5.75 findings/game day, 0.7 person-hours per finding.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `MTTD / MTTA / MTTM / MTTR` decomposition | find the phase that dominates |
| `P(false positive/day) = N(1−Φ(k))` | choosing an alerting threshold |
| `P(detect) = 1 − (1−p)^n` | why threshold alerts miss small regressions |
| `expected_damage = P(bad) × damage_at_exposure` | business case for progressive delivery |
| `CFR = failed/total` | the release-engineering metric |
| `actionable_fraction = acted/pages` | alert quality |
| `recurrence_rate` per incident class | whether an action worked |
| `completion_rate × action_effectiveness` | real risk reduction from postmortems |
| `P(unacked in t) = (1−ack)^n` | escalation ladder design |
| `coverage = exercised_classes/total` | game-day programme health |
