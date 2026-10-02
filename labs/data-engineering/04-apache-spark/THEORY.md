# Apache Spark Theory

## Architecture
- **Driver**: Main program, creates SparkContext
- **Cluster Manager**: YARN, K8s, Standalone
- **Executors**: Worker processes
- **Tasks**: Units of work

## Core Abstractions
- **RDD**: Immutable partitioned collection
- **DataFrame**: RDD + Schema, optimized via Catalyst
- **Dataset**: Type-safe DataFrame

## Execution Model
DAG Scheduler -> Task Scheduler -> Executors

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Tuning Spark — Apache Spark 4.2.0 Documentation (Spark 4.2.0 released 2026-07-14; verified Oct 2026) — https://spark.apache.org/docs/latest/tuning.html#data-serialization — Takeaway for the RDD/DataFrame section: prefer Kryo serialization over Java serialization (up to ~10x smaller/faster) and register custom classes, since serialization cost dominates shuffle and cached-partition traffic in the DAG execution model.
- Tuning Spark — Apache Spark 4.2.0 Documentation (Spark 4.2.0 released 2026-07-14; verified Oct 2026) — https://spark.apache.org/docs/latest/tuning.html#memory-management-overview — Takeaway for the driver/executor architecture: execution and storage share one unified region (M) with an eviction-safe storage subregion (R); apps without caching get the full region for execution, so leave `spark.memory.fraction`/`storageFraction` at defaults unless GC stats justify change.
- Tuning Spark — Apache Spark 4.2.0 Documentation (Spark 4.2.0 released 2026-07-14; verified Oct 2026) — https://spark.apache.org/docs/latest/tuning.html#other-considerations — Takeaway for tasks and the cluster manager section (YARN/K8s/Standalone): target 2–3 tasks per CPU core, raise parallelism when reduce/shuffle working sets OOM, and respect data locality (PROCESS_LOCAL > NODE_LOCAL > RACK_LOCAL) via `spark.locality` waits.
