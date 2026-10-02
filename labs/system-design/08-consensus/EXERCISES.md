# Distributed Consensus Exercises

## Exercise 1: Raft Implementation from Scratch (Code Task)

**Implement** a minimal Raft node:

```java
// RaftNode.java
public class RaftNode implements RaftService {
    // State
    enum Role { FOLLOWER, CANDIDATE, LEADER }
    Role role;
    int currentTerm;
    String votedFor;
    List<LogEntry> log;
    int commitIndex;
    int lastApplied;
    
    // Volatile leader state
    int[] nextIndex;
    int[] matchIndex;
    
    // RPCs
    public RequestVoteResponse requestVote(RequestVoteRequest req);
    public AppendEntriesResponse appendEntries(AppendEntriesRequest req);
    public InstallSnapshotResponse installSnapshot(InstallSnapshotRequest req);
    
    // Client
    public ClientResponse propose(Command cmd);
    
    // Internal
    void startElection();
    void becomeLeader();
    void replicateLog();
    void advanceCommitIndex();
    void applyToStateMachine();
}
```

**LogEntry**: `{term, index, command}`

**Requirements**:
- Leader election with randomized timeouts (150-300ms)
- Log replication with AppendEntries (matching, truncation)
- Commit index advancement (majority, current-term rule)
- State machine application (sequential)
- Persistent state (term, votedFor, log) to disk
- Snapshotting (trigger at log size threshold)

**Testing**:
1. Single node: propose → committed → applied
2. 3 nodes: kill leader → new election → continue
3. Network partition: minority partition cannot commit
4. Log divergence: follower behind → catch up via AppendEntries
5. Snapshot: large log → snapshot → new node joins → InstallSnapshot

---

## Exercise 2: Leader Election Correctness (Proof Task)

**Prove** or **disprove** each claim:

1. **Claim**: "In Raft, a leader in term T always has all entries committed in terms < T."
2. **Claim**: "If a follower grants vote to candidate C in term T, C's log is at least as up-to-date as the follower's."
3. **Claim**: "Raft's election restriction (log up-to-date check) is sufficient to guarantee Leader Completeness."
4. **Claim**: "A cluster can have two leaders in the same term if network partitions."

For each: Provide proof sketch or counterexample scenario.

---

## Exercise 3: Cluster Membership Change (Code Task)

**Implement** joint consensus membership change:

```java
// MembershipManager.java
public class MembershipManager {
    // Config states: STABLE, JOINT, TRANSITIONING
    
    // Current config: Set<Node> nodes
    // Pending config: Set<Node> nodes (during joint)
    
    // TODO:
    // proposeConfigChange(newNodes) → returns ConfigChangeId
    // handleConfigChangeEntry(entry) → updates state machine
    // getQuorumSize() → depends on current phase
    // canCommit() → checks both majorities in joint phase
}

// ConfigChange entry in log:
class ConfigChange {
    Set<Node> oldNodes;
    Set<Node> newNodes; // null = stable, non-null = joint
}
```

**Requirements**:
- Leader only: propose config change (append to log)
- Joint phase: require majority from BOTH old and new configs
- Transition to new config: second config change entry
- New nodes: start as non-voting, catch up log, then become voting
- Removed nodes: step down if leader, stop voting

**Test**:
1. 3 nodes → add 2 nodes (5 total) → verify joint quorum works
2. Remove node during joint → verify old majority still works
3. Leader removed → verify new leader elected from remaining
4. Rapid changes: add, remove, add → verify no split brain

---

## Exercise 4: Read Optimization Comparison (Experimental Task)

**Implement** three read paths in your Raft node:

```java
// ReadPath.java
interface ReadPath {
    ReadResult read(String key);
}

// 1. Quorum Read (baseline)
class QuorumRead implements ReadPath { ... }

// 2. ReadIndex
class ReadIndexRead implements ReadPath { ... }

// 3. Leader Lease
class LeaseRead implements ReadPath { 
    // Requires clock sync (simulate with bounded drift)
}
```

**Benchmark** on 5-node cluster:
- Workload: 90% reads, 10% writes
- Measure: p50/p99 read latency, throughput
- Vary: network RTT (1ms, 5ms, 20ms), clock drift (0ms, 1ms, 10ms)

**Analyze**:
| Metric | Quorum | ReadIndex | Lease (0 drift) | Lease (10ms drift) |
|--------|--------|-----------|-----------------|-------------------|
| p50 latency | | | | |
| p99 latency | | | | |
| Throughput | | | | |
| Stale reads | 0 | 0 | 0 | ? |

**Discussion**: When is each appropriate? What happens to lease reads under clock skew?

---

## Exercise 5: Paxos vs Raft Comparison (Code Task)

**Implement** Basic Paxos for a single decree, then compare to Raft:

```java
// PaxosNode.java
class PaxosNode {
    // Proposer
    void propose(Value v);
    // Phase 1
    PrepareResponse sendPrepare(int n);
    // Phase 2
    AcceptResponse sendAccept(int n, Value v);
    
    // Acceptor
    PromiseResponse onPrepare(int n);
    AcceptedResponse onAccept(int n, Value v);
    
    // Learner
    void onAccepted(int n, Value v);
}
```

**Multi-Paxos Extension**:
- Distinguished proposer (leader)
- Skip Phase 1 for subsequent proposals
- Log replication similar to Raft

