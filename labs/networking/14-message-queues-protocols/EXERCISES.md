# EXERCISES — Message Queues

## 1. Pattern match (beginner)
For each: stock-price broadcast, image-resize farm, payment auth with
reply, poison-message handling — choose pub/sub, work queue,
request/reply, or DLQ and justify in one line each. *Check against Q3.*

## 2. Partition math (beginner)
Topic: 6 partitions, 10 consumers in a group. How many idle? What changes
at 3 partitions / 3 consumers / keyed vs null-key producers? Draw the
assignment.

## 3. Semantic choice (intermediate)
Assign at-most/at-least/exactly-once to: temperature telemetry, order
fulfillment tasks, ledger transfers. For the middle case, design the
dedup table (key, TTL, exactly where in the handler it checks).

## 4. Lag drill (intermediate)
Given `kafka-consumer-groups` lag growing 5k/min on 2 of 12 partitions:
diagnose (skewed keys? slow consumer? rebalance storm?) in order, then
prescribe: scale, batch knobs, async, repartition — with the constraint
that two consumers share a DB connection pool of 10.

## 5. 500K fraud sketch (advanced)
Size the Q7 pipeline on paper: partitions, brokers, RF, Flink windows,
RocksDB state, Redis alert path, exactly-once boundary. Then halve the
budget (5 brokers) and show what degrades first, with numbers.
