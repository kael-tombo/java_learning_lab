# Flashcards — Distributed ID Generation

Self-test cards. Cover the prompt, recall, then check.

1. **Card: Snowflake bit layout (64-bit)** — Prompt: What are the three components of a Snowflake ID? / Answer: Timestamp (41b) + worker/machine ID (10b) + per-ms sequence (12b). ~69 years of ms, 1024 workers, 4096 IDs/ms/worker.
2. **Card: Why worker-ids threaten uniqueness** — Prompt: What is the single coordination assumption Snowflake depends on? / Answer: Worker IDs are unique. Duplicates cause duplicate IDs — silent corruption. Fence worker-ids via leases (etcd/ZK) at startup.
3. **Card: UUIDv4 vs v7** — Prompt: Contrast UUIDv4 and UUIDv7 in one line each. / Answer: v4 = 122 random bits, coordination-free but index-hostile; v7 = Unix-ms prefix + random, coordination-free AND roughly time-ordered (index-friendly).
4. **Card: ULID** — Prompt: What is a ULID? / Answer: 128-bit, Crockford-base32 encoded, 48-bit ms timestamp + 80-bit randomness. Lexicographically sortable, URL-safe, monotonic within a ms on one node.
5. **Card: CAP placement of central sequencer** — Prompt: DB-sequence ID generation under partition: CP or AP? / Answer: CP-leaning: correctness preserved, but generation blocks/fails over when the primary is unreachable.
6. **Card: PACELC Else-side for central sequencer** — Prompt: No partition — what does a central sequencer trade? / Answer: Latency (a remote RTT per ID or per block) for Consistency (strict uniqueness/order).
7. **Card: Hi-Lo / block allocation** — Prompt: How does Hi-Lo amortize coordination? / Answer: Coordinator hands out hi-blocks of size N; node mints N IDs locally. Coordinator load drops to M/N. Bigger N = fewer calls but more waste on crash.
8. **Card: Clock regression defense** — Prompt: Clock steps backward — what must the generator do? / Answer: Refuse to mint until wall clock passes the last used timestamp; persist the high-water mark to survive restarts.
9. **Card: Per-worker monotonicity** — Prompt: What ordering does Snowflake actually guarantee? / Answer: Only per-worker monotonicity (same worker, increasing ms/sequence). No global total order — cross-worker order is approximate within clock skew.
10. **Card: Duplicate worker-id detection** — Prompt: How do you detect two nodes sharing a worker-id? / Answer: Background audit of recent ID windows for duplicates + startup fencing (lease worker-id; refuse to start on conflict) + downstream PK-violation alerting.
11. **Card: B-tree fragmentation** — Prompt: Why do random UUIDs hurt B-tree indexes? / Answer: Random insert positions cause page splits and poor cache locality; write amplification rises. Time-ordered IDs append mostly at the right edge.
12. **Card: Sequence exhaustion in a ms** — Prompt: Snowflake worker exceeds 4096 IDs in one ms — options? / Answer: Spin-wait for next ms (adds tail latency) or widen sequence bits (shrinks timestamp/worker space). Bursty workloads need headroom.
13. **Card: ID size vs entropy** — Prompt: Why not just use 256-bit random IDs everywhere? / Answer: Collision odds vanish, but storage, index, log, and cache costs grow; many stores/debuggers assume 64–128-bit IDs. Size is a systems cost.
14. **Card: Ledger ordering** — Prompt: Can ID sort order replace a ledger's creation order? / Answer: No. Approximate order ≠ linearizable order. Money-grade ordering needs a single-writer log or consensus sequence; IDs are for identity, logs are for order.
15. **Card: Worker-id assignment strategies** — Prompt: Name three ways to assign worker IDs. / Answer: Static config (simple, error-prone), coordinator lease at startup (safe, needs coordinator), derived from IP/Pod ordinal (convenient in K8s StatefulSets, must bound to 10 bits).
16. **Card: Restart hazard** — Prompt: Why must the last timestamp survive restarts? / Answer: A restarted node with a stale clock would re-mint already-issued (timestamp, sequence) pairs. Persist the watermark and stall on regression.
