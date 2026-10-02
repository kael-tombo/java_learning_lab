# Distributed Consensus Flashcards

## Consensus Fundamentals

**Q: What is the consensus problem?**
**A:** N nodes agree on one value. Safety: all decide same valid value. Liveness: eventually decide.

**Q: FLP Impossibility?**
**A:** No deterministic consensus in async system with 1 crash failure. Safety + Liveness impossible together.

**Q: How do practical systems circumvent FLP?**
**A:** Assume partial synchrony (eventually bounded message delay, bounded clock drift). Use timeouts.

**Q: Safety vs Liveness in practice?**
**A:** Safety **always** guaranteed. Liveness only during "good" periods (synchronous).

---

## Raft: Leader Election

**Q: Raft node states?**
**A:** Follower, Candidate, Leader.

**Q: Election trigger?**
**A:** Follower election timeout (150-300ms randomized) without hearing from leader.

**Q: RequestVote RPC?**
**A:** Candidate sends: term, candidateId, lastLogIndex, lastLogTerm.

**Q: Vote granting rule?**
**A:** Grant if: term ≥ currentTerm, and candidate's log ≥ voter's log (term, then index).

**Q: Why randomized timeouts?**
**A:** Prevent split votes (multiple candidates same term).

**Q: Leader legitimacy?**
**A:** Wins majority votes. Sends empty AppendEntries (heartbeat) to maintain authority.

---

## Raft: Log Replication

**Q: AppendEntries RPC?**
**A:** Leader → Follower: term, leaderId, prevLogIndex, prevLogTerm, entries[], leaderCommit.

**Q: Follower log matching?**
**A:** If log[prevLogIndex].term == prevLogTerm → append entries, truncate conflicts.

**Q: Commit rule?**
**A:** Entry committed when stored on majority. Leader commits when its commitIndex advances.

**Q: Leader commit advancement?**
**A:** Only advances commitIndex for entries in **current term** (prevents stale commits).

**Q: Log Matching Property?**
**A:** If two logs have same index & term, all preceding entries identical.

---

## Raft: Safety

**Q: Election Restriction?**
**A:** Candidate must have log at least as up-to-date as voter. Ensures Leader Completeness.

**Q: Leader Completeness?**
**A:** If entry committed in term T, all leaders for terms > T contain that entry.

**Q: Why only current-term commits?**
**A:** Prevents: old leader commits entry, new leader elected without it, overwrites it.

---

## Raft: Reads & Leases

**Q: Leader Lease Read?**
**A:** Leader gets majority promise "I won't elect new leader until time T". Reads locally. Needs clock sync.

**Q: ReadIndex?**
**A:** Leader gets commitIndex from majority via heartbeat. Waits for local commitIndex ≥ that. Reads locally. No clocks.

**Q: Follower Read?**
**A:** Follower serves if its commitIndex ≥ leader's commitIndex (from heartbeat). Risk: stale if behind.

---

## Raft: Membership Changes

**Q: Joint Consensus?**
**A:** Transition C_old → C_old,new (both majorities required) → C_new.

**Q: Why not direct switch?**
**A:** Old and new majorities might not overlap → split brain (two leaders).

**Q: Single-node changes?**
**A:** Add/remove one node at a time. Safe if majority overlap maintained.

---

## Paxos

**Q: Basic Paxos roles?**
**A:** Proposer, Acceptor, Learner.

**Q: Phase 1 (Prepare)?**
**A:** Proposer sends Prepare(n). Acceptor promises not to accept < n, replies with highest accepted.

**Q: Phase 2 (Accept)?**
**A:** Proposer sends Accept(n, value). Value = highest from promises, or own. Acceptor accepts if n ≥ promised.

**Q: Multi-Paxos optimization?**
**A:** Stable leader skips Phase 1 for subsequent slots. Distinguished proposer avoids livelock.

**Q: Fast Paxos?**
**A:** Learners can accept directly (1 RTT). Needs larger quorum (3/4). For non-conflicting commands.

---

## Zab (ZooKeeper)

**Q: Zab vs Raft — Leader election?**
**A:** Zab: Discovery → Sync → Broadcast. Leader can be behind, catches up. Raft: Leader always has all committed.

**Q: Zxid?**
**A:** 64-bit: epoch (32 bits) | counter (32 bits). Global ordering.

---

## Snapshotting

**Q: Why snapshot?**
**A:** Log grows indefinitely. Snapshot compacts state.

**Q: InstallSnapshot?**
**A:** Leader sends snapshot to lagging follower. Follower restores state machine, resumes from snapshot index.

**Q: Snapshot includes?**
**A:** lastIncludedIndex, lastIncludedTerm, state machine data.

---

## Production

**Q: Common leader instability causes?**
**A:** Network issues, GC pauses, disk latency, clock skew.

**Q: Replication lag indicators?**
**A:** commitIndex - matchIndex high. Slow follower, network, large entries.

**Q: Pipeline AppendEntries?**
**A:** Send next batch before previous acked. Higher throughput.

**Q: ReadIndex vs Lease tradeoff?**
**A:** Lease: 0 RTT, needs clocks. ReadIndex: 1 RTT, no clocks, always safe.

---

## Mathematical

**Q: Quorum intersection?**
**A:** Majority quorums: Q = N/2 + 1. Q + Q > N → any two intersect.

**Q: Raft election quorum?**
**A:** Majority of cluster size (N/2 + 1).

**Q: Joint consensus quorum?**
**A:** Need majority of C_old AND majority of C_new simultaneously.