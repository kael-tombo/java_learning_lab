# Consensus - Vision

## Why This Lab Exists
Consensus is the most expensive primitive in distributed systems, and most
people overuse it. It is required when *replicas must agree on an ordered
history of facts* and a split brain would corrupt irreversible state. It is not
required to serve a stale page, count a click, or rate-limit a user. This lab
exists so you can tell the difference before you pay for a Raft cluster.

## The Mental Model
Consensus is a **safety** property bought with **availability**, and the price
is stated by FLP:

> In an asynchronous system with even one process that can crash, no
> deterministic algorithm can guarantee both safety and liveness.

Every real system therefore weakens *liveness* (it uses timeouts, which
requires clocks) and keeps *safety*. The engineering consequence: **a partition
must never produce two leaders that both accept writes**.

## Why Quorums Work
The whole thing reduces to one combinatorial fact:

```
  any two quorums of size floor(n/2)+1 MUST intersect
```

That intersection is why two leaders cannot commit conflicting entries at the
same log index: the second leader's election must be rejected by someone in
the intersection who has already seen the first leader's entry. Everything
else — terms, log matching, election restriction — is machinery for finding
and exploiting that intersection.

## What You Should Be able To Do
- State the liveness condition and explain why 2f+1 tolerates f failures.
- Implement Raft's leader election and AppendEntries with conflict truncation.
- Explain log matching, the commit rule (majority of *current-term* entries),
  and why that word "current-term" is load-bearing.
- Explain the election restriction (up-to-date logs win) and what happens
  without it.
- Compare Raft, Paxos, and Zab on understandability and operational profile.
- Explain joint consensus for membership change and why a direct switch is
  unsafe.
- Choose ReadIndex over lease reads when clocks are unreliable, and say why.

## The Anti-Goals
- Not "run Raft yourself for everything". Use a boring managed store.
- Not lease reads with unsynchronised clocks. That is a split brain with extra
  steps.
- Not membership change in two phases. Use joint consensus.

## Success Criteria
You can implement leader election and log replication from scratch, prove the
log-matching property holds in a test, and explain in one paragraph why the
system is safe despite every component being fallible.

## How To Use This Lab
1. `THEORY.md` for Raft, Paxos, Zab, membership, snapshots.
2. `MATH_FOUNDATION.md` for quorum intersection, FLP, availability, commit
   latency.
3. `CODE_DEEP_DIVE.md` for the election timer, AppendEntries, ReadIndex.
4. `MINI_PROJECT.md` to build a Raft cluster you can kill nodes in.
5. `REAL_WORLD_PROJECT.md` to run consensus in a real replicated store.