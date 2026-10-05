# Distributed Consensus - Mini Project

## Project: A Three-Node Raft Cluster You Can Chaos-Test

### Objective
Implement enough of Raft to elect a leader, replicate a log, and commit entries safely —
then break it with partitions and prove the safety properties hold.

### Requirements
1. `RaftNode` with persistent `currentTerm`, `votedFor`, and log
2. Request/response RPCs: `RequestVote`, `AppendEntries` (heartbeats carry empty entries)
3. Deterministic simulation: virtual clock, message queue, no `Thread.sleep` in tests
4. A `Network` that can drop, duplicate, and delay messages
5. Property assertions: at most one leader per term, no committed entry lost

### Steps

**Step 1: State the invariants before coding**
- Safety 1 (Election Safety): at most one leader per term
- Safety 2 (Log Matching): same index + same term ⇒ identical prefix
- Safety 3 (Leader Completeness): a committed entry exists in every future leader's log
- Availability: a majority of up nodes ⇒ a leader within an election timeout

**Step 2: Persistent state (survives restart)**
```java
final class RaftNode {
    private int currentTerm;          // persisted
    private String votedFor;          // persisted
    private final List<Entry> log;    // persisted
    private int commitIndex;          // volatile
    private String leaderId;          // volatile

    boolean isLeader() { return leaderId.equals(id) && state == State.LEADER; }
}
```
A `Storage` interface keeps term/votedFor/log so tests can crash-and-restart nodes.

**Step 3: Election timeout with randomized jitter**
```java
void onTimeout() {
    if (state != State.FOLLOWER) return;
    currentTerm++;
    votedFor = id;
    persist();
    state = State.CANDIDATE;
    final int votes = 1 + countVotes(selfVotesFromPeers());   // vote for self
    if (majority(votes)) becomeLeader();
}
```
Randomize the timeout in `[T, 2T]` or every node times out at once and there is no leader.

**Step 4: AppendEntries and the commit rule**
```java
void onAppendEntries(int prevLogIndex, int prevLogTerm, Entry entry, int leaderCommit) {
    if (prevLogIndex > 0 && termAt(prevLogIndex) != prevLogTerm) {
        reply(false, currentTerm);            // follower rejects; leader backs up
        return;
    }
    truncateConflictingSuffix(prevLogIndex + 1);
    append(entry);
    persist();
    commitIndex = Math.max(commitIndex, Math.min(leaderCommit, lastIndex()));
    reply(true, currentTerm);
}
```
The leader's side is where the safety lives: **`commitIndex` only advances once a majority
has acked the same index**, and `N - commitIndex` may only move forward.

```java
void advanceCommit() {
    for (int n = lastIndex(); n > commitIndex; n--) {
        if (majority(countAcksFor(n)) && termAt(n) == currentTerm) { commitIndex = n; return; }
    }
}
```
Only entries from the *current* term may be committed by counting — this detail is what
prevents the Figure 8 bug.

**Step 5: Chaos the cluster**
1. Partition the leader away — a new leader must emerge in the majority side
2. Kill the leader — followers time out and elect a replacement
3. Partition, then heal — the old leader must step down when it sees a higher term
4. In every scenario assert: one leader max, no lost committed entries

### Deliverables
1. `RaftNode`, `Storage`, `Network`, `Cluster` simulator in `com.distributed.consensus`
2. Deterministic tests for each of the four scenarios
3. A `Log` consistency checker that diffs all replicas after every test
4. A short note on which Raft elections you skipped and why (CHALLENGE territory)

### Extension (CHALLENGE)
Implement log compaction via snapshotting and `InstallSnapshot`, then prove the cluster
recovers a follower that has been down long enough to fall behind compaction.

### Estimated Time
6-8 hours