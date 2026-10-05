# Replication Strategies - Vision

## The Big Picture
Replication is copying data so that one node's failure is not the system's failure. The
strategy you pick — leader/follower, multi-leader, quorum, or gossip — decides who accepts
writes, how stale a read may be, and what happens when two nodes disagree.

## Why This Matters
Replication is where availability is bought. It also decides the failure modes you will
debug at 3am: split brain, silent divergence, or a follower set that is stale enough to lose
acknowledged writes on failover.

## The Vision for This Lab
This lab starts with single-leader replication and works outward, measuring as it goes. The
focal question is not "does it replicate" but "after the leader dies, what do I have, and
what did I promise?"

## Learning Philosophy
1. Acknowledge after durability, not after memory
2. Sync vs async is a durability/latency dial — set it explicitly per data class
3. Read repair fixes reads, not writes — know which one you are doing
4. Quorums are arithmetic: R + W > N or you have not proven anything

## Future Path
- 03-distributed-consensus — where leader election and log safety actually live
- 12-distributed-failure-detection — detecting the follower that stopped replicating
- 17-distributed-filesystems — replication under erasure coding

## Success Metrics
You have mastered replication when you can:
- [ ] Implement sync and async leader/follower and measure the latency difference
- [ ] Demonstrate split brain and explain how fencing prevents it
- [ ] Prove quorum reads and writes with a partition
- [ ] State exactly what data you lose when an async follower is promoted

## The Distributed Mindset
> Replication is a promise made on behalf of a machine you cannot see. Define the promise in
terms of what survives its death, then test that definition rather than your assumption.