# MLOps Orchestration - History

## Shared background
- Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), systematized batch versus stream processing and log-based data integration used across these labs.
- Sculley, Holt, Golovin and colleagues, "Hidden Technical Debt in Machine Learning Systems" (NIPS 2015), documented how serving, glue code, pipelines, and monitoring dominate production ML cost.
- Breck and colleagues' ML Test Score rubric extended that line of work into scored production-readiness checks for data, models, and infrastructure.

## Orchestration specifics
- DAG schedulers for data work predate ML orchestration; retries, backfill, and lineage entered ML pipelines from that tradition.
- Cron-style scheduling descends from Unix periodic execution; event-driven triggers follow message-queue and log-based integration patterns.
- Exponential backoff with jitter is long-standing networked-systems practice for retrying without synchronizing load.
- Continuous-integration practice (automated checks before merge) is the ancestor of CI-for-ML gates before training and promotion.
- Locked dependencies and recorded environments generalize reproducible-build practice from software engineering.
- DAG-scheduler deepened: topological ordering turns dependency edges into
  run order, and branch parallelism falls out of the same structure —
  independent nodes simply have no edge between them. The acyclicity
  rule is what guarantees the ordering exists at all.
- Cron deepened: fixed-cadence ticks bound staleness by period plus run
  duration, which suits steady retraining; the failure mode is racing
  late data, and arrival-gated event triggers are the correction that
  message-queue practice supplied.
- Backoff deepened: doubling waits spread load while the cap bounds the
  worst stall, and jitter breaks the synchronization that simultaneous
  retries would otherwise recreate after a shared outage. Uncapped
  synchronized retry is how a dependency outage becomes a second outage.
- CI-gates deepened: pre-merge checks that block bad code became
  pre-training checks (schema, ranges, nulls) and pre-promotion checks
  (overall lift plus per-slice bars), each stopping the run while the
  current production model keeps serving untouched.
- Reproducible-build deepened: lockfiles plus recorded commits and seeds
  turn reruns into equality checks — the fingerprint 1047179432 is that
  habit executed — so divergence points at an unpinned input instead of
  a mystery.
- Queue-separation deepened: distinct lanes for scheduled, event, and
  backfill runs stop replays from starving cadence work; the shared-queue
  failure is scheduled waits growing exactly while history is repaired.
- Promotion-record deepened: naming who, when, and which lineage pointer
  shipped turns deployment into an auditable act with a revert address,
  generalizing release tagging from software to model artifacts.
