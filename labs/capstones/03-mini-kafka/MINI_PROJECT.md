# Mini Kafka — MINI PROJECT

## Project: A Partitioned, Replicated Log with Consumer Groups

`minikafka` in Java 21: append-only segments, leader/follower replication with
ISR, a consumer group coordinator, at-least-once delivery, and a CLI to
inspect and replay.

### Scope

- **Log**: append, fetch by offset, segment files, size/time-based rollover,
  time and size retention, and a compaction mode.
- **Replication**: leader + followers, periodic fetchers, ISR tracking, leader
  election on failure, `acks=0|1|all` semantics.
- **Groups**: coordinator, member registration, assignment (range/round-robin),
  rebalance on join/leave, offset commit and resume.
- **Delivery**: producer retry + idempotence, consumer commit-after-process,
  a DLQ.
- **CLI**: `append`, `consume`, `describe`, `offsets`, `reassign-leader`.

### Architecture

```
producer -> [partition] -> [log segment files]  replicated to followers
                |                                      |
                |  fetch(offset)                        |  ISR tracking
                v                                      v
         consumer group (members) <-- coordinator -- offsets store
                |
           DLQ on failure
```

### Implementation — the log

```java
public final class PartitionLog implements Closeable {
    private final Path dir;
    private final long segmentBytes;
    private final long retentionMs;
    private final Map<String, LogSegment> segments = new LinkedHashMap<>();
    private long baseOffset;                 // offset of the first live segment
    private long highWaterMark;              // next offset to be assigned
    private long logEndOffset;               // next offset to be persisted

    public void append(byte[] record) {
        maybeRoll();
        LogSegment seg = segments.get(activeSegmentName());
        long offset = logEndOffset;
        seg.append(offset, record);
        logEndOffset++;
        highWaterMark = Math.max(highWaterMark, logEndOffset);
    }

    /**
     * Offset semantics, spelled out because everything else depends on them:
     *   baseOffset    - earliest offset still retained
     *   logEndOffset  - next offset that will be written (the "log end")
     *   highWaterMark - next offset that is replicated to all ISR members
     *
     * A consumer reading at the HWM may get records another consumer will not
     * see if the leader fails; reading at the log end is the "only committed"
     * position. This distinction is the whole basis of the delivery guarantees.
     */
    public FetchResult fetch(long fromOffset, int maxBytes) {
        long start = Math.max(fromOffset, baseOffset);
        if (start >= logEndOffset) return FetchResult.empty(start, highWaterMark, logEndOffset);
        List<Record> out = new ArrayList<>();
        int bytes = 0;
        for (LogSegment seg : segments.values()) {
            for (long o = Math.max(start, seg.baseOffset()); o < seg.highOffset(); o++) {
                Record r = seg.read(o);
                if (r == null) break;
                out.add(r);
                bytes += r.sizeInBytes();
                if (bytes >= maxBytes) return new FetchResult(out, start + out.size(),
                        highWaterMark, logEndOffset);
            }
        }
        return new FetchResult(out, start + out.size(), highWaterMark, logEndOffset);
    }

    private void maybeRoll() {
        LogSegment active = segments.get(activeSegmentName());
        if (active != null && active.sizeBytes() >= segmentBytes) {
            roll(Duration.ofSeconds(1));
        }
    }

    /** Retention deletes whole segments. This is why a consumer that falls too
     *  far behind loses data and must reset to the log start. */
    public int deleteExpiredSegments(long now) {
        int removed = 0;
        Iterator<Map.Entry<String, LogSegment>> it = segments.entrySet().iterator();
        while (it.hasNext()) {
            LogSegment seg = it.next().getValue();
            if (now - seg.lastModified() > retentionMs) {
                it.remove();
                deleteQuietly(seg.path());
                baseOffset = seg.highOffset();
                removed++;
            }
        }
        return removed;
    }
}
```

### Implementation — replication and ISR

