# Distributed Transactions - Vision

## The Big Picture
A distributed transaction spans resources that cannot join one local ACID transaction. The
question is not "how do I make it atomic" — under partitions, that is often impossible — it
is "what is my atomic *substitution*, and what does it cost when it fails?"

## Why This Matters
Every business process that touches a database and a message broker has this problem. The
naive answer — 2PC across everything — works, blocks, and eventually produces a coordinator
that holds locks during an outage. The real answers are SAGA, the transactional outbox, and
idempotent consumers, and choosing correctly is a per-process business decision.

## The Vision for This Lab
This lab implements the mechanisms and then the patterns. You will build 2PC and watch it
block, build a SAGA and watch it compensate imperfectly, and build an outbox and discover
it makes most of your SAGA problems disappear. That progression is the point.

## Learning Philosophy
1. **Atomicity is a business concept** — "all or nothing" must be defined by the domain
2. **Compensation is not rollback** — a refund is not an undo of a charge
3. **Idempotency is the prerequisite** — every retry-safe operation gets a key
4. **Prefer the boring pattern** — outbox before clever orchestration

## Future Path
- 18-distributed-queues — the transport half of the outbox pattern
- 06-distributed-messaging — at-least-once delivery and what it forces on consumers
- 14-design-payment-system — where the trade-offs are unforgiving

## Success Metrics
You have mastered distributed transactions when you can:
- [ ] Explain when 2PC blocks and why that is worse than failing
- [ ] Implement a SAGA with real compensations and a persistent state machine
- [ ] Implement an outbox with relay and prove no event is lost
- [ ] Explain why compensation cannot undo an already-visible side effect

## The Distributed Mindset
> There is no global transaction. There is only a sequence of local ones plus the business
rule for what to do when one of them fails after the fact. Write that rule down first.