# Distributed Messaging - Mini Project

## Project: A Single-Node Broker with Consumer Groups

### Objective
Implement enough of a partitioned log broker for one or more consumer groups to read from it
safely, then crash the consumers and prove no message is lost or skipped.

### Requirements
1. `MessageBroker` — append-only log per partition, durable before ack
2. `Partitioning` — hash(key) to partition, with an explicit partition count
3. `ConsumerGroup` — one active consumer per partition, rebalance on join/leave
4. `OffsetStore` — commit offset only after processing succeeds
5. `PubSubSystem` fan-out where *every* subscriber gets every message (no groups)

### Steps

**Step 1: The log is the whole design**
```java
final class PartitionLog {
    private final List<Record> records = new ArrayList<>();
    private long baseOffset;                       // compaction floor

    synchronized long append(Record r) {
        long offset = baseOffset + records.size();
        records.add(r);
        persist(r, offset);                       // durable BEFORE returning to client
        return offset;
    }
    synchronized List<Record> fetch(long from, int max) {
        if (from < baseOffset) throw new OffsetOutOfRange(from);  // must trigger re-seek
        return records.subList((int) (from - baseOffset), Math.min(records.size(), (int)(from - baseOffset) + max));
    }
}
```
Two invariants: append is durable before ack, and an offset below the compaction floor is a
loud error rather than a silent skip.

**Step 2: Partitioning and why the count is a decision**
```java
int partitionFor(String key) {
    return Math.floorMod(key.hashCode(), partitionCount);
}
```
Same key → same partition → ordering preserved for that key only. Choose `partitionCount` as
`ceil(throughput / per-partition-capacity)` and never below your consumer concurrency.

**Step 3: Consumer group rebalancing**
```java
void onJoin(String memberId) {
    members.put(memberId, Set.of());                 // no assignment yet
    rebalance();
}
void rebalance() {
    var ids = new ArrayList<>(members.keySet()); Collections.sort(ids);
    var ps = IntStream.range(0, partitionCount).boxed().toList();
    for (int i = 0; i < ids.size(); i++)            // simple range assignment
        members.put(ids.get(i), new HashSet<>(ps.subList(i * partitionCount / ids.size(),
                                                          (i + 1) * partitionCount / ids.size())));
}
```
On rebalance, revoke owned partitions and stop at the last **committed** offset — not the
last fetched one, or you will process past what you committed after a crash.

**Step 4: The crash test**
```java
@Test
void crashBetweenProcessAndCommitDoesNotSkip() {
    broker.append("orders", List.of(m("a"), m("b"), m("c")));
    consumer.processThenThrowOn("b");       // processes b, dies before commit
    consumerGroup.restartAll();
    // last committed offset was for "a", so "b" is redelivered — not skipped
    assertThat(processedKeys()).containsExactly("a", "b", "c");
}
```
Redelivery, not loss. That is at-least-once, and it is the behaviour you must build for.

**Step 5: Fan-out vs groups**
`PubSubSystem.send(topic, msg)` delivers to every subscriber cursor. `ConsumerGroup` delivers
to one member per group. Show both running against one broker: three groups each get every
message; adding a second member to a group halves its throughput per member.

**Step 6: Measure lag**
```java
long lag(String topic, String group) {
    return logEndOffset(topic) - committedOffset(group);
}
```
Expose lag per partition. A uniformly high lag means the consumer is slow; lag on exactly one
partition means a hot key — that diagnosis is the whole skill.

### Deliverables
1. `MessageBroker`, `PartitionLog`, `ConsumerGroup`, `OffsetStore`, `PubSubSystem`
2. Crash test proving no skip and a duplicate test proving at-least-once
3. Rebalance test: add a member mid-stream and confirm no partition is processed twice
4. A lag-per-partition printer and a one-paragraph diagnosis for each of three lag shapes

### Extension (CHALLENGE)
Implement a hot-key detector: track per-key rates per partition and recommend a partition
count increase plus a key-suffix strategy when one key dominates.

### Estimated Time
4-5 hours