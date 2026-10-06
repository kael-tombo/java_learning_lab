# REAL_WORLD_PROJECT — Data Contracts Across a Shared Lakehouse

**Track:** mlops  |  **Lab:** lab09  |  **Level:** Intermediate

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

A data platform serves 60 models from one lakehouse with 40 upstream producers and no contracts. A producer changed a column from cents to dollars; four models trained on prices 100x too low for six weeks before anyone noticed the scores looked odd.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Producers | 40 upstream tables owned by 11 teams |
| Consumers | 60 models plus analysts reading the same tables |
| Current state | no contracts; failures detected by model degradation |
| Worst recent incident | unit change went undetected for 6 weeks |
| Goal | breakages fail at the producer boundary within minutes |

## 3. Target Architecture

```text
 producers (40 tables / 11 teams)
      |
  contract registry (schema, ranges, semantics, freshness, owners)
      |
  validation executed at the producer boundary (pushdown)
      |
  +---------+ (pass) ------------+---------- (fail) ------------+
  |                              |                             |
 offline (validated snapshot)  feature materialisation   producer blocked, consumer paged
  |                              |
 training (point-in-time)    online serving
  |
 validation results attached to snapshot + model version
  |
 quality trends per table, per consumer
```

## 4. Component Responsibilities

### 4.1 Contract registry

- Per-table contracts: schema, types, nullability, primary keys, ranges, categories, freshness
- Semantic definitions stored with the table so units are unambiguous
- Named owner team per table, and a change process with a notice period
- Consumer inventory per table so a breaking change can be scoped before it lands

### 4.2 Enforcement at the boundary

- Contracts validated in the producer's pipeline before the table is published
- Pushdown execution so full validation is affordable on wide tables
- Blocking failures stop publication and page the producer, not the consumers
- Warning-level expectations recorded as trends for the producer team

### 4.3 Consumer protection

- Consumers validate again at their boundary as defence in depth
- Validation metadata attached to each snapshot and to model versions
- Feature store (Lab 04) materialises only from validated snapshots
- Unit and range metadata exposed so a consumer can assert on units

### 4.4 Quality operations

- Per-table quality trends with slope alerts and owners
- Contract coverage report showing which tables lack contracts
- Breaking change review requiring consumer sign-off for high-blast-radius tables
- Post-incident review adding a contract for every missed failure mode

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Inventory 40 tables; identify the 20 with the highest consumer count |
| Week 3-4 | Write contracts for those 20 with producer sign-off; enforce at the boundary |
| Week 5 | Pushdown validation engine with full-table execution and measured cost |
| Week 6-7 | Extend contracts to the remaining 20 tables; attach validation metadata to snapshots |
| Week 9 | Consumer sign-off workflow for breaking changes; first drill of a unit-change scenario |

## 6. Runbook (copy-paste)

```bash
# Contract status per table
curl -s localhost:8080/contracts | jq '.[] | {table,owner,contractVersion,coverage}'

# Validation result for the latest published snapshot
curl -s 'localhost:8080/validation?table=orders&latest=1' | jq '.blocking,.warnings,.score'

# Quality trend for a table with slope
curl -s 'localhost:8080/quality/trend?table=orders&window=30d' | jq '.score,.slope'

# Blast radius of a proposed breaking change
curl -s 'localhost:8080/contracts/blast-radius?table=orders&change=price_units' | jq '.consumers'

# Publish an exception for a known-bad row (time-boxed, logged)
curl -XPOST localhost:8080/validation/exception -d '{"table":"orders","reason":"backfill","expiresIn":"2h"}'
```

## 7. Observability and SLOs

- Coverage: percentage of tables with enforced contracts (target 100% for the top 20 first).
- Detection: time from a producer change to a blocking failure (target under 15 minutes).
- Blast radius: consumers identified before a breaking change lands (target 100%).
- Exceptions: number of time-boxed overrides, all expiring and reviewed.
- Outcome: production incidents caused by data breakage, trending to zero.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A producer pushes a unit change outside the contract | Table was not covered | Blocking failure at publication; page the producer; scope consumers from the inventory |
| An exception becomes permanent | No expiry on overrides | Overrides carry a mandatory expiry; expired exceptions block publication and are reviewed monthly |
| Validation cost becomes the bottleneck | Row-by-row checks in the JVM | Push predicates into the query engine; measure and optimise the slowest checks |
| Contracts drift from reality as tables evolve | No change process | Breaking change review with consumer sign-off and a notice period |
| Consumers still read unvalidated tables directly | No enforcement on the consumer side | Deprecate direct access; route consumers through validated snapshots |

## 9. Prevention Backlog

- Semantic layer so units and definitions are queryable rather than documented.
- Contract coverage automation discovering new tables and alerting on gaps.
- Cross-table referential integrity checks with an owner per relationship.
- Consumer-side validation as defence in depth with drift-aware thresholds.
- Quarterly drill of a unit-change scenario with measured detection time.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **MLflow — Tracking and Model Registry documentation**: https://mlflow.org/docs/latest/ml/tracking/
  Reference model for experiment/run/metric lineage and the registry lifecycle (the vocabulary this lab re-implements in Java).
- **Kubernetes — ConfigMaps and Secrets**: https://kubernetes.io/docs/concepts/configuration/configmap/
  How configuration is injected into scheduled workloads — the practical lineage story for a DAG run that must be reproducible months later.
- **DVC — data and model versioning**: https://dvc.org/doc/user-guide
  Content-addressed versioning of datasets and model binaries; the standard way to make a data snapshot referenceable in a run record.

> The deliverable is 40 producers whose breakages fail at their own boundary in minutes, with the blast radius known before a change lands and no unit change reaching a model for six weeks.
