# Consensus - Code Deep Dive

Pure Java. A single-file Raft-shaped cluster you can kill nodes in.

## 1. Server State and the Persistent Log

```java
package systemdesign.consensus;

import java.io.*;
import java.util.*;

/**
 * The state a Raft server must persist before responding to anything else.
 *
 * Everything in `volatile` is lost on restart. Everything else must hit disk
 * (fsync) BEFORE the RPC that required it is acknowledged. This is not
 * "persistence for durability" — it is required for SAFETY. A node that
 * forgets its term will vote twice in the same term and break the protocol.
 */
public final class RaftServer {

    public enum Role { FOLLOWER, CANDIDATE, LEADER }

    private volatile Role role = Role.FOLLOWER;
    private volatile int currentTerm = 0;      // monotonically increasing
    private volatile String votedFor = null;   // cleared each new term
    private volatile int commitIndex = 0;     // highest index known committed
    private volatile int lastApplied = 0;     // index handed to the state machine

    /** The log. index 0 is a sentinel so prevLogIndex is never negative. */
    private final List<LogEntry> log = Collections.synchronizedList(new ArrayList<>());
    private final LogEntry sentinel = new LogEntry(0, 0, null);

    // Leader-only state, rebuilt on every election (see the warning below).
    private final Map<Integer, Integer> nextIndex = new HashMap<>();
    private final Map<Integer, Integer> matchIndex = new HashMap<>();

    public record LogEntry(int index, int term, byte[] command) {
        public boolean isSentinel() { return index == 0; }
    }

    public RaftServer() { log.add(sentinel); }

    // ---- durability -------------------------------------------------------
    private final File stateFile = new File("raft-state.bin");

    /**
     * fsync-backed persist. In production this is a WAL append + group commit.
     * The critical property: NO acknowledgement is sent until this returns.
     */
    public synchronized void persist() throws IOException {
        try (FileOutputStream fos = new FileOutputStream(stateFile);
             DataOutputStream out = new DataOutputStream(new BufferedOutputStream(fos))) {
            out.writeInt(currentTerm);
            out.writeUTF(votedFor == null ? "" : votedFor);
            out.writeInt(log.size());
            for (LogEntry e : log) {
                out.writeInt(e.index());
                out.writeInt(e.term());
                int n = e.command() == null ? -1 : e.command().length;
                out.writeInt(n);
                if (n > 0) out.write(e.command());
            }
            out.flush();
            fos.getFD().sync();   // <-- the line that makes it survive a crash
        }
    }

    /** Called on restart, before accepting a single RPC. */
    public synchronized void restore() throws IOException {
        if (!stateFile.exists()) return;
        try (DataInputStream in = new DataInputStream(new FileInputStream(stateFile))) {
            currentTerm = in.readInt();
            String v = in.readUTF();
            votedFor = v.isEmpty() ? null : v;
            int n = in.readInt();
            log.clear();
            for (int i = 0; i < n; i++) {
                int idx = in.readInt(), term = in.readInt(), len = in.readInt();
                byte[] cmd = len < 0 ? null : new byte[len];
                if (len > 0) in.readFully(cmd);
                log.add(new LogEntry(idx, term, cmd));
            }
        }
        // term only ever increases, even across restarts
        role = Role.FOLLOWER;
    }
}
```

**Residual risk:** `fos.getFD().sync()` per RPC costs a full disk round trip and
caps throughput near `1 / fsync`. Group commit is mandatory in a real
implementation (see `MATH_FOUNDATION.md`, group commit table).

## 2. Election Timeout and RequestVote

```java
/**
 * The election timeout is the liveness escape hatch. Raft gives up on FLP's
 * guarantee and uses wall-clock time; the randomisation is what prevents two
 * candidates from colliding forever.
 */
public final class ElectionTimer {
    private final long minMs;
    private final long maxMs;
    private long deadline;

    public ElectionTimer(long baseMs) {
        this.minMs = baseMs;
        this.maxMs = 2 * baseMs;
        reset();
    }

    /** Jitter over [min, 2*min) is the fix for split votes. */
    public void reset() {
        deadline = System.currentTimeMillis()
                 + minMs + ThreadLocalRandom.current().nextLong(minMs);
    }

    public boolean expired() { return System.currentTimeMillis() >= deadline; }
    public long msUntilExpiry() { return deadline - System.currentTimeMillis(); }
}
```

