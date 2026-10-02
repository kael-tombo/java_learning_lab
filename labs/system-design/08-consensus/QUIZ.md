# Distributed Consensus Quiz

## Questions

1. **FLP Impossibility**: FLP states no deterministic consensus in async systems with one crash. How do Raft/Paxos circumvent this? What assumption do they add?

2. **Raft Election Restriction**: A candidate with log `[term=3, index=5]` requests votes. A voter has log `[term=3, index=6]`. Does the voter grant vote? What if voter has `[term=4, index=4]`?

3. **Log Replication**: Leader (term 5) has entries up to index 10. Follower has up to index 8 (term 5). Leader sends AppendEntries with prevLogIndex=8, prevLogTerm=5, entries[9,10]. Follower replies success. Is entry 10 committed? When?

4. **Leader Lease vs ReadIndex**: Compare leader lease reads vs ReadIndex. Which requires clock synchronization? Which adds latency? Which is safer under clock skew?

5. **Joint Consensus**: Why does Raft use `C_old,new` intermediate config instead of direct `C_old → C_new`? Give a scenario where direct switch causes split brain.

6. **Paxos vs Raft**: In Multi-Paxos, what happens if the distinguished proposer (leader) fails? How does a new proposer learn the current state? Compare to Raft leader election.

7. **Zab vs Raft**: Zab leader can be "behind" followers during discovery phase. Why is this safe? How does Raft prevent this?

8. **Snapshotting**: Leader snapshots at index 100 (term 5). Follower is at index 50. Leader sends InstallSnapshot. Follower restores, but its log has entries 51-60 (term 4) that conflict with snapshot. What happens?

9. **Cluster Change + Failure**: 5-node cluster (A,B,C,D,E). Change to 3-node (A,B,C). During joint consensus `C_old,new`, nodes D and E crash. Can cluster still commit? What quorum is needed?

10. **Real-World Design**: Build a config service for 1000-node fleet. Requirements: read latency < 5ms, write latency < 50ms, survive 2 node failures, config changes < 1s propagation. Choose: (a) Raft (etcd), (b) Paxos (Chubby-style), (c) Zab (ZooKeeper), (d) Custom lease-based. Justify.

---

## Answers

1. **Circumvention**: They assume **partial synchrony** — eventually messages arrive within bounded time, clocks have bounded drift. This allows timeouts for leader election. Liveness guaranteed only during synchronous periods.

2. **Election Restriction**:
   - Voter `[3,6]` vs Candidate `[3,5]`: Voter's log is **more up-to-date** (same term, higher index) → **DENY** vote.
   - Voter `[4,4]` vs Candidate `[3,5]`: Voter's term higher (4 > 3) → **DENY** vote (candidate's term stale).
   - Candidate must have log ≥ voter's (term, then index).

3. **Commitment**: Entry 10 **not yet committed**. Only replicated to 1 follower. Need majority (3 of 5). When leader gets success from 2 followers (including self), commitIndex advances to 10.

4. **Comparison**:
   - **Leader Lease**: Requires **clock sync** (bounded drift). **Zero latency** reads. **Unsafe** under clock skew (two leaders may have valid leases).
   - **ReadIndex**: **No clocks needed**. **1 RTT** latency (heartbeat round). **Safe** always.

5. **Joint Consensus Necessity**: 
   - Direct switch: Old majority {A,B,C}, new majority {C,D,E}. Overlap = {C} only.
   - If partition splits {A,B} vs {D,E}, both could elect leaders (each has majority in their config).
   - Joint `C_old,new` requires **both** old and new majorities → overlap guaranteed.

6. **Multi-Paxos Leader Failure**:
   - New proposer runs Phase 1 (Prepare) with higher proposal number.
   - Learns previously accepted values from majority promises.
   - Continues from highest proposal.
   - **Raft**: Simpler — new leader elected via RequestVote, log completeness guaranteed by election restriction.

7. **Zab Discovery Phase Safety**:
   - Leader collects **epoch** from followers, picks max(epoch) + 1 as new epoch.
   - Followers only accept proposals with epoch ≥ their acknowledged epoch.
   - Leader syncs missing transactions **before** broadcast.
   - **Raft**: Candidate must have log ≥ voters (election restriction) → leader always has all committed entries.

8. **InstallSnapshot Conflict**:
   - Follower **discards** its log entries 51-60 (term 4).
   - Snapshot (index 100, term 5) supersedes — leader has more up-to-date state.
   - Follower restores snapshot, resumes from index 100.

9. **Joint Consensus Quorum**:
   - `C_old,new`: Old={A,B,C,D,E} (maj=3), New={A,B,C} (maj=2). **Both majorities required** → need 3 from old AND 2 from new.
   - After D,E crash: Old quorum needs 3 of {A,B,C} → possible. New quorum needs 2 of {A,B,C} → possible.
   - **Yes**, cluster can commit (A,B,C satisfy both).

10. **Choice: (a) Raft (etcd)**.
    - **Why**: 
      - etcd uses Raft, optimized for reads (ReadIndex/Lease).
      - 5-node cluster: tolerates 2 failures.
      - Read latency ~1-2ms (local lease read), write ~10-20ms (Raft quorum).
      - Config change propagation: watch mechanism < 100ms.
      - Battle-tested at scale (Kubernetes, CoreDNS).
    - **Why not others**: Chubby/Paxos more complex; ZooKeeper/Zab higher latency; custom lease risky.