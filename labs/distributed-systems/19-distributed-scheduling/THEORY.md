# Theory of Distributed Scheduling

## 1. Why Distributed Scheduling?

Single-node schedulers (cron, Windows Task Scheduler) fail when the node goes down. Distributed scheduling provides:
- High availability (failover to another node)
- Load distribution (multiple nodes share work)
- Exactly-once execution (no duplicate or missed jobs)
- Scalability (more nodes = more jobs)

## 2. Scheduling Models

### Leader Election Model
- One node executes the job, others standby
- Simplest model, single point of execution
- Leader elected via consensus (ZK, Etcd, DB)

### Partitioned Model
- Each node responsible for a subset of jobs
- Jobs distributed by hash or range partitioning
- No single point of failure

### Shared-Nothing Model
- All nodes eligible to run any job
- Job acquired via distributed lock
- Most flexible, highest overhead

## 3. Quartz Scheduler

Quartz is a Java scheduling library with clustering support:
- JDBC JobStore for persistent job storage
- Clustering via database locks (pessimistic)
- Job triggers: cron, simple, calendar-based
- Misfire handling for late execution

## 4. Distributed Cron

Traditional cron has no distributed semantics. Distributed cron adds:
- Leader election for single execution
- Cron expression synchronization
- Missed execution recovery
- Cross-timezone scheduling

## 5. Job Execution Guarantees

- **At-most-once**: Job may be skipped, never duplicated
- **At-least-once**: Job always runs, may run multiple times
- **Exactly-once**: Job runs exactly one time (hardest)

## 6. Misfire Handling

When a scheduled job doesn't run on time:
- **Fire now**: Execute immediately (catch up)
- **Ignore**: Skip missed execution
- **Next with count**: Execute next time with missed count