```java
public final class ReplicaManager {
    private final Map<String, PartitionState> partitions = new ConcurrentHashMap<>();

    public record PartitionState(String topicPartition, String leaderId,
                                 Map<String, Long> followerLags,      // replica -> lag
                                 Set<String> isr,
                                 long highWaterMark, long leaderEpoch) {
        public boolean hasHealthyIsr() { return isr.size() >= minIsr(); }
        public boolean underReplicated() { return isr.size() < replicas(); }
    }

    /** Follower fetch. The lag is what determines ISR membership, and ISR is
     *  what `acks=all` is satisfied against. */
    public void onFetchResponse(String replicaId, String tp, long fetchOffset,
                                long logEndOffset, long highWaterMark) {
        partitions.computeIfPresent(tp, (k, st) -> {
            Map<String, Long> lags = new HashMap<>(st.followerLags());
            lags.put(replicaId, Math.max(0, st.logEndOffset - fetchOffset));
            Set<String> isr = new HashSet<>(st.isr());
            // A replica is in the ISR if it has caught up to the LEO, within tolerance.
            if (lags.get(replicaId) <= replicaLagTolerance) isr.add(replicaId);
            else isr.remove(replicaId);
            return new PartitionState(tp, st.leaderId(), lags, isr,
                    Math.min(st.highWaterMark(), highWaterMark), st.leaderEpoch());
        });
    }

    /** acks=all means "all replicas in the ISR have it", NOT "all replicas". */
    public AppendResult append(String tp, byte[] record, String acks) {
        PartitionState st = partitions.get(tp);
        if (st == null) return AppendResult.notLeader(st == null ? null : st.leaderId());
        if ("all".equals(acks) && !st.hasHealthyIsr()) {
            return AppendResult.notEnoughReplicas(st.isr());
        }
        partitionLog(tp).append(record);
        return switch (acks) {
            case "0" -> AppendResult.acked(highWaterMark(tp));
            case "1" -> AppendResult.acked(partitionLog(tp).logEndOffset());
            default  -> new AppendResult(AckStatus.REPLICATED, highWaterMark(tp),
                                          st.isr().size(), replicas());
        };
    }

    /** Election: highest offset wins, ties broken by replica id for determinism. */
    public String electLeader(String tp, Set<String> candidates) {
        return candidates.stream()
                .max(Comparator.comparingLong((String r) -> replicaFetchOffset(tp, r))
                        .thenComparing(Comparator.naturalOrder()))
                .orElseThrow(() -> new NoEligibleLeader(tp));
    }
}
```

### Implementation — consumer groups

```java
public final class GroupCoordinator {
    private final Map<String, GroupState> groups = new ConcurrentHashMap<>();

    public record Member(String id, String host, long lastHeartbeat) {}
    public record Assignment(String topic, Map<String, List<Integer>> partitionsByMember) {}

    public record GroupState(String groupId, Map<String, Member> members,
                             String leaderId, String assignmentEpoch,
                             Map<Integer, String> committedOffsets) {}

    public JoinResult join(String groupId, String memberId, String host) {
        GroupState st = groups.compute(groupId, (g, existing) -> {
            GroupState base = existing == null
                    ? new GroupState(g, new LinkedHashMap<>(), null, "0", new HashMap<>())
                    : existing;
            Map<String, Member> members = new LinkedHashMap<>(base.members());
            members.put(memberId, new Member(memberId, host, now()));
            String leader = base.leaderId() == null ? memberId : base.leaderId();
            return new GroupState(g, members, leader, base.assignmentEpoch(), base.committedOffsets());
        });
        return new JoinResult(st.leaderId(), needsRebalance(st));
    }

    /**
     * Rebalance: the leader computes a new assignment and everyone re-joins.
     * The cost is real — every member stops, re-reads offsets, and restarts.
     * It is the single largest source of consumer latency in a group.
     */
    public Assignment rebalance(String groupId, int partitions) {
        GroupState st = groups.get(groupId);
        if (st == null || !st.leaderId().equals(me())) throw new NotLeader(st);
        List<String> memberIds = new ArrayList<>(st.members().keySet());
        Collections.sort(memberIds);                      // deterministic
        Map<String, List<Integer>> out = new LinkedHashMap<>();
        for (int i = 0; i < memberIds.size(); i++) {
            int from = (int) Math.floor((double) i * partitions / memberIds.size());
            int to   = (int) Math.floor((double) (i + 1) * partitions / memberIds.size());
            out.put(memberIds.get(i), range(from, to));   // range assignor
        }
        bumpEpoch(groupId);
        return new Assignment(groupId, out);
    }
}
```

### Implementation — consumer with commit-after-process and DLQ

