# Code Deep Dive — Time Ordering

## 1. EventClock Interface

The EventClock interface defines the contract for all clock implementations. It provides methods for ticking (advancing time on internal events), sending (preparing a timestamp for messages), and receiving (updating time from incoming messages).

`java
public interface EventClock<T> {
    T tick();
    T send();
    void receive(T other, long currentTimeMillis);
}
`

### Design Decisions
- **Generic type T** allows different timestamp representations
- **Separation of tick and send** allows different semantics
- **currentTimeMillis parameter** allows hybrid clocks to incorporate physical time

## 2. LamportClock Implementation

The LamportClock maintains a single integer counter. It is the simplest logical clock but provides only total ordering without causality information.

### Key Methods
- **tick()**: Increments counter by 1 and returns the new value
- **send()**: Increments counter by 1 and returns the new value
- **receive()**: Takes the sender's timestamp, computes max(local, received) + 1

### Edge Cases
- **Initial state**: Counter starts at 0
- **Concurrent events**: Lamport clocks can't detect concurrency
- **Message loss**: Lost messages cause clock divergence

## 3. VectorClock Implementation

VectorClock maintains an array of integers, one entry per known process.

### Key Methods
- **tick()**: Increments own entry and returns a copy
- **send()**: Increments own entry and returns a copy
- **receive()**: Element-wise max, then increment own entry

### Comparison Logic
- **happensBefore(v1, v2)**: v1[i] <= v2[i] for all i and v1 != v2
- **concurrent(v1, v2)**: Neither happensBefore

## 4. HybridLogicalClock Implementation

HLC combines physical time (milliseconds) with a logical counter.

### tick() Logic
1. Get current physical time
2. If > stored: update, reset counter
3. If == stored: increment counter

### receive() Logic
1. Extract sender's times
2. Take max of current, local, received
3. Handle tie-breaking with logical counters

## 5. CausalBroadcast Implementation

### Delivery Algorithm
1. Each process maintains a vector clock and message queue
2. On message arrival, check causal delivery condition
3. Deliver if all causally preceding messages delivered
4. Buffer otherwise, re-check after each delivery

## 6. Testing Strategy

### Unit Tests
- Verify monotonicity for each clock type
- Test causality tracking with simple sequences

### Integration Tests
- Multi-threaded scenarios with multiple processes
- Verify causal broadcast ordering
