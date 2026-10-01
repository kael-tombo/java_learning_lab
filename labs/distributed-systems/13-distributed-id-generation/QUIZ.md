# Quiz — Distributed ID Generation

10 questions. Answers with explanations at the end of each question.

## Q1 — Uniqueness scope
Which property is hardest to guarantee for IDs generated independently on partitioned nodes?
- a) Rough time-ordering
- b) Global uniqueness without coordination
- c) Fixed 64-bit length
- d) JSON serializability

**Answer: b).** Independent generators cannot consult each other during a partition, so collisions must be prevented structurally (namespace bits, node IDs, randomness with enough entropy). Length and encoding are local choices; ordering is best-effort.

## Q2 — CAP framing
Under CAP, a Snowflake-style generator (timestamp + worker-id + sequence, no cross-node coordination) is best described as:
- a) CP — refuses to generate during partitions
- b) CA — consistent and available with no partitions
- c) AP — available during partitions, uniqueness depends on correct worker-id assignment (a coordination/setup assumption)
- d) Not subject to CAP at all

**Answer: c).** Generation never blocks on remote nodes, so it stays available. Correctness (uniqueness) rests on the out-of-band invariant that worker IDs are unique — which itself required coordination at assignment time.

## Q3 — PACELC framing
PACELC asks: "if Partition, how do Availability and Consistency trade off; Else, how do Latency and Consistency trade off?" For a central DB-sequence (auto-increment via one primary), the ELSE-side tradeoff is:
- a) Every ID costs a remote round trip (latency) in exchange for strict ordering/uniqueness (consistency)
- b) No latency cost because sequences are free
- c) Partitions improve latency
- d) PACELC does not apply to sequences

**Answer: a).** Centralized coordination buys strong guarantees and charges per-ID latency plus a single-point-of-failure/throughput bottleneck.

## Q4 — Consistency model
Snowflake IDs are "roughly time-ordered" but two IDs from different workers can invert wall-clock order. Which consistency description fits?
- a) Linearizable total order
- b) Sequential consistency
- c) No global ordering guarantee — only per-worker monotonicity (plus best-effort timestamp ordering subject to clock skew)
- d) Causal consistency of IDs

**Answer: c).** There is no agreed total order across workers; each worker's own counter is monotonic, and timestamps order approximately, within clock-skew error.

## Q5 — Clock skew failure
A worker's clock jumps backward (NTP step) and it reuses a timestamp with a reset sequence. What breaks, and what is the standard defense?
- a) Nothing; sequences self-heal — no defense needed
- b) Duplicate IDs — defense: refuse to generate until clock catches up past last timestamp (wait it out), and/or persist last timestamp
- c) IDs get too long — defense: compress them
- d) Only latency suffers — defense: add retries

**Answer: b).** Time regression reopens an already-used (timestamp, sequence) space. The generator must stall until time advances, and should persist the high-water mark across restarts.

## Q6 — Tradeoff reasoning: UUIDv4 vs Snowflake
A team needs IDs that are (1) mergeable across regions with no coordination and (2) index-friendly in B-trees. Which analysis is correct?
- a) UUIDv4 satisfies both
- b) Snowflake satisfies both
- c) Neither satisfies both: UUIDv4 gives coordination-free uniqueness but random I/O fragments indexes; Snowflake is index-friendly but needs unique worker-id assignment (coordination). Pick by which cost hurts more, or use UUIDv7 / ULID as a middle ground.
- d) Use DB auto-increment; it satisfies both

**Answer: c).** This is the classic entropy-vs-orderability tradeoff. UUIDv7/ULID (time-ordered randomness) are the usual compromise: no worker registry, mostly monotonic.

## Q7 — Coordination cost math
With a Hi-Lo scheme (allocate a hi-block of size N from a coordinator, then mint N IDs locally), what is the coordinator load for M IDs?
- a) M remote calls
- b) M/N remote calls — batching amortizes coordination
- c) Zero calls ever
- d) M² calls

**Answer: b).** Larger blocks mean fewer allocations (less load, better availability during blips) but more IDs wasted if a node dies. Size N is a waste-vs-coordination tradeoff knob.

## Q8 — Failure injection preview
Node A and node B are accidentally configured with the same worker-id. Which detection scheme catches it fastest?
- a) Periodic collision audit of recent IDs across nodes
- b) Longer IDs
- c) Faster clocks
- d) Bigger sequence counters

**Answer: a).** Duplicate worker IDs are silent until duplicates appear downstream (PK violations). A background uniqueness auditor over recent windows, plus startup worker-id fencing (lease the worker-id in ZooKeeper/etcd), converts silent corruption into a loud alarm.

## Q9 — Ordering vs uniqueness
A payment ledger needs IDs that sort in creation order globally. Can Snowflake-style IDs satisfy this?
- a) Yes, exactly, because timestamps are exact
- b) Approximately only — clock skew and same-millisecond ties mean "sorted by ID" is not a linearizable creation order; ledgers needing exact order must sequence via a log (Kafka partition, consensus) instead
- c) Yes if sequence bits are widened
- d) No, IDs can never be ordered

**Answer: b).** Approximate order is fine for sharding/sorting UX; money ordering needs a single-writer log or consensus sequence.

## Q10 — Design judgment
Three AZs, partitions between AZs are expected, and ID generation must never block. Rank the options:
- a) DB auto-increment > Snowflake > UUIDv7
- b) UUIDv7/ULID > Snowflake (with fenced worker-ids) > central DB sequence
- c) Central DB sequence is always best
- d) All are equivalent under partition

**Answer: b).** Under must-never-block, coordination-free schemes (UUIDv7) rank first; Snowflake is second but depends on worker-id fencing done before the partition; a central sequencer blocks or needs failover, so it ranks last here.
