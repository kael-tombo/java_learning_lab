# Lab 14: Production Incident Response & RCA — Real World Project

## Scenario: "Forty-Six Minutes and a Postmortem Nobody Read"

You are the SRE lead for a payments platform: 16 Spring Boot 3 services, Java 21, Kubernetes, ~70 engineers, an 8-person on-call rotation, and a formal incident process that everyone believes is working.

**The incident** — Tuesday 02:14.

1. **02:14** — Release of `ledger-writer` 3.2.0 begins. The migration takes an `ACCESS EXCLUSIVE` lock on a 380M-row table.
2. **02:16** — Queries queue. Connection pools exhaust. `ledger-writer`, `statement-service`, and `reporting` begin timing out.
3. **02:31** — First customer complaint. There is no alert on pool saturation, no alert on 5xx for these services, and no alert on database lock waits.
4. **02:31–02:52** — The deployer, on a call, does not suspect the migration (application logs show connection timeouts, not SQL errors). Investigation wanders for 21 minutes.
5. **02:52** — The migration is killed. Queued queries flood the primary; another 4 minutes of total unavailability.
6. **02:52–03:00** — Service recovers. **Total customer-visible impact: 46 minutes.**
7. **03:20** — A postmortem is written. It is 6 pages, well-formatted, and correctly assigns blame to nobody. It lists 11 action items.
8. **Six weeks later** — Of the 11 action items, 4 are complete, 5 are past due and unowned, 2 were closed as "won't fix". Nobody has measured whether the incident class recurred. The process is unchanged.

**Your job over 4 weeks**: make incident response measurably better. Establish the time decomposition so you know which lever matters, build a declaration and command model the team actually uses, make postmortem actions owned and tracked to completion, and prove with recurrence data whether any of it worked.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Measure what you have (Day 1–4)

### 1.1 Incident history

For the last 12 months, extract every incident from the tracking system: declared time, detected time, acknowledged, mitigated, resolved, severity, services affected, cause class, whether it was a recurrence.

**Deliverable 1 — Incident dataset** with the time decomposition per incident and the computed MTTD/MTTA/MTTM/MTTR distributions (median, p85, worst).

### 1.2 Where does the time actually go?

Aggregate the decomposition across all incidents. Which phase dominates? Is it detection, diagnosis, decision, or mitigation?

**Deliverable 2 — Phase analysis**: the dominant phase, the distribution, and the cheapest intervention for that phase. Be prepared for the answer to be "detection" even if the team believes it is "diagnosis".

### 1.3 Alert quality audit

Every paging alert in the estate: pages fired in 90 days, how many caused an action, owner, runbook present.

**Deliverable 3 — Alert audit** with `actionable_fraction`, `pages_per_shift`, and the ranked list of offenders. Also the on-call load calculation (interruption hours per shift per engineer).

### 1.4 Postmortem audit

Every postmortem in 12 months: action items, owners, dates, completion status, and whether the incident class recurred afterwards.

**Deliverable 4 — Postmortem audit**: completion rate, overdue rate, recurrence rate per class, and the computed *effective* risk reduction (`completion_rate × action_effectiveness`). This is your business case.

### 1.5 Incident class taxonomy

Group the 12 months of incidents into stable classes (e.g. "pool exhaustion", "post-deploy in-flight failures", "certificate expiry", "dependency latency", "data inconsistency", "capacity").

**Deliverable 5 — Class taxonomy** with counts, MTTR per class, and recurrence counts. Recurrence is the key column: a class that keeps coming back tells you the previous actions did not work.

---

## Phase 2 — Command and coordination (Day 4–8)

### 2.1 Declaration criteria

Pre-declared, objective, and posted where responders will see them:

| Trigger | Severity | Response target |
|---|---|---|
| Money movement halted or incorrect | SEV-1 | Commander in 5 min, first update in 15 min |
| > 5% request failures on a customer path for > 5 min | SEV-1 | as above |
| Degradation above SLO burn threshold | SEV-2 | Commander in 15 min |
| Any novel failure with no runbook | SEV-2 | as above |
| Single-service degradation with a workaround | SEV-3 | Normal on-call, no incident channel |

Anyone may declare. State that explicitly.

**Deliverable 6 — Declaration criteria** published in the on-call handbook, the alert runbooks, and the service templates' runbook stubs.

### 2.2 Roles and the timeline template

Three roles with explicit duties: **Incident Commander** (coordination and decisions only), **Operations Lead** (mitigation and diagnosis), **Communications Lead + Scribe** (external/internal updates and the timeline). For SEV-3, the on-call fills all three and that is fine.

Rules, stated as rules:
- One production change at a time, announced with the exact command and its rollback.
- A change-freeze for unrelated deploys during SEV-1.
- Timeline entries append-only, single clock, hypotheses marked unverified, refuted hypotheses marked REFUTED.
- A "no change" update on schedule even when there is nothing new.