**Compare** (document):
| Aspect | Basic Paxos | Multi-Paxos | Raft |
|--------|-------------|-------------|------|
| Understandability | | | |
| Leader stability | | | |
| Log structure | | | |
| Membership change | | | |
| Implementation complexity | | | |

---

## Exercise 6: Zab Protocol Analysis (Analysis Task)

**Analyze** ZooKeeper's Zab protocol:

1. **Discovery Phase**: Leader collects `CEPOCH` from followers, picks new epoch = max + 1. Why is this safe if leader was partitioned?

2. **Synchronization Phase**: Leader sends `SYNC` with missing transactions. Follower acknowledges. What if follower has transactions leader doesn't?

3. **Broadcast Phase**: Similar to Raft. What is `ZXID` and how does it ensure ordering?

4. **Compare Zab vs Raft**:
   - Zab allows leader to be behind → how does it catch up safely?
   - Zab uses `NEWLEADER`/`ACK` instead of `AppendEntries` → differences?
   - Zab config changes: dynamic, no joint consensus → how safe?

**Deliverable**: 2-page comparison with diagrams.

---

## Exercise 7: Consensus Performance Tuning (Experimental Task)

**Target**: Your Raft implementation or etcd/Consul.

**Tune and measure**:

1. **Heartbeat interval**: 50ms, 100ms, 500ms
   - Effect on election timeout, failover time, network load

2. **Election timeout range**: 150-300ms, 500-1000ms, 1-2s
   - Effect on stability vs failover speed

3. **Batch size**: 1, 10, 100, 1000 entries per AppendEntries
   - Throughput vs latency tradeoff

4. **Snapshot interval**: Every 10k, 100k, 1M entries
   - Compaction time, new node join time, memory usage

5. **Pipeline depth**: 1 (sync), 5, 10, 50
   - Throughput under high load

**Document**: For each parameter, show latency/throughput curves. Recommend production defaults.

---

## Exercise 8: Linearizability Testing (Verification Task)

**Implement** a linearizability checker for your consensus system:

```java
// LinearizabilityChecker.java
class LinearizabilityChecker {
    // History: List<Operation> where Operation = {type: READ/WRITE, key, value, startTime, endTime}
    
    // TODO: 
    // check(history) → boolean (linearizable?)
    // Uses Knossos/Wing-Gong algorithm or similar
}

// Operation generator:
class OperationGenerator {
    // Generates concurrent read/write operations
    // Verifies against model (e.g., single-threaded map)
}
```

**Test** your Raft implementation:
1. Run 1000 concurrent clients doing reads/writes
2. Capture history with timestamps
3. Run checker → any violations?
4. Inject failures (kill leader, partition) during test → verify safety

**Tools**: Use Jepsen-style testing or `porcupine` (Go) / `knossos` (Clojure) model.

---

## Exercise 9: Consensus in Production — Incident Response (Scenario Task)

**Scenario**: Your 5-node etcd cluster (Raft) shows:
- Leader changes every 30 seconds
- Replication lag spikes to 10k entries
- Client read latency p99 > 500ms

**Debugging steps** (document your runbook):
1. What metrics do you check first?
2. How do you distinguish: network issue vs GC pause vs disk latency?
3. What commands do you run on each node?
4. If leader is thrashing due to GC, what config changes help?
5. If disk is slow, what Raft parameters to adjust?

**Failure Injection Practice**:
1. Add 100ms disk latency to one follower → observe lag
2. Kill leader process (SIGKILL) → measure failover time
3. Partition network (iptables) between leader and 2 followers → verify minority steps down

---

## Exercise 10: Building a Config Service (Design Task)

**Design** a distributed configuration service using consensus:

**Requirements**:
- 10,000 services reading config
- Config updates: 10/minute
- Read latency: < 5ms p99
- Write latency: < 50ms p99
- Propagation: < 1s to all readers
- Survive 2 node failures (5-node cluster)
- Config size: up to 1MB per key

**Architecture**:
```
Services → (watch) → Config Service (Raft cluster) → (notify) → Services
```

**Decide and justify**:
1. **Consensus backend**: etcd (Raft) vs Consul (Raft) vs ZooKeeper (Zab) vs custom
2. **Read path**: Quorum / ReadIndex / Lease / Follower reads / Client-side cache
3. **Watch mechanism**: Long-polling / WebSocket / gRPC streaming
4. **Large values**: Store in Raft log? External blob store (S3) with reference in log?
5. **Schema evolution**: Config versioning, rollback, canary deploy

**Deliverable**: Architecture doc + config + capacity plan.

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1. Raft Implementation | 25 | All features work, passes tests |
| 2. Election Proofs | 10 | Correct proofs/counterexamples |
| 3. Membership Change | 15 | Joint consensus correct, tested |
| 4. Read Optimization | 15 | Implemented, benchmarked, analyzed |
| 5. Paxos vs Raft | 10 | Working code, clear comparison |
| 6. Zab Analysis | 10 | Accurate, detailed |
| 7. Performance Tuning | 15 | Systematic, documented results |
| 8. Linearizability Test | 15 | Checker works, finds/confirms bugs |
| 9. Incident Response | 10 | Practical runbook, failure injection |
| 10. Config Service Design | 10 | Complete, justified, production-ready |

**Total**: 135 points