# Lab 14: Production Incident Response & RCA — Mini Project

## Project: `IncidentLab` — Run the Incident, Write the Timeline, Prove the Actions Worked

**Time**: 10–14 hours | **Difficulty**: Intermediate–Advanced | **Stack**: Java 21, Spring Boot 3, Docker Compose (multi-service lab), Prometheus + Grafana, Loki or plain log files, Toxiproxy or a fault-injection sidecar, kubectl (kind) optional

Build a small system you can break on purpose, run a complete incident exercise with real roles and a live timeline, write a blameless postmortem, then verify the actions actually reduce recurrence.

---

## Part 1 — The system

```
[loadgen] → [gateway:8080] → [orders-api:8081] → [inventory:8082] → [postgres:5432]
                    └──→ [payments:8083] ──→ [external-psp (WireMock):9999]
```

Endpoints designed to fail in interesting ways:
- `POST /api/orders` — happy path, hits inventory and payments.
- `POST /api/orders?failRate=` — a fault-injection knob so *you* are the cause (used for the SLO-gone experiment).
- `GET /api/orders/{id}` — reads a cache; a cache-warm path.
- `GET /internal/reconcile` — the "safe" admin endpoint that will turn out not to be safe.

Two deliberate landmines, present from the start, neither documented:
1. `payments` opens a new HTTP connection per call to the PSP (no pooling) and holds a semaphore of 50.
2. `inventory` reads a config value `stock.threshold` from an environment variable that is **not** declared in the manifest, so it defaults to `Integer.MAX_VALUE` — a silently missing config value.

---

## Part 2 — The incident exercise (Part 2 is the deliverable)

### 2.1 Preconditions

- A staging environment you can break (or a local `docker compose` cluster).
- A Slack-like channel (or a shared doc pretending to be one).
- Three people, or three roles played sequentially if solo: **Incident Commander**, **Operations Lead**, **Comms Lead + Scribe**.
- Pre-written templates: incident declaration, internal update, external status update.
- A timeline document template.

### 2.2 The injected scenario

Do **not** tell the responders the cause. Inject:

1. **T+0** — `inventory` begins returning 500 for ~35% of calls after its connection pool to Postgres is exhausted (its Hikari pool is 5, and each request holds a connection for 800 ms because of a deliberate sleep).
2. **T+0** — No alert fires. The only signal is a `POST /api/orders` error rate that the lab's Grafana shows but nobody is watching.
3. **T+8 min** — You (as the "customer") file a ticket: "checkout fails intermittently".
4. **T+20 min** — The PSP (WireMock) starts returning 800 ms responses, so `payments` also begins to fail — a **second, independent** incident in the same window. This is deliberate: it tests whether the team can distinguish causes or assumes one root cause explains everything.

### 2.3 Timeline template

```markdown
| Time (UTC) | Type | Entry | By | Confidence |
|---|---|---|---|---|
| 11:47:02 | observation | orders-api 5xx rate 4% (from dashboard) | IC | confirmed |
| 11:47:40 | hypothesis | inventory pool exhaustion | ops | unverified |
| 11:49:10 | action  | kubectl scale orders-api 4→8 | ops | - |
| 11:52:00 | observation | 5xx rate unchanged after scale-out | IC | confirmed |
| 11:52:30 | hypothesis (refuted) | scale-out was the fix | IC | REFUTED - noted so nobody retries it |
```

Rules you enforce on yourself:
- Every entry timestamped from one clock.
- Hypotheses marked unverified; refuted ones marked **REFUTED** and kept (so the team stops re-arguing).
- Actions recorded with the exact command, so the postmortem can quote them.
- No editing after the incident; corrections are new rows.

### 2.4 Comms cadence

Every 15 minutes, write an update — including when nothing changed:

```
[STATUS 11:47] Investigating intermittent checkout failures. 5xx affecting ~4% of orders.
Impact: some customers cannot complete checkout. No data loss observed.
Next update: 12:02. Contact: #incident-2026-05-12
```

### 2.5 Declared objectives

- Declare within 5 minutes of the first customer report.
- Fill all three roles explicitly in the timeline header.
- One production change at a time, announced with its rollback.
- Mitigation attempt within 30 minutes.
- First postmortem within 48 hours.