**Deliverable 7 — Incident response standard** with the role definitions, the timeline template, and the change protocol. Reviewed and acknowledged by the whole rotation.

### 2.3 Rollback decision rule

The rule that stops 20 minutes of debate at 02:31:

```
IF (correlation with the last change is high)
   AND (rollback is available: schema + data + contracts permit it)
   AND (the previous version is safe against current state)
THEN roll back immediately; diagnose after.
ELSE mitigate forward, and name the decision + rationale in the timeline.
```

Every service gets a declared rollback availability status: `available`, `partially available` (with conditions), or `unavailable — fix-forward playbook required`.

**Deliverable 8 — Rollback decision rule** plus a per-service rollback availability register.

---

## Phase 3 — Make postmortems produce something (Week 2)

### 3.1 Postmortem structure (enforced)

Summary → impact (with numbers) → timeline reference → what went well → what didn't → **contributing factors table** (never a single root cause) → actions → recurrence check → open questions.

Banned as a cause: "human error", "operator error", "should have known". Each must be replaced with the design/interface/tooling gap.

**Deliverable 9 — Postmortem template** plus a linter that rejects a postmortem containing a banned phrase or missing an owner/date/definition-of-done column.

### 3.2 Action tracking as real work

- Every action has a named owner, a date, and an observable definition of done.
- Actions live in the normal team backlog with the postmortem as the source.
- A weekly review of overdue actions with the engineering manager.
- A completion-rate metric reported monthly.

**Deliverable 10 — Action tracking process**, with the monthly completion-rate report for the first month and the escalation path for overdue items.

### 3.3 Review cadence

- Incident review within 48 hours (facts fresh, memory usable).
- Written postmortem within 5 business days.
- Monthly class-level review: counts, MTTR, recurrence, action completion.
- Quarterly systemic review: which classes keep recurring and what structural change is required.

**Deliverable 11 — Review cadence** with the meeting agendas, the class-level dashboard, and the first monthly review held.

---

## Phase 4 — Reduce the dominant phase (Week 2–3)

Acting on the Phase 1.2 finding:

**If detection dominates** (as it will): build the alerting — 5xx rate per service, pool saturation (`pending > 0`), connection acquisition time p99, database lock waits, queue depth, certificate expiry, disk space, and burn-rate SLO alerts per service. Measure the expected detection time for each alert class using the threshold sensitivity arithmetic.

**If diagnosis dominates**: build the "recent changes" panel and the change-correlation runbook, plus per-service dashboards with dependency latency broken out.

**If decision dominates**: ship the rollback decision rule and the rollback availability register.

**If mitigation dominates**: write and *test* the top 10 runbooks; add kill switches (flag-driven) for the expensive optional paths.

**Deliverable 12 — Phase-reduction work** with the before/after decomposition on the same scenarios from Phase 1.

---

## Phase 5 — On-call health (Week 3)

- Page budget: ≤ 1–2 actionable pages per shift. Measure and publish.
- Flaky alerts: one re-notification, then a ticket. No page loops.
- Handoff: written, covering active incidents, known issues with workarounds, recent deploys, flaky alerts.
- Escalation ladder with the acknowledgement-probability arithmetic and a called human at 10 minutes.
- Compensation for out-of-hours and for incident time.

**Deliverable 13 — On-call health report**: pages/shift before and after, actionable fraction, escalation ladder, acknowledgement probabilities, comp-time policy.

---

## Phase 6 — Prove it (Week 3–4)

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Replay the 02:14 lock incident in staging (a 380M-row table, `ACCESS EXCLUSIVE`) | detected in < 5 min by a pool-saturation or lock-wait alert; declared within 10 min; mitigated < 30 min |
| S2 | Replay with detection only (no mitigation practice) | measures the pure detection improvement |
| S3 | Two independent faults in the same window | timeline shows both identified separately; no single-cause assumption |
| S4 | Bad release, rollback available | rolled back per the decision rule; diagnosis after |
| S5 | Bad release, rollback unavailable (schema changed) | fix-forward playbook followed; decision recorded in the timeline |
| S6 | Revoke the responder's prod access | the failure is found and resolved in < 10 min, or the workaround is identified |
| S7 | Expired certificate | alerted before expiry; renewal runbook works |
| S8 | Game day: dependency at 3 s | runbook usable unaided; gaps logged as actions |
| S9 | Rollback drill on all 16 services | rollback time measured; unavailable rollbacks listed |
| S10 | Postmortem of S1 written, reviewed, linted | passes the linter; all actions have owners and definitions-of-done |
| S11 | Action completion after 30 days | > 70% completion; overdue < 10% |

**Deliverable 14 — Incident readiness test report** with all eleven scenarios, measured times, and fixes for anything missed.

---

## Phase 7 — Institutionalize and quantify (Week 4)

