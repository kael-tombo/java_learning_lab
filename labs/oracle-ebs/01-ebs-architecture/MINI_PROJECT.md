# Lab 01: EBS Architecture — Mini Project

## Goal
Diagnose and remediate month-end concurrent request backlog on a 2,000-user EBS
instance in 90 minutes.

## Requirements
- R1: A baseline query set — app tier CPU, CM queue depth, avg wait time.
- R2: A query locating `JTF_QUEUE_LOCK` contention in the wait history.
- R3: A diagnosis document naming the constraint and the evidence for it.
- R4: A Concurrent Manager configuration audit showing single-queue operation.
- R5: A 3-node cloning plan with service assignment per node.
- R6: `FND_CONCURRENT_QUEUE_PUB` calls creating three specialised managers.
- R7: Work shift configuration throttling non-critical work at month-end.
- R8: A before/after load test comparison table with measured deltas.

## Steps
1. Capture the baseline: queue depth, avg wait, and app tier CPU.
2. Read `FND_CONCURRENT_REQUESTS` to see how requests are distributed.
3. Query the wait events for `JTF_QUEUE_LOCK` and record the count.
4. Write the diagnosis: constraint, evidence, and mechanism.
5. Design the 3-node layout and which services run where.
6. Create the specialised queues with explicit target nodes.
7. Define work shifts covering the month-end peak window.
8. Run the load test and compare against the baseline.
9. Write the before/after table with real measured numbers.

## Acceptance criteria
- The diagnosis cites at least two independent metrics, not one.
- The `JTF_QUEUE_LOCK` query returns rows and you explain what they mean.
- The before/after table shows a measured reduction in avg wait time.
- The plan is safe to roll back by disabling, not deleting, the queues.

## Stretch
- Model what happens if you only add a node without specialising the managers.
- Propose a monitoring query that would have caught this a week earlier.