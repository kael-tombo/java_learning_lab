# MINI PROJECT — Virtual Threads: 10k-Connection Gateway

## Goal (2 weeks, ~8–10h)
Migrate a thread-pool gateway to virtual threads, prove 10k concurrent I/O, find and fix pinning, and adopt structured scopes for fan-out.

## Requirements
### Functional
1. Fake upstream (latency 50–200ms seeded): gateway fans out to 3 upstreams per request, merges with `StructuredTaskScope.ShutdownOnFailure` + 2s deadline.
2. Before/after: fixed-pool (200) version vs `Executors.newVirtualThreadPerTaskExecutor()` version behind a flag.
3. Lock audit: one path deliberately uses `synchronized`; replace with `ReentrantLock` after JFR pinning evidence.
4. `ScopedValue` (or ThreadLocal with justification) for request-id propagation across virtual threads.
5. CLI/loadgen: N concurrent clients, report throughput, p50/p95/p99, timeout count.
### Non-functional
- No pooling of virtual threads; no `ThreadLocal` megabyte caches; carrier count logged (`jdk.management` / JFR).
- 14+ tests: merge correctness, deadline-cancel path, scope-failure propagation, lock-swap equivalence, id propagation.
- README: platform-vs-virtual table (threads, memory, p99) + pinning screenshot/note.
- Soak: 10k concurrent fake-I/O without OOM on default heap.

## Phases
### Week 1 — Migrate + Measure (4–5h)
- Both executors, fan-out merge, loadgen harness.
- Deliverable: 1k-concurrency comparison table.
### Week 2 — Pin + Structure (4–5h)
- JFR pinning hunt, ReentrantLock swap, scoped values, 10k soak.
- Deliverable: pinning fix evidence + final verdict memo.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Migration | Flag-switched, clean close | Works | Pool-kept |
| Structured scope | Deadline+cancel correct | Used | Raw futures |
| Pinning fix | JFR before/after | Fixed unmeasured | Still synchronized-hot |
| Context prop | ScopedValue correct | ThreadLocal justified | Lost ids |
| Tests + soak | 14+ tests, 10k soak | 10+ tests | No load evidence |

Pass ≥ 70. Stretch: carrier-size tuning (`jdk.virtualThreadScheduler`); chaos (slow upstream) + hedged request.
