# Replication Strategies - Mini Project

## Project: Leader/Follower Replication with a Split-Brain Test

### Objective
Implement single-leader replication in synchronous and asynchronous modes, then partition the
cluster and see exactly what each mode promises when the leader dies.

### Requirements
1. `LeaderFollowerReplication` with configurable `SyncMode` (SYNC, ASYNC, QUORUM)
2. `Replica` with applied-offset tracking so lag is observable
3. Quorum read/write path over N replicas
4. `SplitBrainSimulator` that isolates the old leader
5. JUnit tests asserting durability promises per mode

### Steps

**Step 1: Replication and the durability dial**
```java
enum SyncMode { SYNC, ASYNC, QUORUM }

Ack append(LogEntry e) {
    var followers = members.stream().filter(m -> m != leader).toList();
    switch (mode) {
        case ASYNC -> {
            followers.forEach(f -> f.enqueue(e));         // ack now, promise nothing
            log.append(e); apply(e);
            return Ack.DURABLE_LOCALLY_ONLY;
        }
        case SYNC -> {
            if (!allSucceed(followers, e)) { return Ack.REFUSED; }
            log.append(e); apply(e);
            return Ack.DURABLE_ON_MAJORITY_OR_MORE;       // stronger: all followers
        }
        case QUORUM -> {
            if (!majorityAcks(followers, e)) return Ack.REFUSED;
            log.append(e); apply(e);
            return Ack.DURABLE_ON_QUORUM;
        }
    }
}
```
Record for each mode what an ack actually means. This table is the deliverable:

| Mode | Ack means | Data lost if follower promoted with lag L |
|---|---|---|
| ASYNC | on the leader only | up to L entries |
| SYNC | on every follower | nothing |
| QUORUM | on a majority | possible: entries acked by a minority partition |

**Step 2: Measure the cost**
Run 10k appends in each mode and record throughput and p99 latency. SYNC will be several
times slower — that is the price of never losing an acknowledged write.

**Step 3: Split brain**
```java
@Test
void partitionedOldLeaderAcceptsWritesThatWillBeLost() {
    network.partition(leader, followers);
    assertThat(leader.append(entry("post-partition")).isAcked());   // ASYNC: yes!
    network.heal();
    var winner = electNewestLeader();                     // higher term wins
    winner.log().entries().doesNotContain(entry("post-partition"));
}
```
The old leader acked a write that no longer exists. This is why real systems fence the old
leader with a monotonically increasing term and reject anything stale.

**Step 4: Quorum reads and writes**
```java
Versioned read(String key) {
    var responses = replicas.stream().map(r -> r.read(key)).toList();
    return mostRecent(responses);      // read repair: push the winner back
}
void write(String key, String value, long version) {
    long acks = replicas.stream().filter(r -> r.write(key, value, version)).count();
    if (acks + 1 > replicas.size()) leader.advance(version);
}
```
Partition 5 replicas into 2 and 3. The 3-side accepts writes (3 + 1 > 5). The 2-side must
reject. Assert exactly that.

**Step 5: Read repair**
Record a version-vector per key. After a quorum read, write the winning version back to
lagging replicas and assert lag drops. This is how gossip-free clusters converge reads.

### Deliverables
1. `LeaderFollowerReplication` in all three modes + `Replica` with lag tracking
2. Split-brain test proving the lost-ack, plus a fencing check that would reject it
3. Quorum test asserting the minority side rejects writes
4. Throughput/latency table for the three modes and a durability-promise statement each

### Extension (CHALLENGE)
Implement multi-leader with last-writer-wins on a Lamport clock, then show the two leaders
converge — and construct the divergent-edit case where convergence produces a value neither
user intended.

### Estimated Time
3-4 hours