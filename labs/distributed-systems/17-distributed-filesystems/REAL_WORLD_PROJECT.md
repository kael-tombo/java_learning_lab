# Distributed File Systems - Real World Project

## Project: Object Storage Frontend with S3-Compatible Semantics

### Objective
Build the object-storage layer for an application: buckets, versioning, atomic publish,
erasure-coded durability, and lifecycle — with the failure behaviour documented and tested.

### Why This Is a Real Problem
Applications outgrow the disk long before they outgrow the API. What they need from object
storage is not raw throughput — it is the *semantics*: atomic publish, versioning that lets
you undo, immutability for the things that must not change, and a durability statement you can
defend in an audit.

### Architecture Overview
```
  App ─▶ API (bucket, key, version) ─▶ Metadata (consensus, strong)
          │                                 │
          │                                 ├─ versioning
          │                                 └─ atomic publish: commit pointer last
          ▼
       Block layer: erasure-coded, k=6 + m=3
          │
          ├─ Hot tier (SSD, recent objects)
          └─ Cold tier (cheaper, after 30 days)
```

### Phase 1: Define the Semantics First (Week 1)
1. Publish model: a key becomes visible **only** when all blocks are durable and the metadata
   commit succeeds. No partial visibility, ever
2. Versioning: every write creates a version; delete marks a tombstone rather than removing
3. Immutability: write-once keys (audit records, signed artefacts) reject any second write,
   enforced at the metadata layer
4. Consistency: strong read-after-write for the same key, since the commit is a consensus op
5. Write these five sentences down; they are the contract every code review should check

### Phase 2: Implement the Metadata Layer (Week 2)
1. Buckets as containers with policy (versioning state, lifecycle rules, encryption key ref)
2. Object metadata: key, version, size, content hash, etag, creation time, storage class
3. Atomic publish: write blocks, fsync-equivalent, then a single metadata commit
4. Conditional writes: `If-None-Match: *` to make creation idempotent under client retries
5. List operations: paginated, eventually consistent for the *listing* while reads of a
   specific key are strong — document that asymmetry, it surprises people

### Phase 3: Durability and Erasure Coding (Week 3)
1. k=6 data + m=3 parity blocks: 1.5x space, tolerates 3 node losses
2. Scrubbing job: periodically read every block and verify its hash, repairing from parity
3. Rebuild on failure: recompute missing blocks from surviving ones automatically
4. Verify no block is placed in the same failure domain as another copy of its stripe
5. Drill: kill 3 nodes holding one object's blocks and prove a read succeeds

**Be honest in the write-up:** erasure coding reduces read performance at low node counts.
That is why the hot tier exists, and the tiering policy is what pays for the space saving.

### Phase 4: Lifecycle and Tiers (Week 4)
1. Transition objects to cold storage after 30 days; keep a local cache for recent reads
2. Expiration rules for temporary objects — with a delayed-delete window so an accidental
   expiry is recoverable
3. Lifecycle must never delete the only copy; verify every rule against the erasure tolerance
4. Cost model per tier, reviewed against actual access patterns before enabling the switch

### Phase 5: Operate (Week 5+)
1. Metrics: PUT/GET latency percentiles, PUT failure rate, block repair jobs, scrub findings,
   cold-tier hit rate, orphaned blocks
2. Alerts: scrub failure (silent corruption), orphaned block growth, publish failure rate
3. Runbooks: "object unavailable" (checks scrub findings first), "publish failing",
   "rebuild needed"
4. Quarterly disaster drill: delete a random object's metadata and confirm reconstruction

### Deliverables
1. Semantics document (the five sentences) approved by the consuming teams
2. Metadata layer with versioning, immutability, conditional writes, and atomic publish
3. Erasure-coded block layer with scrubbing and automatic rebuild
4. Lifecycle and tiering with a cost model, plus dashboards and runbooks

### Success Criteria
- No partial object is ever visible, proven by a failure-injection test at every step
- Three-node loss of one object's blocks still serves a correct read
- Scrubbing detects and repairs injected corruption within one cycle
- Lifecycle rules never reduce durability below the erasure tolerance

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon S3 product documentation —
  https://aws.amazon.com/s3/
  Use for: the reference object-storage semantics — versioning, strong read-after-write
  consistency, and the documented consistency guarantee for LIST versus GET. Verify current
  consistency claims on the page before asserting them in your own contract; this guarantee
  has changed over time.
- Kubernetes Documentation, "Cluster Architecture" —
  https://kubernetes.io/docs/concepts/architecture/
  Use for: the etcd-backed metadata store model — consensus for the namespace, separate
  storage for data. That separation is exactly the architecture above, and the docs are
  explicit that etcd needs a backup plan.

### Estimated Time
7-8 weeks part-time