**Deliverable**: `TIMELINE.md` — the complete timeline, the comms log (all updates including "no change"), and the declaration message.

---

## Part 3 — Time decomposition and blast radius

Fill this in from your timeline:

| Phase | Duration | Notes |
|---|---|---|
| Detect | | |
| Acknowledge | | |
| Assess | | |
| Decide | | |
| Mitigate | | |
| Verify | | |
| Restore | | |

Then compute:

```
MTTD, MTTA, MTTM, MTTR
```

Blast radius:

```
requests_failed = failed_fraction × duration × total_rps
distinct_customers ≈ requests_failed × (1 − retry_success_rate)
revenue_at_risk = requests_failed × value_per_request
```

And the cost of the detection gap:

```
cost_saving_from_faster_detection = Δminutes × peak_rps × failed_fraction × value_per_request
```

**Deliverable**: `DECOMPOSITION.md` with the table, the formulas filled in, and a statement of which phase dominated and which intervention would move it most cheaply.

---

## Part 4 — Root cause analysis, honestly

### 4.1 Five whys (for each of the two independent causes)

```
Symptom: checkout intermittently fails
  Why? orders-api returns 502 because inventory returned 500
    Why? inventory could not get a DB connection
      Why? its Hikari pool is 5 and each request holds a connection for 800 ms
        Why? a deliberate 800 ms sleep was added in a "realistic slow query" PR
          Why? nobody sized the pool against the new latency
```

### 4.2 Contributing factors (not one root cause)

For the incident overall:

| Factor | Type | Changeable? | Action |
|---|---|---|---|
| No alert on `orders-api` 5xx | detection gap | yes | |
| No alert on Hikari pool pending/active | detection gap | yes | |
| No runbook for "checkout failures" | response gap | yes | |
| Pool size not derived from latency | design gap | yes | |
| `inventory` and `payments` both degraded → unclear which to investigate | observability gap | partly | |
| On-call had no dashboard link for the order path | tooling gap | yes | |
| Rollback of `orders-api` would not have helped (both deps bad) | rollback availability | n/a — stated | |

**Conclusion rule for yourself**: if your postmortem says "human error" anywhere, rewrite it as a design/interface/tooling gap.

### 4.3 The undeclared-config landmine

Discover (or are told after the incident) that `stock.threshold` is missing from the manifest. Decide:
- Was it part of *this* incident? (No — it is a latent bomb. Log it separately.)
- How does an undeclared config value get detected? (Fail fast on missing required config; manifest schema validation.)

**Deliverable**: `POSTMORTEM.md` — full structure: summary, impact with numbers, timeline reference, what went well, what didn't, contributing factors table, actions with owner/date/definition-of-done, recurrence check, open questions.

---

## Part 5 — Actions with observable definitions of done

Every action must be checkable:

| # | Action | Owner | By | Definition of done | Recurrence check |
|---|---|---|---|---|---|
| 1 | Alert on `orders-api` 5xx > 1% for 5 min | | | Alert fires in the replayed scenario | Replay S1: alert fires < 5 min |
| 2 | Alert on Hikari `pending > 0` for 2 min | | | | Replay S2 |
| 3 | Pool sizing doc + CI check on pool size vs p99 | | | PR adding a sleep without pool change fails | |
| 4 | Runbook `RUNBOOK_CHECKOUT_FAILURES.md` with tested commands | | | Two responders follow it unaided in a game day | |
| 5 | Fail fast on missing required config | | | Starting without `STOCK_THRESHOLD` fails at boot | |
| 6 | Per-dependency latency SLO on the order path | | | Dashboard shows p99 per dependency | |

**Deliverable**: the action table plus a tracking mechanism (a real board, not a doc). Aim for > 70% completion in the exercise — anything less, and note that the process needs fixing too.

---

## Part 6 — Prove the actions worked (recurrence measurement)

Re-run the *same* injected scenario three times, measuring:

| Run | MTTD | MTTM | MTTR | Detected by | Detection source |
|---|---|---|---|---|---|
| Baseline (before actions) | | | | customer | ticket |
| After actions 1–2 | | | | | |
| After all actions | | | | | |

Then compute honestly:

```
rate_before = incidents_in_period_before / months_before
rate_after  = incidents_in_period_after  / months_after
reduction   = 1 − rate_after / rate_before
```

