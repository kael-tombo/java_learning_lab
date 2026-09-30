# ADVANCED GUIDE: Raft Distributed Consensus from Scratch & Formal Verification
## Lab 17 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Mathematical Quorum & Split-Brain Invariants

In distributed consensus (Raft, Paxos):
- A cluster consists of $2F + 1$ nodes, allowing it to survive $F$ node failures.
- **Quorum Requirement**: Any decision (leader election, log commit) requires acknowledgement from a strict majority:
  $$\text{Quorum Size} = \left\lfloor \frac{N}{2} \right\rfloor + 1$$
- **The Pigeonhole Principle Invariant**:
  Any two quorums in a cluster of size $N$ must overlap by at least **one common node**:
  $$Q_1 \cap Q_2 \neq \emptyset$$
  Because $Q_1$ and $Q_2$ overlap, the overlapping node guarantees that conflicting leaders cannot be elected and committed logs cannot be overwritten.

---

## 2. Minimal Java Raft Consensus State Machine

```java
package com.learning.production.lab17;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Core Raft Consensus Protocol state machine implementation.
 * Handles Leader Election, Randomized Heartbeat Timers, and Split-Brain Defense.
 */
public class RaftNode {
    public enum Role { FOLLOWER, CANDIDATE, LEADER }

    private final String nodeId;
    private final List<String> clusterPeers;
    private final int quorumSize;

    private Role currentRole = Role.FOLLOWER;
    private long currentTerm = 0;
    private String votedFor = null;
    private long lastHeartbeatTimestamp;

    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    public record RequestVoteArgs(long term, String candidateId, long lastLogIndex, long lastLogTerm) {}
    public record RequestVoteReply(long term, boolean voteGranted) {}

    public record AppendEntriesArgs(long term, String leaderId, long prevLogIndex, long prevLogTerm, List<String> entries, long leaderCommit) {}
    public record AppendEntriesReply(long term, boolean success) {}

    public RaftNode(String nodeId, List<String> allNodes) {
        this.nodeId = nodeId;
        this.clusterPeers = new ArrayList<>(allNodes);
        this.clusterPeers.remove(nodeId);
        this.quorumSize = (allNodes.size() / 2) + 1;
        this.lastHeartbeatTimestamp = System.currentTimeMillis();
        startElectionTimeoutMonitor();
    }

    private void startElectionTimeoutMonitor() {
        // Randomized election timeout between 150ms and 300ms to avoid split votes
        long timeoutMs = 150 + ThreadLocalRandom.current().nextInt(150);
        scheduler.scheduleAtFixedRate(() -> {
            synchronized (this) {
                if (currentRole != Role.LEADER && (System.currentTimeMillis() - lastHeartbeatTimestamp > timeoutMs)) {
                    startElection();
                }
            }
        }, timeoutMs, timeoutMs, TimeUnit.MILLISECONDS);
    }

    private synchronized void startElection() {
        currentRole = Role.CANDIDATE;
        currentTerm++;
        votedFor = nodeId; // Vote for self
        lastHeartbeatTimestamp = System.currentTimeMillis();

        AtomicInteger votesGranted = new AtomicInteger(1); // 1 vote from self
        System.out.printf("[%s] Election started for Term %d. Seeking quorum of %d...%n", nodeId, currentTerm, quorumSize);

        for (String peer : clusterPeers) {
            CompletableFuture.supplyAsync(() -> sendRequestVoteRpc(peer, new RequestVoteArgs(currentTerm, nodeId, 0, 0)))
                    .thenAccept(reply -> {
                        synchronized (this) {
                            if (reply.term() > currentTerm) {
                                stepDown(reply.term());
                                return;
                            }
                            if (currentRole == Role.CANDIDATE && reply.voteGranted() && reply.term() == currentTerm) {
                                if (votesGranted.incrementAndGet() >= quorumSize) {
                                    becomeLeader();
                                }
                            }
                        }
                    });
        }
    }

    private synchronized void becomeLeader() {
        if (currentRole != Role.CANDIDATE) return;
        currentRole = Role.LEADER;
        System.out.printf("[%s] *** QUORUM ACHIEVED. PROMOTED TO LEADER FOR TERM %d ***%n", nodeId, currentTerm);
        startHeartbeatEmitter();
    }

    private void startHeartbeatEmitter() {
        scheduler.scheduleAtFixedRate(() -> {
            synchronized (this) {
                if (currentRole != Role.LEADER) return;
                for (String peer : clusterPeers) {
                    sendAppendEntriesRpc(peer, new AppendEntriesArgs(currentTerm, nodeId, 0, 0, List.of(), 0));
                }
            }
        }, 0, 50, TimeUnit.MILLISECONDS); // Heartbeat every 50ms
    }

    public synchronized RequestVoteReply handleRequestVote(RequestVoteArgs args) {
        if (args.term() > currentTerm) {
            stepDown(args.term());
        }

        boolean canVote = (votedFor == null || votedFor.equals(args.candidateId()));
        if (args.term() == currentTerm && canVote) {
            votedFor = args.candidateId();
            lastHeartbeatTimestamp = System.currentTimeMillis();
            return new RequestVoteReply(currentTerm, true);
        }
        return new RequestVoteReply(currentTerm, false);
    }

    public synchronized AppendEntriesReply handleAppendEntries(AppendEntriesArgs args) {
        if (args.term() > currentTerm) {
            stepDown(args.term());
        }
        if (args.term() < currentTerm) {
            return new AppendEntriesReply(currentTerm, false); // Reject stale leader
        }

        // Valid leader recognized
        lastHeartbeatTimestamp = System.currentTimeMillis();
        if (currentRole == Role.CANDIDATE) {
            currentRole = Role.FOLLOWER;
        }
        return new AppendEntriesReply(currentTerm, true);
    }

    private void stepDown(long newTerm) {
        currentTerm = newTerm;
        currentRole = Role.FOLLOWER;
        votedFor = null;
    }

    // Mock RPC transport
    private RequestVoteReply sendRequestVoteRpc(String peer, RequestVoteArgs args) { return new RequestVoteReply(args.term(), true); }
    private AppendEntriesReply sendAppendEntriesRpc(String peer, AppendEntriesArgs args) { return new AppendEntriesReply(args.term(), true); }
}
```
