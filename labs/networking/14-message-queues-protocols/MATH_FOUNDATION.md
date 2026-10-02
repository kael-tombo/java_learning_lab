# MATH_FOUNDATION — Message Queues

## 1. Partition parallelism bounds

Topic with P partitions, C consumers in a group: effective parallelism
= min(P, C). Extra consumers idle; extra partitions cost fds/RAM/disk per
broker. Throughput ≈ P × single-partition rate (100K msg/s quoted) until
broker NIC/disk saturates — partitions parallelize, they don't create
bandwidth.

## 2. Queueing math (Little's law again)

Backlog L = λ·W (arrival rate × mean service time). Consumers behind ⇒ W
rises ⇒ L grows unboundedly. Adding consumers divides W across workers
(linear while partitions allow); batching (`max.poll.records`) amortizes
per-message fixed cost; async handlers cut W by overlapping I/O. If λ >
max service rate at full scale, no consumer count helps — throttle
producers or shed load.

## 3. Semantic cost ordering

Loss probability (at-most) vs duplicate rate (at-least) vs coordination
cost (exactly-once: 2PC/transaction markers + idempotent state). Expected
cost of duplicates = P(dup) × cost-of-double-apply — when double-apply is
catastrophic (payments), exactly-once pays for itself; when idempotent
(email digest), at-least-once + dedup table wins.
