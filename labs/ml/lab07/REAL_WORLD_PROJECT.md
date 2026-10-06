# REAL_WORLD_PROJECT — Retail Customer Segmentation Service

**Track:** ml  |  **Lab:** lab07  |  **Level:** Intermediate

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

A 2.4M-customer retailer needs segments that marketing campaigns actually use, refreshed weekly, stable enough that a campaign measured over six weeks still refers to the same population. You own the segmentation and the drift alarm.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Population | 2.4M active customers, 900k with a purchase in the last 90 days |
| Refresh cadence | weekly full re-segmentation; daily incremental scoring |
| Consumers | 6 campaign tools, CRM, warehouse audiences, finance reporting |
| Serving SLO | p99 lookup < 60 ms; weekly job done before Monday 06:00 |
| Contract | Segments must be reconcilable month over month for campaign ROI |

## 3. Target Architecture

```text
 CRM + orders + web events --> warehouse (daily)
                                        |
                             weekly feature build (RFM + category mix)
                                        |
                    +-------------------+-------------------+
                    |                                       |
          full re-segmentation (k-means,          stability check (ARI vs
          10 restarts, k chosen + versioned)      last week's labels)
                    |                                       |
                    +-------------------+-------------------+
                                        |
                              segment registry (versioned)
                                        |
              +-------------------+------+------+-------------------+
              |                       |                     |
         campaign tools            CRM UI               warehouse audiences
      (segment + size in payload)  (daily lookup)        (Parquet export)

   Monitoring: population drift per segment, PSI on features, job freshness
```

## 4. Component Responsibilities

### 4.1 Feature build

- RFM features plus category-mix entropy, all computed from a frozen window definition
- Features standardised with statistics stored alongside the version, not recomputed downstream
- Zero-activity customers handled explicitly rather than by imputation guesswork
- Feature snapshot ID attached to every assignment so it is replayable

### 4.2 Segmentation and registry

- k-means with 10 restarts; k chosen once and versioned with a written justification
- Stability gate: adjusted Rand index against last week's labels above a threshold, else investigate
- Segment ID and description in a registry, with the run that produced it
- Non-parametric labels for stability (0 = most stable week in the last 12)

### 4.3 Serving and consumption

- Lookup service serving customer to segment with the version, p99 under 60 ms
- Campaign tools receive segment plus size so a stale audience is visible at send time
- Warehouse Parquet export for analysts, partitioned by snapshot date
- No consumer may join on a segment ID without the version

### 4.4 Drift and operations

- Weekly population share per segment; alert on a shift beyond 5 points
- PSI on the RFM features to catch upstream data problems
- Job freshness SLO with a fallback to the previous week's segmentation
- Reconciliation report so finance can tie campaign ROI to segment version

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship descriptive stats and a fixed-size quartile baseline so every later claim has a reference |
| Week 2 | Feature build with frozen window definitions and snapshot versioning |
| Week 3 | Weekly segmentation job with the stability gate; run three weeks before trusting it |
| Week 4 | Registry, lookup service, Parquet export; migrate one campaign tool |
| Week 5 | All campaign tools migrated; drift alerts live; rollback drill documented and timed |

## 6. Runbook (copy-paste)

```bash
# Which segmentation is live, and how fresh is it?
curl -s localhost:8080/admin/segmentation | jq '{version,builtAt,rows,freshnessHours}'

# Population share per segment vs last week
curl -s 'localhost:8080/admin/populations?window=2w' | jq '.segments,.delta'

# Feature PSI since the last snapshot
curl -s 'localhost:8080/admin/drift?feature=recency' | jq '.psi,.threshold'

# Roll back to the previous week's segmentation
curl -XPOST localhost:8080/admin/segmentation/rollback -d '{"to":"seg-2026-09-21"}'

# Reconcile one campaign's audience size against the registry
curl -s 'localhost:8080/admin/audience?campaignId=c-8842' | jq '.segment,.size,.version'
```

## 7. Observability and SLOs

- SLO: weekly job completes before Monday 06:00; lookup p99 < 60 ms; availability 99.9%.
- Stability: adjusted Rand index against the previous week, monitored as a distribution not a single value.
- Business: campaign lift and ROI per segment, reported with the segment version attached.
- Drift: population share shift per segment; feature PSI with an alert threshold of 0.2.
- Consumption: number of consumers still joining without a version (target zero).

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Weekly job misses the Monday deadline | Feature build slowed by an upstream schema change | Serve the previous week's segmentation with a stale banner; page the data owner |
| Segment population share shifts by 20% | A large acquisition campaign or a returns-driven feature change | Investigate feature PSI before re-clustering; do not silently re-cut k |
| Stability gate fails two weeks running | Data quality change rather than real drift | Freeze the segmentation version, escalate to data engineering, keep serving the last good one |
| Campaign audience size disagrees with the registry | A consumer joined without the version column | Block the export without a version; this is a contract failure, not a dashboard bug |
| Lookup p99 breaches 60 ms | Cache miss storm after a snapshot swap | Pre-warm the cache before publishing the new version |

## 9. Prevention Backlog

- Automated stability report including per-segment member overlap with the prior week.
- Cluster-in-cluster monitoring so a segment that fragments is detected before campaigns notice.
- Incremental daily assignment instead of full weekly re-segmentation.
- Timed rollback drill each quarter with the result published to the marketing team.

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

> The deliverable is a segmentation that means the same population for six weeks, is versioned, is reconciled by finance, and pages you before a campaign notices.
