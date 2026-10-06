# Consensus - MINI PROJECT

## Project: A Raft Cluster You Can Kill in the Middle of Anything

**Time**: 12-16 hours

**Goal**: Implement enough of Raft to survive a partition, a crash, and a
restart — and to *prove* safety with tests that would catch the classic bugs.

### Scope

Implement in one package, single file per concern:

- `RaftServer` — state, durable log, `persist()` / `restore()`
- `ElectionTimer` — randomised `[T, 2T)` timeouts
- `onRequestVote` / `onAppendEntries`
- `advanceCommitIndex` with the current-term guard
- `ReadIndexCoordinator`
- `ClusterConfig` with joint consensus
- A simulated network with configurable delay, partition, and drop rates

### Step 1: Durable State (2 h)

`persist()` must fsync before any RPC response. Required tests:

- Crash (abandon the object) after `persist()`, restart, assert term and log
  match.
- Simulate a *partial* write by corrupting the state file. Assert `restore()`
  refuses to start rather than running with a half-loaded log. A node that
  starts with a partial log will silently violate safety.

### Step 2: Election (3 h)

Run a 3-node cluster with no partitions. Required:

- Exactly one leader emerges within ~2 election windows.
- The leader is the node with the most up-to-date log (inject a node with a
  longer log and verify it wins — this is the up-to-date rule).
- No node votes twice in the same term. Assert by counting `votedFor` writes
  per term across a 1,000-iteration fuzz.

### Step 3: Replication and Truncation (3 h)

Required tests, each of which corresponds to a specific bug:

| Test | Setup | Assert |
|------|-------|--------|
| Log matching | leader appends 10 entries, follower syncs | follower log is identical |
| **Truncation** | follower has divergent entries, leader overwrites | follower suffix deleted, not merged |
| Stale term | old-term AppendEntries | rejected, term unchanged |
| PrevLog mismatch | wrong prevLogIndex | rejected with conflict hint |
| **Commit rule** | replicate old-term entries, no current-term entry | commitIndex must NOT advance |

The truncation test and the commit-rule test are the two that catch the bugs
teams actually ship. Write them first.

### Step 4: Partition and Heal (2 h)

```
1. Isolate the leader (old leader still thinks it leads)
2. Elect a new leader among the remaining two (R = 2 of 2 excluding old, need 2)
3. Client writes entries on the new leader
4. Heal the partition
5. Assert the OLD leader's divergent entries are truncated and it becomes follower
6. Assert NO acknowledged write is lost  <-- the safety property
```

The final assertion is the whole point of the lab. Add a check that no write
acknowledged to a client before the partition is missing afterwards.

### Step 5: ReadIndex (1 h)

Assert that a client read after a write on a follower returns the written
value (because ReadIndex pins it to the leader's commit point). Then
deliberately break the implementation by skipping the majority wait and watch
the test fail with stale data. That failing test documents *why* ReadIndex
exists.

### Step 6: Membership Change (2 h)

Grow 3 -> 4 -> 5 via joint consensus. Assert:

- During the joint phase, no commit can be achieved with a majority of only
  old or only new voters.
- After `leaveJoint`, a single-node "old" majority can no longer commit.

Then attempt a *direct* 3 -> 5 switch and assert your test can find a
configuration where two disjoint majorities both exist. That is the bug joint
consensus prevents.

### Step 7: Chaos (1 h)

Run a 30-minute fuzz with random 0-200 ms delays, 5% packet drop, and random
node kills/restarts. Record:

- Leadership changes per minute (should be low when the network is stable).
- Unacknowledged writes (allowed).
- **Lost acknowledged writes** (must be zero — this is the safety invariant).
- Election time distribution vs. configured `T`.

### Deliverables

1. `RaftServer` with fsync-backed durability and a corruption test.
2. Election with a no-double-vote fuzz test.
3. Replication with explicit truncation and commit-rule tests.
4. Partition/heal test asserting zero lost acknowledged writes.
5. ReadIndex with the "removed the majority wait" negative test.
6. Joint consensus for 3->5 membership with the disjoint-majority demonstration.
7. A 30-minute chaos run with the four metrics above and a written conclusion.

### Stretch

- Add snapshot + `InstallSnapshot` so a lagging follower can catch up, and
  assert a restarted node with a truncated log recovers correct state.
- Add a linearizability checker (record client operations with real timestamps
  and verify no overlapping ops appear out of order in the log).