# Architecture of Time Ordering Systems

## 1. System Overview

### Layer 1: Clock Layer
- Basic time-keeping primitive
- LamportClock, VectorClock, HybridLogicalClock
- Interface: tick(), send(), receive()

### Layer 2: Ordering Layer
- Establishes event ordering from timestamps
- Detects causality and concurrency

### Layer 3: Communication Layer
- Attaches timestamps to messages
- Interprets timestamps on delivery

### Layer 4: Application Layer
- Uses ordering for application logic
- Key-value store, event log, distributed counter

## 2. Component Diagram
`
Application Layer (KV Store, Event Log, Counters)
        |
Ordering Layer (Causal Broadcast, Version Vectors)
        |
Clock Layer (Lamport, Vector, HLC)
        |
Communication Layer (TCP, Serialization)
`

## 3. Clock Selection Guide
| Requirement | Recommended Clock | Rationale |
|-------------|------------------|-----------|
| Total order, low overhead | Lamport | O(1) storage |
| Causality, small cluster | Vector (Array) | O(n) storage |
| Causality, large cluster | Vector (Map) | O(k) storage |
| Wall-clock + causality | HLC | O(1) storage |
| Dynamic membership | Interval Tree | Adaptive |
| Conflict detection | Version Vector | Per-key tracking |
