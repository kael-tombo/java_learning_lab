# Distributed Locking - Vision

## The Big Picture
A distributed lock is a lease: a claim that expires. The interesting part is not acquiring
it — it is what happens when the holder pauses, partitions, or is slow, and the lease it no
longer owns is still being used to protect a resource someone else now holds.

## Why This Matters
Locks are the escape hatch developers reach for when a distributed invariant is hard, and
they are the source of the most damaging bug class in this lab: two clients both believing
they hold the lock, one of them acting on a resource that was reassigned. That is not a
correctness bug you can detect later; it is corrupt data.

## The Vision for This Lab
This lab builds locks, then tries to break them, and concludes with the design pattern that
actually works: fencing tokens. The lab's real output is the judgement about when *not* to
use a lock at all.

## Learning Philosophy
1. A lock is a lease, and a lease can expire while you still hold it
2. Pause is worse than crash — a dead holder stops; a paused one keeps writing
3. Fencing tokens turn a lock into a monotonic guard the resource can enforce
4. Prefer uniqueness constraints and idempotency over locks

## Future Path
- 14-distributed-locks — the production-grade implementation set
- 03-distributed-consensus — etcd and ZooKeeper use consensus underneath
- 09-distributed-id-generation — monotonic tokens are a specialised ID

## Success Metrics
You have mastered distributed locking when you can:
- [ ] Implement a lease-based lock with expiry and renewal
- [ ] Reproduce the paused-client double-entry corruption
- [ ] Implement and verify a fencing token end to end
- [ ] Argue convincingly for replacing three of your four lock uses with something else

## The Distributed Mindset
> You cannot stop a process from acting after you have taken its lock away. The only defence
is a token that increases, that the resource validates, and that an old holder cannot forge.