# QUIZ — Message Queues

## 1. Push vs pull: which side is smart in RabbitMQ vs Kafka?
<details><summary>Answer</summary>RabbitMQ: smart broker pushes, dumb consumer. Kafka: dumb broker stores, smart consumer pulls/fetches.</details>

## 2. Same key always lands where, and why does it matter?
<details><summary>Answer</summary>Same partition (`hash(key) % N`) — per-key ordering. Null key round-robins (spread, no order).</details>

## 3. 6 partitions, 10 consumers: idle count?
<details><summary>Answer</summary>4 idle — one consumer max per partition per group. Parallelism = min(P, C).</details>

## 4. DLQ purpose in one line?
<details><summary>Answer</summary>Quarantine unconsumable (poison) messages for autopsy instead of infinite redelivery blocking the queue.</details>

## 5. MQTT QoS 0/1/2 map to which semantics?
<details><summary>Answer</summary>At-most / at-least / exactly-once (4-step handshake) — same cost ladder as the general semantics.</details>

## 6. Kafka exactly-once ingredients?
<details><summary>Answer</summary>Idempotent producer + transactional API + consumer offset coordination. All three, or it isn't exactly-once.</details>

## 7. Backpressure: first metric, last resort?
<details><summary>Answer</summary>First: queue depth/lag. Last: producer throttling/shedding — after scaling, batching, async, repartitioning.</details>

## 8. Why check consumer count against partition count before scaling?
<details><summary>Answer</summary>Extra consumers idle past P — scaling consumers without partitions is theater. Repartition first.</details>

## 9. Edge pattern MQTT→gateway→Kafka: why the handoff?
<details><summary>Answer</summary>MQTT fits constrained devices (2-byte header); Kafka fits durable analytics. Gateway translates frugality into throughput.</details>

## 10. Rebalance triggers + assignor names?
<details><summary>Answer</summary>Consumer join/leave; EagerSticky (stop-the-world) vs CooperativeSticky (incremental).</details>
