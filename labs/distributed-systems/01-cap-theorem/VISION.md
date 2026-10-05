# CAP Theorem - Vision

## The Big Picture
The CAP theorem is the most misquoted result in distributed systems. Its actual claim is
narrow and precise: when a network partition occurs, a distributed data store cannot
simultaneously guarantee linearizable consistency and total availability. That is it.
There is no "pick two of three" shopping list to browse.

## Why This Matters
Every architectural decision in a distributed system is a CAP decision in disguise:
- A banking ledger that must never serve stale balances is choosing C over A.
- A shopping cart that must stay reachable is choosing A over C.
- A partition-tolerant cluster is not choosing; it is accepting P and living with the
  consequences on every request path.

## The Vision for This Lab
This lab builds CAP as an *experiment*, not a slogan. You will build a multi-node store,
inject real partitions, and observe each consistency choice fail in the direction the
theorem predicts. Understanding stops being theoretical once you have seen a stale read
survive a heal.

## Learning Philosophy
1. **Prove, do not recite** — every claim in this lab is demonstrated in code
2. **Partitions first** — CAP is only observable when the network is broken
3. **Name the trade** — state which guarantee you gave up, in writing
4. **Latency is a guarantee** — treat consistency choices as latency budgets

## Future Path
- 02-consistency-models — the granularity ladder from linearizable to eventual
- 07-replication-strategies — where C, A, and P actually get configured
- 03-distributed-consensus — how groups buy C back at the cost of latency

## Success Metrics
You have mastered CAP when you can:
- [ ] Restate the theorem without the "pick two" framing
- [ ] Inject a partition and record the stale read in a test
- [ ] Justify CP vs AP for three different product features
- [ ] Explain why PACELC extends the theorem usefully

## The Distributed Mindset
> Partitions are not failures. Partitions are the *normal* state of a network.
Design for the partition, then decide what you are willing to lie about.