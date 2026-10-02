# Distributed Consensus Theory

## Consensus Problem

### Definition
Given N nodes, agree on a single value despite failures.
**Safety**: Nothing bad happens (all decide same value, value was proposed).
**Liveness**: Something good eventually happens (decide if majority up).

### FLP Impossibility
> In an **asynchronous** system with even **one crash failure**, no **deterministic** consensus protocol can guarantee both safety and termination.

**Implications**:
- Real systems use timeouts (partial synchrony) or randomization
- Safety always guaranteed; liveness only during "good" periods
- Practical systems: Raft, Paxos, Zab assume partial synchrony

---

## Raft Consensus

### Core Idea
**Understandable** consensus via strong leader. Decomposed into:
1. **Leader Election**
2. **Log Replication**
3. **Safety** (election restriction)
4. **Membership Changes**

### Node States
```
Follower → (timeout) → Candidate → (votes) → Leader
    ↑                    ↓                    ↓
    └─────── (higher term) ←──────────────────┘
```

### Terms & Log
- **Term**: Logical time, increments on election
- **Log Entry**: `{term, index, command}`
- **Commit Index**: Highest index known committed
- **Last Applied**: Highest index applied to state machine

### Leader Election
1. Follower increments term, becomes Candidate
2. Votes for self, sends RequestVote RPCs
3. **Election restriction**: Only vote for candidate with log at least as up-to-date
   - Compare: (lastLogTerm, lastLogIndex) lexicographically
4. Wins if majority votes → becomes Leader
5. Sends empty AppendEntries (heartbeat) to establish authority

**Randomized timeouts**: 150-300ms prevents split votes.

### Log Replication
```
Client → Leader: append command
Leader: append to local log
Leader → Followers: AppendEntries(prevLogIndex, prevLogTerm, entries[])
Follower: if matches prevLogIndex/Term → append, reply success
Leader: on majority success → commit, apply, reply client
```

### Safety: Election Restriction
**Leader Completeness**: If entry committed in term T, all future leaders for terms > T contain that entry.
**Proof**: Candidate must have all committed entries (majority overlap with commit quorum).

### Read Optimization: Lease Read
Leader serves reads locally if:
1. Has valid lease (heartbeat from majority within election timeout)
2. Or: ReadIndex — ask majority for commitIndex, wait for own commitIndex ≥ that

---

## Paxos Family

### Basic Paxos (Single Decree)
**Roles**: Proposer, Acceptor, Learner (often same nodes)

**Phase 1 (Prepare)**:
```
Proposer → Acceptors: Prepare(n)
Acceptor: if n > highestPreparePromised → promise(n), reply (acceptedProposal, acceptedValue)
```

**Phase 2 (Accept)**:
```
Proposer: if majority promised → pick value (highest proposal from promises, or own)
Proposer → Acceptors: Accept(n, value)
Acceptor: if n ≥ highestPreparePromised → accept, reply
```

**Learning**: Learners learn when majority accept same value.

### Multi-Paxos (Log Replication)
Optimization: Stable leader → skip Phase 1 for subsequent entries.
```
Leader: for each slot i:
  Propose(i, value) → Phase 2 only (Accept)
```
**Distinguished proposer** (leader) avoids livelock.

### Fast Paxos
Allow learners to accept directly (bypass leader) for non-conflicting commands.
- **Classic quorum**: Majority
- **Fast quorum**: 3/4 majority for fast path
- **Tradeoff**: Lower latency (1 RTT) but larger quorum

---

## Zab (ZooKeeper Atomic Broadcast)

### Differences from Raft
| Aspect | Raft | Zab |
|--------|------|-----|
| Term | Term | Epoch |
| Leader | Must have all committed | Can be behind, catches up |
| Log | Entries | Transactions (id, zxid) |
| Membership | Joint consensus | Dynamic config |

### Phases
1. **Discovery**: Leader collects state from followers
2. **Synchronization**: Leader syncs followers (proposes missing txns)
3. **Broadcast**: Normal operation (like Raft replication)

**Zxid**: 64-bit (epoch << 32 | counter). Ensures global ordering.

---

## Cluster Membership Changes

### Problem
Change cluster config (add/remove nodes) without losing safety.

### Joint Consensus (Raft)
```
C_old → C_old,new (joint) → C_new
```
- **C_old,new**: Both old and new majorities required
- **Transition**: 
  1. Leader proposes C_old,new (enters joint)
  2. Once committed, proposes C_new
  3. Once committed, new config active

### Why Not Direct Switch?
If C_old → C_new directly, old and new majorities might not overlap → two leaders possible.

### Single-Node Changes (Simpler)
Change one node at a time. If majority overlap guaranteed, safe.

---

## Lease Mechanisms

### Leader Lease
Leader obtains "lease" from majority: "I am leader until time T".
- Requires synchronized clocks (bounded drift)
- Allows read-only operations without quorum
- **Risk**: Clock skew → two leaders with valid leases

### ReadIndex (Raft, no clocks)
1. Leader gets commitIndex from majority (heartbeat)
2. Waits for own commitIndex ≥ that
3. Serves read locally
**Safe**: No clocks needed, but 1 RTT for read.

### Follower Reads
Follower serves read if:
- Knows leader's commitIndex (via heartbeat)
- Its own commitIndex ≥ that
- **Risk**: Stale reads if follower behind

---

## Snapshotting & Log Compaction

### Problem
Log grows indefinitely.

### Solution: Snapshot
1. State machine writes snapshot to disk
2. Includes: lastIncludedIndex, lastIncludedTerm
3. Deletes log before that index

### InstallSnapshot RPC
Leader sends snapshot to lagging follower:
- Chunked transfer
- Follower restores state machine
- Resumes log replication from snapshot index

---

## Production Considerations

### Performance
| Optimization | Effect |
|--------------|--------|
| Pipeline AppendEntries | Higher throughput |
| Batch client requests | Amortize RPC cost |
| Async disk writes | Lower latency (risk on crash) |
| ReadIndex/Lease reads | Scale reads |

### Monitoring
- **Leader stability**: term changes, election frequency
- **Replication lag**: commitIndex - follower matchIndex
- **Log size**: time to snapshot
- **RPC latency**: p50, p99 for AppendEntries

### Common Issues
| Symptom | Cause |
|---------|-------|
| Frequent leader changes | Network issues, GC pauses, disk latency |
| High replication lag | Slow follower, network, large entries |
| Stuck commit | Follower down, quorum lost |
| Split brain | Clock skew (leases), network partition |

---

## Mathematical Foundations

### Quorum Intersection
```
N = cluster size
Q = quorum size (majority = N/2 + 1)
Any two quorums intersect: Q + Q > N
```
Ensures: any two leaders share a voter → election restriction works.

### Liveness Condition
```
Network: eventually synchronous (bounded delay)
Clocks: bounded drift
Failures: < N/2 simultaneous
→ Consensus terminates
```

### Raft Log Matching Property
If two logs contain entry with same index and term, all preceding entries identical.
**Proof**: By induction on index. Leader only appends, never overwrites.

---

## References
- "In Search of an Understandable Consensus Algorithm" - Ongaro & Ousterhout (Raft)
- "Paxos Made Simple" - Lamport
- "ZooKeeper: Wait-free coordination" - Hunt et al.
- "Consensus on Transaction Commit" - Gray & Lamport (2PC vs Paxos)
- etcd/Raft implementation: github.com/etcd-io/raft