```java
/**
 * RequestVote handler. The two clauses below are the whole election-safety
 * argument; get either wrong and the cluster loses committed entries without
 * any node being faulty.
 */
public record RequestVote(int term, String candidateId, int lastLogIndex, int lastLogTerm) {}
public record RequestVoteResponse(int term, boolean voteGranted) {}

public synchronized RequestVoteResponse onRequestVote(RequestVote req) throws IOException {
    // Rule 1: never vote twice in the same term. This is what stops two
    // leaders existing in one term.
    if (req.term() > currentTerm) {
        currentTerm = req.term();
        votedFor = null;
        role = Role.FOLLOWER;
        persist();                 // term bump MUST be durable before replying
    }
    if (req.term() < currentTerm) {
        return new RequestVoteResponse(currentTerm, false);  // stale candidate
    }
    if (votedFor != null && !votedFor.equals(req.candidateId())) {
        return new RequestVoteResponse(currentTerm, false);  // already voted
    }

    // Rule 2: only grant if the candidate's log is at least as up to date.
    // Without this, an elected leader may be missing committed entries.
    LogEntry myLast = log.get(log.size() - 1);
    boolean upToDate = req.lastLogTerm() > myLast.term()
            || (req.lastLogTerm() == myLast.term() && req.lastLogIndex() >= myLast.index());
    if (!upToDate) {
        return new RequestVoteResponse(currentTerm, false);
    }

    votedFor = req.candidateId();
    electionTimer.reset();          // we now wait for THEIR heartbeat
    persist();
    return new RequestVoteResponse(currentTerm, true);
}
```

**Residual risk:** the "up to date" comparison uses only `(lastTerm, lastIndex)`.
That is correct only because the log matching property holds — which depends on
correct truncation in step 3.

## 3. AppendEntries with Conflict Truncation

```java
public record AppendEntries(int term, String leaderId, int prevLogIndex, int prevLogTerm,
                            List<LogEntry> entries, int leaderCommit) {}
public record AppendEntriesResponse(int term, boolean success,
                                    int conflictIndex, int conflictTerm) {}

/**
 * THE most important method in Raft. Three things must happen:
 *  1. verify prevLogIndex/prevLogTerm match  (log matching)
 *  2. DELETE any existing conflicting suffix  (the step everyone forgets)
 *  3. append the new entries
 */
public synchronized AppendEntriesResponse onAppendEntries(AppendEntries req) throws IOException {
    if (req.term() < currentTerm) {
        return new AppendEntriesResponse(currentTerm, false, 0, 0);
    }
    if (req.term() > currentTerm) {
        currentTerm = req.term();
        votedFor = null;
    }
    role = Role.FOLLOWER;
    electionTimer.reset();          // any valid leader traffic defuses the timer

    // (1) Does our log actually contain prevLogIndex with prevLogTerm?
    if (prevLogIndexMismatch(req.prevLogIndex(), req.prevLogTerm())) {
        // Optimisation: return a HINT so the leader can skip the whole
        // conflicting range in one step instead of decrementing one index at
        // a time (the O(n) "backing up one index per round trip" trap).
        LogEntry at = (req.prevLogIndex() < log.size()) ? log.get(req.prevLogIndex()) : null;
        return new AppendEntriesResponse(currentTerm, false, req.prevLogIndex(),
                at == null ? -1 : at.term());
    }

    // (2) TRUNCATE the conflicting suffix. Skipping this is the classic bug:
    //    the node then holds two different entries at the same index and, if
    //    elected, silently overwrites committed history.
    for (int i = req.entries().size() - 1; i >= 0; i--) {
        LogEntry incoming = req.entries().get(i);
        int idx = req.prevLogIndex() + 1 + i;
        if (idx < log.size()) {
            LogEntry existing = log.get(idx);
            if (existing.term() == incoming.term() && existing.index() == incoming.index()) {
                continue;                      // already have it; idempotent retry
            }
            while (log.size() > idx) {
                log.remove(log.size() - 1);    // drop the conflicting tail
            }
        }
        log.add(new LogEntry(incoming.index(), incoming.term(), incoming.command()));
    }
    if (!req.entries().isEmpty()) persist();

    // (3) Advance commitIndex, but only up to the last NEW entry.
    int lastNew = req.prevLogIndex() + req.entries().size();
    if (req.leaderCommit() > commitIndex) {
        commitIndex = Math.min(req.leaderCommit(), lastNew);
    }
    return new AppendEntriesResponse(currentTerm, true, 0, 0);
}

private boolean prevLogIndexMismatch(int prevIndex, int prevTerm) {
    if (prevIndex < log.size() && log.get(prevIndex).term() == prevTerm) return false;
    return true;
}
```

**Residual risk:** this implementation has no snapshot support, so
`prevLogIndex` below the snapshot point fails permanently. You need
`InstallSnapshot` plus a sentinel representing "compacted through N".

## 4. The Commit Rule (why "current term" is load-bearing)

