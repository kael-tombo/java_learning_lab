# Theory of Distributed Time Ordering

## 1. The Problem of Time in Distributed Systems

In a centralized system, a single physical clock provides a total order of events. In distributed systems, each node has its own clock, and these clocks drift relative to each other. Even with Network Time Protocol (NTP), clock skew is unavoidable. This creates fundamental challenges:

- **Event Ordering**: Without synchronized clocks, determining which event happened first across nodes is impossible with physical time alone.
- **Causality**: Understanding which events causally affect others is critical for correctness in distributed databases, version control, and replicated state machines.
- **Consistency**: Strong consistency models require establishing a global order of operations.

### The Happens-Before Relation

Lamport defined the happens-before relation (denoted ->) with two rules:
1. If events a and b occur on the same process and a occurs before b, then a -> b
2. If event a is the sending of a message and event b is the receipt of that message, then a -> b
3. The relation is transitive: if a -> b and b -> c, then a -> c

Two events are concurrent (a || b) if neither a -> b nor b -> a.

## 2. Lamport Logical Clocks

Lamport clocks assign a timestamp to each event such that if a -> b, then C(a) < C(b).

### Algorithm
- Each process i maintains a counter C_i
- Before each event: C_i = C_i + 1
- When sending message m: include C_i in the message
- When receiving message m with timestamp t: C_i = max(C_i, t) + 1

### Limitations
- The converse is NOT guaranteed: C(a) < C(b) does NOT imply a -> b
- Lamport clocks provide total ordering but lose causality information

## 3. Vector Clocks

Vector clocks overcome Lamport clock limitations by maintaining a vector of timestamps, one entry per process.

### Algorithm
- Each process i maintains a vector V_i[1..n]
- Before an event: V_i[i] = V_i[i] + 1
- When sending message m: include V_i in the message
- When receiving message m with vector V: V_i[j] = max(V_i[j], V[j]) for all j, then V_i[i] = V_i[i] + 1

### Comparison Rules
- V_a <= V_b iff V_a[i] <= V_b[i] for all i
- V_a < V_b iff V_a <= V_b and V_a != V_b
- Events are concurrent if neither V_a <= V_b nor V_b <= V_a

## 4. Hybrid Logical Clocks (HLC)

HLC combines physical time (from NTP) with logical time to provide both wall-clock correlation and causality tracking.

### Properties
- HLC values are close to physical time (within bounded error)
- HLC is monotonically increasing
- HLC preserves causality (if a -> b, then HLC(a) < HLC(b))
- HLC values can be compared across nodes with reasonable physical time correlation

## 5. Causal Ordering

Causal broadcast ensures messages are delivered in an order consistent with causality: if a message m1 causally precedes m2, all processes deliver m1 before m2.

### Causal Delivery Conditions
- If send(m1) -> send(m2), then deliver(m1) -> deliver(m2)
- Concurrent messages can be delivered in any order

## 6. Version Vectors and Dotted Version Vectors

Version vectors are used in distributed storage systems to track updates to replicated data. Each replica maintains a vector of version counters.

Dotted version vectors extend this by adding a dot (a single event identifier) to distinguish between state and event tracking.

## 7. Clock Synchronization Protocols

### NTP (Network Time Protocol)
- Hierarchical architecture with stratum levels
- Uses multiple time sources and statistical filtering
- Typical accuracy: 1-50ms on LAN, 10-100ms on WAN

### PTP (Precision Time Protocol, IEEE 1588)
- Hardware timestamping for microsecond accuracy
- Used in financial trading and industrial control
- Requires specialized network hardware

## 8. Applications

- **Distributed Databases**: Amazon Dynamo uses vector clocks for conflict resolution
- **CRDTs**: Conflict-free Replicated Data Types rely on causal ordering
- **Event Sourcing**: Event stores use logical timestamps for ordering
- **Distributed Consensus**: Paxos and Raft use logical time for leader election
- **Debugging**: Time ordering aids in debugging distributed system failures
