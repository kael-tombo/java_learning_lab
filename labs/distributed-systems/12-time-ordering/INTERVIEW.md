# Time Ordering (Duplicate Lab) - Interview Preparation

> Key interview questions about time and ordering in distributed systems.

---

## Core Interview Questions

### Q1: What are logical clocks and why are they needed?
**Answer**: Physical clocks drift and cannot be perfectly synchronized. Logical clocks (Lamport, Vector) provide event ordering without synchronized clocks. Lamport clocks capture happens-before relationship: if A happens before B, then Lamport(A) < Lamport(B). Not sufficient for concurrent detection.

### Q2: How do you implement a Lamport clock?
**Answer**: Each process maintains counter. On internal event: increment. On send: increment, attach to message. On receive: update to max(local, received) + 1. Total ordering requires process ID tiebreaker. No concurrent event detection.

### Q3: What is causal consistency and how is it implemented?
**Answer**: Operations causally related must be seen in same order. Concurrent operations can be seen in any order. Implemented using vector clocks: each process tracks all processes' counters. If vector A <= vector B element-wise, A happened before B. Otherwise, they're concurrent.

### Q4: What is the problem with using NTP for ordering?
**Answer**: NTP has unbounded error (can be 10-100ms). Clock skew can cause non-monotonic time. Not safe for ordering decisions in distributed databases. Google's TrueTime solves this by bounding the error.

### Q5: How does CockroachDB use Hybrid Logical Clocks (HLC)?
**Answer**: HLC = max(physical, physical_last, logical_last). Acts like physical clock but preserves causal ordering. CockroachDB uses HLC timestamps for serializable snapshot isolation. Provides both wall time approximation and causality.

## Company-Specific Focus

| Company | Time/Ordering Focus |
|---------|--------------------|
| Google | "TrueTime API for external consistency" |
| Amazon | "Vector clocks for DynamoDB conflict detection" |
| CockroachDB | "HLC for distributed transactions" |
| Redis | "Replication offset for ordering" |

## LeetCode Connections

| Problem | # | Ordering Concept |
|---------|---|-----------------|
| Merge Intervals | 56 | Clock merge semantics |
| Time Based KV Store | 981 | Version queries |
| Alien Dictionary | 269 | Custom ordering |
| Task Scheduler | 621 | Priority ordering |

## System Design Connections

- **Design a Distributed Database**: Choose clock mechanism
- **Design a Causality Tracker**: Vector clocks
- **Design a Global Timeline**: TrueTime-like API
- **Design a Version Manager**: Hybrid logical clocks

> **Key Insight**: Clock synchronization is fundamental to distributed systems. Know at least one implementation of logical and hybrid clocks in detail.