# History - Data Pipelines

Only widely documented facts; uncertain details are omitted.

## Warehousing era

- Inmon's and Kimball's data-warehousing work (1990s) separated
  analytical stores from operational systems and gave ETL (extract,
  transform, load) its name and discipline: nightly batches into
  modeled marts.
- ELT (load first, transform in the warehouse) came later with cheap
  storage and powerful warehouses - same letters, reversed economics.

## Distributed processing

- MapReduce (Dean and Ghemawat, 2004/2008 paper) made commodity-cluster
  batch standard practice; Hadoop (mid-2000s, open source) spread it.
- Log-structured messaging (early 2010s systems, Kafka the widely known
  example) made durable event streams ordinary infrastructure - but this
  lab claims only its commonly documented at-least-once default posture,
  no versions or internals.

## Orchestration and contracts

- DAG schedulers (Airflow, 2014 open source, and peers) turned cron
  spaghetti into retryable, observable graphs.
- Schema registries with compatibility rules mechanized the
  additive-vs-breaking distinction this lab teaches as set relations.

## Lesson

Each era re-learned: key your records, validate before transforming,
keep sinks replay-safe, and version the contracts between teams.

## Reading the lineage

Inmon/Kimball (model the mart), MapReduce (scale the batch), streams
(freshen the flow), DAG schedulers (order the chaos), registries (rule
the contracts). Each layer kept the previous one's discipline - replay,
keys, validation - and added one new power with its new failure mode.

## What the pendulum teaches

Batch vs stream, ETL vs ELT: the pendulum swings with storage and
compute economics, but keys, contracts, and quarantine never swing out.
Build on the invariants; rent the fashion.
