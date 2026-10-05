# Distributed Consensus - Vision

## The Big Picture
Consensus is the machinery that lets independent machines agree on one value while some of
them are crashed, slow, or lying. Paxos got there first; Raft made it teachable. Neither is
optional — every strongly consistent replicated store you will ever call is running a
consensus protocol underneath, usually wearing a disguise.

## Why This Matters
Consensus is where the hard parts of distributed systems actually live: leader election,
log replication, commit rules, and safety under arbitrary message reordering. It is also the
only way to make a cluster agree on something *and know they agree*. Everything else —
replication, leader/follower, quorum reads — is downstream of consensus.

## The Vision for This Lab
This lab implements Raft from the paper's structure: persistent log, election timeout, term
numbers, commit index only advancing by majority, and the leader-completeness property that
makes leadership unique. You will not implement Paxos's multi-phase prepare/accept and only
get it right once; you will implement Raft twice and debug it twice, which is the actual
skill.

## Learning Philosophy
1. **Invariants first** — write the safety properties before the code
2. **Terms are a logical clock** — every rejection carries a term, learn to read it
3. **Majority is the unit of progress** — nothing commits without it
4. **Deterministic simulation** — no wall-clock timers in tests, ever

## Future Path
- 14-distributed-locks — consensus-backed mutual exclusion
- 10-time-ordering — logical clocks underpin the term mechanism
- 17-distributed-filesystems — Raft powers modern metadata services

## Success Metrics
You have mastered consensus when you can:
- [ ] Implement Raft election and log replication with real persistence
- [ ] Explain why commit index only advances on majority ack
- [ ] Reproduce and fix a stale-read bug during leader failover
- [ ] State the Leader Completeness and Log Matching properties from memory

## The Distributed Mindset
> Consensus buys agreement by paying latency. The question is never "is consensus safe" but
"how many round trips of latency will we pay, and have we written that number down?"