| Metric | Before | After |
|---|---|---|
| MTTD (median / p85) | 14 min / 41 min | < 3 min / < 10 min |
| MTTM (median) | 71 min | < 30 min |
| MTTR (median / p85) | 106 min / 4 h | < 45 min / < 2 h |
| Incidents with a timeline document | ~20% | 100% of SEV-1/SEV-2 |
| Incidents declared within 10 min | unknown | > 80% |
| Paging alerts that caused an action | 31% | > 80% |
| Pages per shift | 6 | ≤ 2 |
| Postmortem action completion rate | 36% (4/11 in the sample) | > 70% |
| Overdue action rate | 45% | < 10% |
| Incident classes with recurrence tracking | 0 | all |
| Recurrence rate on targeted classes | unmeasured, classes recurring | measurably reduced per class |
| Services with a declared rollback status | 0 | 16 |
| Services with a *tested* runbook | 3 | 16 |
| Game days per quarter | 0–1 | ≥ 1 per quarter, with findings tracked |

Institutionalize: incident response becomes part of the production readiness review (a service without a runbook and a declared rollback status cannot launch); the class taxonomy and recurrence metrics become a quarterly leadership report; the phase decomposition is a standing dashboard so the team always knows which lever matters.

**Deliverable 15 — Business case + institutionalization**, presenting the cost of the 46-minute incident class against the cost of detection alerting, runbooks, and the process change.

---

## Deliverables checklist

- [ ] Phase 1 incident dataset, phase analysis, alert audit, postmortem audit, class taxonomy.
- [ ] Phase 2 declaration criteria, response standard, rollback decision rule + register.
- [ ] Phase 3 postmortem template + linter, action tracking, review cadence.
- [ ] Phase 4 phase-reduction work with before/after decomposition.
- [ ] Phase 5 on-call health report.
- [ ] Phase 6 eleven-scenario readiness test report.
- [ ] Phase 7 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Measurement | "Our MTTR is about an hour" | Per-incident phase decomposition, distributions, and the dominant phase named with evidence |
| Alerting | "We alert on 5xx" | Actionable fraction and pages-per-shift measured; detection sensitivity computed per alert class |
| Command | "We have a Slack channel" | Declared criteria, roles with duties, one-change-at-a-time protocol, append-only timeline with refuted hypotheses kept |
| Decisions | "We rolled back" | Pre-declared rollback rule with the three preconditions, and a per-service availability register |
| Postmortem | "It was blameless" | No banned cause phrases, contributing-factors table, actions with observable definition-of-done, recurrence check |
| Actions | "We track them" | Completion and overdue rates measured; effective risk reduction computed from completion × effectiveness |
| Recurrence | "It hasn't happened since" | Class-level recurrence rates with Poisson bounds on zero-observation claims |
| Proof | "We ran a drill" | Replays the actual lock incident, two-fault discrimination, access revocation, certificate expiry |
| Sustainability | "We wrote a process" | PRR gate, quarterly class report, standing decomposition dashboard, comp policy |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Google SRE Workbook — "Managing Incidents" and "Postmortem Culture"** — https://sre.google/workbook/managing-incidents/ and https://sre.google/workbook/postmortem-culture/ — the canonical source for incident command structure (incident commander, communications lead, operations lead), the guidance that the IC should not be the one debugging, the "preparedness" framing (runbooks, training, alerting as the things that make an incident survivable), and the blameless-postmortem argument with its warning against "action items" that are really just restated good intentions. Also the source for the incident-review-within-a-few-days practice and the "no-blame but real accountability" framing.
2. **Google SRE Workbook — "Alerting on SLOs" (burn-rate paging) and "Being On-Call"** — https://sre.google/workbook/alerting-on-slos/ and https://sre.google/workbook/being-on-call/ — the authoritative treatment of multi-window multi-burn-rate paging (which directly reduces MTTD for the class of degradation you cannot threshold-alert on), and the on-call health material: sustainable rotation, escalation, handoff, and the argument that alert quality is an engineering responsibility rather than a cultural one. Use these to justify the alert-quality audit in Phase 1.3 and the on-call budget in Phase 5.

Additional anchors worth verifying: your own incident tracker and status-page provider's severity definitions and notification cadences; the exact acknowledgement and escalation semantics of your paging tool (PagerDuty/Opsgenie/VictorOps differ in whether a page counts as acknowledged or resolved); and your database's lock-wait and pool-saturation metric names (`pg_stat_activity.wait_event_type = 'Lock'` in PostgreSQL, for example) so the Phase 4 alerts use metrics that actually exist in your version.

---

## Reflection questions

1. Detection was 17 minutes and required no incident skill. Why is it usually the last thing teams invest in?
2. The postmortem had 11 action items and four were completed. What would make five more get done — and is the answer more discipline, or a different mechanism?
3. Nobody measured recurrence. What would a recurrence metric for one incident class look like in your estate, and what threshold would trigger architectural escalation?
4. The 46-minute incident was caused by a migration. Which of your services could not be rolled back today, and how would you find out?
5. If your dominant time phase is diagnosis, what is the fastest structural change that reduces it — and would alerting have been the wrong investment?
