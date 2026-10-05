# Distributed Locks (Deep) - Vision

## The Big Picture
Deep locking is about proving a negative: that no other holder exists and that you will keep
knowing that. That proof requires a store with a linearizable compare-and-set, an expiry whose
semantics you understand, and — the part everyone forgets — a way for the *resource* to reject
a holder that has already lost.

## Why This Matters
A lock that provides mutual exclusion but not *safety* is worse than no lock, because it
converts a loud failure into silent corruption. Deep locking is the discipline of making the
resource the final authority.

## The Vision for This Lab
This lab compares three backends on their actual semantics — ZooKeeper, etcd, and Redis — and
builds each lock to the same contract, then subjects all three to the same adversarial suite:
pause, partition, clock skew, and lost renewal.

## Learning Philosophy
1. Safety over liveness — a lock that may be wrong is worse than a lock that blocks
2. The resource must validate; the client cannot police itself
3. Measure detection latency, then set TTL from it
4. If a uniqueness constraint can do it, do not lock

## Future Path
- 03-distributed-consensus — the machinery underneath etcd and ZooKeeper
- 11-distributed-locking — the intro course
- 19-distributed-scheduling — where locks are usually the wrong tool

## Success Metrics
You have mastered deep distributed locks when you can:
- [ ] Implement the same lock contract against three stores
- [ ] Explain ZooKeeper ephemeral znodes vs etcd leases vs Redis TTL precisely
- [ ] Demonstrate the paused-holder corruption and fence it
- [ ] Replace every lock you can with a constraint, and justify what remains

## The Distributed Mindset
> A lock tells you what others are doing. A fencing token tells the resource what you are
allowed to do. Build the second one, and your first one stops being a correctness risk.