# Distributed File Systems - Vision

## The Big Picture
A distributed file system must answer three questions for every operation: where does the data
live, who is allowed to read it, and what happens when a third of the machines vanish
mid-write. Everything else is metadata, caching, and performance.

## Why This Matters
File systems expose the hardest distributed problems without hiding them: large sequential
I/O, partial failure, mutable and immutable objects, and consistency for directory
operations that nobody benchmarks. The failures are also the least recoverable, because
users notice.

## The Vision for This Lab
This lab builds the two halves separately and then together: erasure coding for durability
without triple storage, and a metadata layer with a consensus-backed namespace. Then it
attacks both with node loss and concurrent renames.

## Learning Philosophy
1. Durability is a code, not a flag — write the encoding math
2. Metadata consistency and data durability are separate problems
3. Cache invalidation in a file system is a correctness problem
4. Every design has a write amplification cost; know yours

## Future Path
- 17-distributed-filesystems — deeper coverage of specific systems
- 03-distributed-consensus — metadata services are consensus services
- 07-replication-strategies — replication underlies object storage

## Success Metrics
You have mastered distributed file systems when you can:
- [ ] Implement Reed-Solomon-style erasure coding and reconstruct from any k of n
- [ ] Explain the durability/space/bandwidth tradeoff numerically
- [ ] Build a metadata namespace with atomic rename and concurrent-op safety
- [ ] Recover a file after losing more replicas than any single copy

## The Distributed Mindset
> A file system that cannot survive losing a third of its disks is not durable, it is
persistent. Durability is a number you can compute: given the failure rate of your disks, how
long until you lose too many?