```java
/**
 * A leader may NOT advance commitIndex by counting replicated entries from a
 * PREVIOUS term. A previous-term entry could still be overwritten by a future
 * leader, so committing it early could lose it.
 *
 * Correct rule: advance commitIndex to the highest N such that
 *   - a majority of matchIndex >= N, AND
 *   - log[N].term == currentTerm
 *
 * Entries from earlier terms then commit implicitly, because once one
 * current-term entry commits, all preceding entries are committed by the log
 * matching property.
 */
public synchronized void advanceCommitIndex(java.util.Set<String> memberIds) {
    int quorum = memberIds.size() / 2 + 1;
    for (int n = log.size() - 1; n > commitIndex; n--) {
        if (log.get(n).term() != currentTerm) continue;   // <-- the load-bearing guard
        int count = 0;
        for (int idx : matchIndex.values()) if (idx >= n) count++;
        if (count >= quorum) { commitIndex = n; break; }
    }
}
```

**Residual risk:** it is tempting to "optimise" by dropping the term check. Do
not. The term check is the difference between a cluster that loses committed
data during a partition and one that does not.

## 5. ReadIndex (correct reads without lease-based staleness)

```java
/**
 * Linearizable reads WITHOUT trusting clocks.
 *
 * The naive options are both broken:
 *  - Read local state: may be stale (this node has not heard from the leader).
 *  - Leader lease read: correct only if clocks are synchronised and the lease
 *    has not expired. Clock skew silently turns this into split brain.
 *
 * ReadIndex instead: prove you were still leader at some instant AFTER the
 * client's request arrived, then read local state.
 *
 *   1. record readIndex = commitIndex
 *   2. broadcast a heartbeat with that readIndex
 *   3. once a MAJORITY of followers have acknowledged (proving no new leader
 *      has been elected since), read your local state
 */
public final class ReadIndexCoordinator {

    private volatile long pendingReadIndex = -1;
    private final java.util.Map<String, Long> followerAcks = new java.util.HashMap<>();

    public void onClientRead(CommitIndexSupplier commitIndex,
                             java.util.function.LongConsumer reply) {
        long idx = commitIndex.get();               // step 1
        pendingReadIndex = idx;
        followerAcks.clear();                       // step 2: broadcast heartbeat
    }

    /** Called when a follower acknowledges the ReadIndex heartbeat. */
    public synchronized void onAck(String followerId, long ackedIndex, int clusterSize) {
        if (ackedIndex < pendingReadIndex) return;   // stale ack, ignore
        followerAcks.merge(followerId, ackedIndex, Math::max);
        int quorum = clusterSize / 2 + 1;
        // leader counts as one ack (it is in touch with itself)
        if (followerAcks.size() + 1 >= quorum) {
            // Safe to read local state: no other leader could have been elected.
            long safeIndex = Math.min(pendingReadIndex, ackedIndex);
            pendingReadIndex = -1;
            followerAcks.clear();
        }
    }

    public interface CommitIndexSupplier { long get(); }
}
```

**Residual risk:** ReadIndex costs a quorum round trip on every read. That is
the honest price of linearizable reads, and it is why many systems accept
*stale* reads instead. Write that trade-off down rather than pretending
`local = consistent`.

## 6. Joint Consensus for Membership Change

```java
/**
 * Adding/removing a node in one step is UNSAFE: the old and new majorities can
 * be disjoint. Raft stages it through a joint configuration.
 *
 *   C_old,new = C_old ∪ C_new
 *   commit requires a majority in C_old AND a majority in C_new
 */
public record ClusterConfig(Set<String> voters, boolean joint, Set<String> oldVoters) {

    /** A config is "active" only if a majority of every constituent set agrees. */
    public boolean hasMajority(Set<String> ackingNodes) {
        if (!joint) {
            int q = voters.size() / 2 + 1;
            return ackingNodes.stream().filter(voters::contains).count() >= q;
        }
        // Joint: majority in the OLD set AND majority in the NEW set.
        int qOld = oldVoters.size() / 2 + 1;
        int qNew = voters.size() / 2 + 1;
        long oldAcks = ackingNodes.stream().filter(oldVoters::contains).count();
        long newAcks = ackingNodes.stream().filter(voters::contains).count();
        return oldAcks >= qOld && newAcks >= qNew;
    }

    /** One-shot change: enter joint first. Never skip straight to `new`. */
    public ClusterConfig enterJoint(Set<String> newVoters) {
        return new ClusterConfig(newVoters, true, Set.copyOf(voters));
    }

    /** Second step: leave joint once the joint config has been committed. */
    public ClusterConfig leaveJoint() {
        return new ClusterConfig(voters, false, Set.of());
    }
}
```

**Residual risk:** joint consensus requires the *configuration change itself* to
be committed under the joint rule, and a learner (non-voting) node must never
count toward any quorum. Both are easy to get subtly wrong.