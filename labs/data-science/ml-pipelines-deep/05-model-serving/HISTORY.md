# Model Serving - History

## Shared background
- Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), systematized batch versus stream processing and log-based data integration used across these labs.
- Sculley, Holt, Golovin and colleagues, "Hidden Technical Debt in Machine Learning Systems" (NIPS 2015), documented how serving, glue code, pipelines, and monitoring dominate production ML cost.
- Breck and colleagues' ML Test Score rubric extended that line of work into scored production-readiness checks for data, models, and infrastructure.

## Serving specifics
- Leonard Richardson and Mike Amundsen, RESTful Web APIs (O'Reilly, 2013), codified resource and versioning patterns behind request/response serving interfaces.
- Shadow, canary, and blue-green rollout vocabulary comes from release-engineering practice for migrating traffic safely between versions.
- Batch scoring on schedules descends from data-warehouse ETL practice; online scoring follows web-service request/response conventions.
- Percentile-based latency objectives (p50/p99) come from service-level-objective practice in site-reliability engineering.
- Model registries and versioned artifacts generalize artifact-repository practice from software release management.

## Mechanism depth on the existing entries
- Kleppmann deepened: the batch/stream split decides serving shape —
  scheduled partition scans for throughput versus per-event stateful
  scoring for continuity — and the log-based integration behind both.
- Technical-debt deepened: serving glue (preprocessing parity, version
  plumbing, prediction logging) is the cost center the 2015 paper names;
  each serving file here maps to one debt it itemizes.
- RESTful-versioning deepened: resource and representation versioning is
  what lets request/response schemas evolve without coordinated
  downtime, which is why schemas carry explicit versions here.
- Rollout-vocabulary deepened: shadow/canary/blue-green are
  traffic-routing policies over pinned versions, so rollback stays a
  routing change rather than a rebuild under pressure.
- SRE-latency deepened: percentile objectives turn raw timings into
  contracts — p50 for the typical case, p99 for the tail that stalls
  users — which is why budgets here are written per version at peak.
- Batch-ETL deepened: scheduled partition scans with row-in/row-out
  validation are the warehouse habit behind the batch path; sharded
  scorers plus prediction sinks are that habit pointed at models.
- Registry deepened: artifact repositories version immutable builds and
  map releases to versions; model registries add the traffic-share map
  so shadow, canary, and blue-green become routing edits, not rebuilds.
- Warmup deepened: cold-start cost (page faults, JIT, cache fill) is the
  systems reason every deploy risks a p99 spike, and the reason
  readiness — not liveness — gates traffic.