```java
public final class GroupConsumer implements Runnable {
    @Override public void run() {
        joinGroup();
        while (running) {
            Assignment a = coordinator.assignmentFor(groupId, memberId);
            Map<TopicPartition, Long> positions = new LinkedHashMap<>();
            for (var e : a.partitionsByMember().entrySet()) {
                if (!e.getKey().equals(memberId)) continue;
                for (int p : e.getValue()) {
                    TopicPartition tp = new TopicPartition(topic, p);
                    positions.put(tp, coordinator.committedOffset(groupId, tp));  // resume point
                }
            }
            for (var e : positions.entrySet()) {
                FetchResult fr = broker.fetch(e.getKey(), e.getValue(), maxBytes);
                for (Record r : fr.records()) {
                    if (!processWithRetry(r)) dlq.send(r, "exhausted retries");
                    // Commit AFTER processing. Committing before means a crash
                    // loses the record; this is the at-least-once contract.
                    coordinator.commit(groupId, e.getKey(), r.offset() + 1);
                }
            }
            sleep(pollIntervalMs);
        }
        leaveGroup();      // triggers a rebalance for everyone else
    }
}
```

### Implementation — idempotent producer

```java
public final class IdempotentProducer {
    private final Map<TopicPartition, Long> partitionEpochs = new HashMap<>();
    private final Map<TopicPartition, Long> nextSequence = new HashMap<>();

    public AppendResult send(String tp, byte[] key, byte[] value, String acks) {
        int p = partitioner(key);
        TopicPartition full = new TopicPartition(tp, p);
        long epoch = partitionEpochs.computeIfAbsent(full, k -> 0L);
        long seq = nextSequence.merge(full, 1L, Long::sum);
        // Sequence numbers let the broker reject a duplicate from a retry,
        // which is what turns at-least-once into effectively-once for this
        // producer session.
        AppendResult r = broker.append(full, seqNumbered(value, epoch, seq), acks);
        if (r.status() == DUPLICATE) return r;
        if (r.isLeaderChanged()) {
            partitionEpochs.merge(full, 1L, Long::sum);   // new producer session
            nextSequence.put(full, 0L);
            return send(tp, key, value, acks);              // one bounded retry
        }
        return r;
    }
}
```

### Test It

```java
@Test void replicationSurvivesLeaderLoss() {
    append("orders", 1000, "all");
    await().atMost(10, SECONDS).until(() -> isr("orders", 0).size() == 3);
    kill(followerOf("orders", 0));
    append("orders", 500, "all");
    assertEquals(1500, logEnd("orders", 0));                // acks=1 still served
    restart(followerOf("orders", 0));
    await().until(() -> isr("orders", 0).size() == 3);
    append("orders", 500, "all");
    assertEquals(2000, logEnd("orders", 0));                // caught up, ISR restored
}

@Test void acksAllFailsWithAMinimalIsr() {
    killTwoFollowers("orders", 0);
    AppendResult r = append("orders", 1, "all");
    assertEquals(AckStatus.NOT_ENOUGH_REPLICAS, r.status());
    assertEquals(AckStatus.OK, append("orders", 1, "1").status());  // acks=1 still works
}

@Test void groupRebalanceMovesPartitions() {
    join("billing", "m1"); join("billing", "m2");
    assertEquals(List.of(0, 1, 2, 3, 4, 5), assigned("billing", "m1"));
    join("billing", "m3");
    await().until(() -> assigned("billing", "m3").size() == 2);     // m3 gets a share
    assertEquals(0, assignedCount("billing", "m1") + assignedCount("billing", "m2")
                     - assignedCount("billing", "m1"));            // no duplicates
}

@Test void consumerResumesFromCommittedOffsetAfterCrash() {
    group("c1").consumeFrom("events", 0);
    process(100);
    killConsumer("c1");
    process(50);                                            // produced while down
    restartConsumer("c1");
    await().until(() -> processedBy("c1") >= 150);
    assertEquals(100, minOffsetProcessedBy("c1"));           // no gap
    assertTrue(duplicatesProcessedBy("c1").isEmpty());        // and no reprocessing
}
```

### Stretch

- Add log compaction: same key, keep the latest value, with the delete-tombstone rule.
- Add a read-only replica and demonstrate that it can fall behind the HWM.
- Implement a producer with transactions (offsets + output in one unit) and
  show read_committed isolation.
- Write a `minikafka-dump` tool that prints the log in a human-readable form.

## Deliverables

- [ ] Log with segments, rollover, offsets (base/logEnd/HWM), and retention
- [ ] Replication with ISR tracking, `acks=0|1|all`, and leader election
- [ ] Consumer group coordinator with rebalance on join/leave and offset resume
- [ ] Idempotent producer with sequence numbers and epoch on leader change
- [ ] Consumer with commit-after-process, retry, and DLQ
- [ ] CLI: append, consume, describe, offsets, reassign-leader
- [ ] Four tests covering failover, min-ISR, rebalance, and resume-after-crash
- [ ] A written table: for each failure, what `acks` setting is safe, and why
