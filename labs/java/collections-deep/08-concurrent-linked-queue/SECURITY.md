# Security: ConcurrentLinkedQueue

## Unbounded growth as DoS

CLQ never rejects: any thread holding a reference can offer indefinitely
until heap exhausts. A malicious/buggy producer = OOM with no backpressure
signal. Mitigations: bound at the application layer (semaphore/ counter +
reject), monitor quiescent depth, isolate producer reachability.

## Null-sentinel confusion

Code that treats "poll returned null" as "empty, stop draining" while a
producer is mid-offer can exit early and strand work — a liveness bug an
attacker with timing control could widen into starvation. Drain loops must
tolerate transient nulls (retry/park, then re-poll) rather than treating
one null as terminal.

## Stale-size control flow

Branching admission control on `size()` (`if (q.size() < N) accept`) races:
the value is stale, so limits over-admit under burst. Enforce limits with
atomics incremented at offer-linearization, not with `size()`.

## Weak-iterator leakage

Iterators expose elements in chain order including concurrently-added
items from other tenants. If the queue multiplexes tenants, a tenant-held
iterator can observe another tenant's elements — partition queues per
trust domain instead of sharing.

## No fairness / starvation

Lock-freedom promises system progress, not per-thread fairness. A loud
producer can keep winning the tail CAS while a quiet one's offers retry —
priority inversion under adversarial load. Rate-limit producers
independently of the queue.
