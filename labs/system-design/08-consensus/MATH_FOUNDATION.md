# Consensus - Math Foundation

## Quorum Intersection

For a cluster of `n` nodes, a majority quorum is:

```
  Q = floor(n / 2) + 1
```

**Theorem:** any two majorities intersect.
```
  |Q1| + |Q2| = 2 * (floor(n/2) + 1) > n
  => |Q1 ∩ Q2| >= |Q1| + |Q2| - n >= 1
```
This single inequality is the entire safety argument. Two disjoint majorities
would require `2Q > n` nodes but only `n` exist, so one of the elections
cannot be granted by a majority.

```
  n = 3 -> Q = 2    |  n = 5 -> Q = 3    |  n = 7 -> Q = 4
```

### Read quorum and R + W > N

For a quorum system with `N` replicas, `R` reads and `W` writes:

```
  guaranteed_fresh  <=>  R + W > N
  stale_read_possible <=>  R + W <= N
```

Worked cases (N = 5):

| R | W | R+W | Guarantee |
|---|---|-----|-----------|
| 1 | 5 | 6 | Linearizable, quorum write, slow reads |
| 3 | 3 | 6 | Balanced (typical strong read) |
| 5 | 1 | 6 | Fast writes, slowest reads |
| 3 | 2 | 5 | NOT guaranteed fresh (R+W == N) |
| 2 | 2 | 4 | Last-write-wins-ish; staleness possible |

Note `R + W = N` is the boundary and it does **not** guarantee freshness. This
is the off-by-one that produces "we set quorum read to 3 and still saw stale
data on a 5-node cluster" — the classic bug.

## Fault Tolerance and the 2f+1 Rule

```
  n >= 2f + 1  =>  tolerates f failures and still forms a majority
```

| Cluster | Max failures (f) | Availability with f failures | Quorum size |
|---------|-----------------|----------------------------|-------------|
| 3 | 1 | 1 - C(3,2)/8 = 62.5% | 2 |
| 5 | 2 | 1 - [C(5,3)+C(5,4)+C(5,5)]/32 = 1 - (10+5+1)/32 = 50% | 3 |
| 7 | 3 | 1 - (35+21+7+1)/128 = 50% | 4 |

Nodes must fail **independently**. The binomial model assumes independent
failure probabilities; correlated failures (one bad switch, one bad kernel,
one bad rack, one deploy) break it entirely. Real availability is therefore
governed by the *shared-fate groups* (racks, AZs), not by `n`.

```
  Effective n = nodes_per_AZ * AZs, and you lose min(AZ_faults, ...) units:
  you can only lose f_AZ * nodes_per_AZ before losing a majority of AZs.
```

## FLP: The Impossibility

Lamport, Fischer, Paterson (1985):

> If a system is completely asynchronous (no bound on message delay), and even
> one process can crash, then no deterministic algorithm can guarantee that
> every process eventually decides correctly.

Proof sketch: the adversary simply never delivers the message that would let
the system decide, while making it indistinguishable from a crash. Safety and
liveness cannot both be guaranteed.

**How Raft escapes:** it assumes bounded *eventual* synchrony — timeouts
eventually fire. So Raft guarantees **safety always**, and **liveness when the
network eventually stabilises**. Every practical claim about Raft should be
phrased with that qualifier attached.

## Randomised Consensus and Expected Progress

Raft's randomised election timeouts are randomised over `[T, 2T)`:

```
  Probability one specific node wins a given election
    p_win = 1 / n

  P(conflict) for two nodes timing out within one election round
    ~= sum over t in [0,T) of (dt/T) * (dt/T)
       = 1/3          (classic Raft analysis result)
```
Split votes happen; what matters is that the probability a round produces a
leader approaches 1 as `T >> network_delay`:

```
  P(no leader in k rounds) = (1 - (1 - 1/n)^k)^n  ->  0 quickly
```
If you set `T` close to typical network delay you get frequent conflicts and
election storms; if you set `T` very large you get slow failover. The tuning
target is `T >> p99 round-trip time`, typically 10x, and the resulting
failover time `T .. 2T` is your actual RTO for the consensus layer.

## Commit Latency

A Raft commit requires a majority round trip *of the current term*:

```
  commit_latency ~= RTT_p50_to_majority
  throughput      ~= (n / Q) * (1 / RTT)  entries per second

  n = 5, RTT = 2 ms, Q = 3:
    ~1,667 entries/s, and each commit costs >= 2 ms
```
Batching amortises this: commit latency is roughly constant per *batch*, not
per entry, so throughput scales with batch size until the batch no longer fits
in one network round trip.

### The leader is the bottleneck

```
  max_write_throughput = 1 / (RTT + append_time)
```
A single leader must append and replicate every entry. This is why Raft write
throughput does **not** improve past the leader's RTT, and why systems that
need more either shard the keyspace (multiple independent Raft groups) or use
a leaderless protocol. Horizontal scaling of consensus = more groups, not
bigger groups.

## Log Matching Property

Raft's log matching:
```
  If two logs contain an entry with the same index AND term,
  then all preceding entries are identical.
```
Proof obligation in the implementation:
```
  (a) AppendEntries carries prevLogIndex AND prevLogTerm
  (b) follower rejects if its term at prevLogIndex differs  -> "log mismatch"
  (c) follower TRUNCATES its suffix before appending
```
Violating (c) is the single most common Raft implementation bug. A follower
that appends without truncating can hold conflicting entries at the same
index, and if it is later elected leader it overwrites committed history.

### Election safety and the up-to-date rule

```
  Voter grants vote iff:
    (voted_for == null OR voted_for == candidate)
    AND candidate.log[last].term >= my.log[last].term
    AND (candidate.log[last].term > my.log[last].term
         OR candidate.log[last].index >= my.log[last].index)
```
Without the log-comparison clause, a leader with a *shorter* log could win and
discard committed entries — breaking safety while all nodes are "healthy".

## Snapshot Size Trade-off

```
  restart_work = log_growth_since_snapshot
  snapshot_cost = serialize(state) + transfer(state_size) + fsync

  optimal snapshot interval ~ sqrt(state_size / entry_rate)
```
Snapshot too often and you pay `state_size` repeatedly; too rarely and
restarts and log-compaction lag. The practical rule: snapshot when the log
exceeds a fixed size (e.g. 1M entries) OR exceeds the state size by a
threshold, whichever comes first.

## Membership Change: Why Direct Switch Fails

Changing `n` directly from 3 to 5 can produce two disjoint majorities during
the transition:

```
  old config C_old = {A,B,C},  majority = 2
  new config C_new = {A,B,D,E}, majority = 3

  {A,B} is a majority of C_old and {D,E} is 2/4 of C_new
  -> a leader elected under C_old and one under C_new can both exist
```
Raft solves it with **joint consensus**: an intermediate configuration
`C_old ∪ C_new` requiring majorities in *both*. Then:

```
  |majority(C_old) ∩ majority(C_old,new)| >= 1
  |majority(C_old,new) ∩ majority(C_new)| >= 1
  -> the two majorities always share at least one node
```
Any other scheme (one-at-a-time membership changes) is equivalent to the same
argument repeated `k` times, and is much easier to get wrong.