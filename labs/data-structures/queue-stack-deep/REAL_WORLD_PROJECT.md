# Worker Pool and Gateway: Queues and Stacks at Depth

Two services, one discipline. A worker pool drains a bounded priority
queue with an overflow policy; an API gateway meters requests through a
FIFO with rate limits; a stack-based validator screens payload syntax.
Depth here means the failure behavior is specified before the code.

Pool lane. Priority queue (heap) with 4 workers, capacity 50k jobs,
drop-oldest policy behind a flag (alternatives: block, drop-newest).
Flood drill at 5x submit rate reconciles submitted = done + dropped +
held, with per-priority completion counts proving starvation freedom.

Gateway lane. FIFO with token-bucket admission; over-limit requests get
429-style refusals counted separately from queue drops. Burst script
(10x for 30 s) must show refusal counts matching the bucket math.

Validator lane. Bracket/expression screen over payloads with mismatch
offsets; invalid jobs quarantine with the offset attached. Fuzzed with
10k generated expressions against a recursive oracle.

Depth probes. Worker death mid-batch (lease redelivery), gateway burst
plus pool flood simultaneously (isolation: gateway SLO holds), snapshot
reload of pending jobs (order preserved), stack depth attack (10k
nesting rejected at the ceiling).

Pack. Both services, drill logs, reconciliation sheets, isolation note.
Bar: reconciliation exactness 12, policy behavior under flood 10,
isolation plus validator parity 8.
## Depth extras
- Flood reconciliation sheet kept.
- Bucket math verified.
- Validator oracle log green.
- Lease redelivery tested.
- Isolation drill quarterly.
- Snapshot order proven.
- Policy flag documented.
- Starvation counts posted.