If you have zero post-action incidents, use the Poisson bound:

```
upper_bound_rate ≈ 3 / months_observed        (95% confidence)
→ "consistent with a rate up to X/month, not proof of elimination"
```

**Deliverable**: `RECURRENCE.md` with the table, the reduction, and the honest statement about what the evidence does and does not support.

---

## Part 7 — Alert quality audit

Inventory every alert in your lab (and, if you have access, one real service):

| Alert | Pages? | Caused an action? | Owner | Runbook? | Verdict |
|---|---|---|---|---|---|
| | | | | | keep / ticket / delete |

Compute:

```
actionable_fraction = pages_that_caused_an_action / total_pages
pages_per_shift
```

Then delete or downgrade the offenders and re-measure.

**Deliverable**: `ALERT_AUDIT.md` with the table, the metrics before/after, and the list of deleted alerts.

---

## Part 8 — Escalation ladder

Design the ladder with acknowledgement probabilities:

```
ack_rate_per_notification = 0.85 (measure yours)
P(acknowledged within t) = 1 − (1 − ack)^attempts(t)
```

| Elapsed | Channel | Action | Cumulative P(ack) |
|---|---|---|---|
| 0 | page | primary on-call | 85% |
| 5 min | page | repeat | 97.8% |
| 10 min | phone | secondary on-call (called, not paged) | 99.5% |
| 15 min | phone | engineering manager (called) | ~99.9% |

Justify the "call a human at 10 minutes" step with the arithmetic.

**Deliverable**: `ESCALATION.md` with the table, the numbers, and the ownership of each step.

---

## Part 9 — Game day (finding defects, not confirming health)

Design a game day whose stated goal is **to break the runbooks**.

Injections:

| Injection | Expected to reveal |
|---|---|
| Slow `inventory` to 3 s | Does the runbook have a saturation step? Does an alert fire? |
| Postgres failover | Is there a documented reconnect procedure? Does the pool recover? |
| Expired TLS certificate on `payments` → PSP | Is there a cert-expiry alert? Who owns renewal? |
| Revoke your own cluster-admin access | Can the on-call actually reach production? (This is the most valuable injection in the lab.) |
| Roll a bad release | Do you roll back? Can you? Does the schema permit it? |
| Fill the disk on `orders-api` | Is there a disk alert? Does the heap dump path fail? |

For each injection, record: detection time, whether the runbook worked, every point a human was blocked, and every undocumented gap.

**Deliverable**: `GAMEDAY.md` with the injection table, the gaps found, and each gap as a tracked action with an owner.

---

## Acceptance Criteria

- [ ] `TIMELINE.md`: complete, single-clock, includes hypotheses marked unverified and refuted hypotheses marked REFUTED, and every production change recorded with its command.
- [ ] All three roles explicitly assigned and visible in the channel; one change at a time honoured.
- [ ] Comms updates every 15 minutes including "no change" updates, with internal and external variants.
- [ ] `DECOMPOSITION.md`: MTTD/MTTA/MTTM/MTTR computed from the timeline, dominant phase identified, cheapest intervention stated.
- [ ] `POSTMORTEM.md`: blameless, contributing-factors table (not a single root cause), no "human error" as a cause, actions with owner/date/definition-of-done, recurrence check included.
- [ ] `RECURRENCE.md`: three re-runs measured, reduction computed, honest statistical statement about zero-observation claims.
- [ ] `ALERT_AUDIT.md`: actionable fraction and pages-per-shift computed before and after; offenders deleted or downgraded.
- [ ] `ESCALATION.md`: ladder with cumulative acknowledgement probabilities and a justified human-call step.
- [ ] `GAMEDAY.md`: at least five injections, with real gaps found and tracked as actions.

---

## Stretch

- Run a game day where the "responder" is someone who has never seen the system, and measure how much of the runbook is usable without tribal knowledge.
- Build a "timeline linter" that flags an incident doc missing a hypothesis, an owner, or a definition of done.
- Correlate your incident classes with your DORA metrics and produce a chart showing whether faster releases actually caused more incidents.
- Convert one incident class into an automated runbook (a script the responder runs rather than reads) and measure the reduction in MTTM.
