# Interview Questions: Memory Model

## Company-Specific Focus

### Google
- Java Memory Model (JMM): happens-before relationships, visibility guarantees
- Volatile: semantics, ordering guarantees, read/write reordering restrictions
- Synchronized: mutual exclusion and memory visibility guarantees

### Microsoft
- JMM vs .NET memory model: release/acquire semantics, volatile differences
- JMM: happens-before, sequential consistency for data-race-free programs

### Amazon
- Double-checked locking: the pattern, the bug, the fix with volatile
- Final fields and their initialization safety guarantee
- Memory barriers on ARM vs x86: how JMM maps to hardware

### Meta
- Data race vs race condition: what JMM prevents and what it doesn't
- Reordering: compiler, JIT, and CPU reordering of instructions
- Atomicity: when operations are atomic on primitive types

### Apple
- JMM on ARM processors: weaker memory ordering than x86
- Final field semantics: safe publication of immutable objects
- Effective immutability for thread safety without synchronization

### Oracle
- JLS 17: Threads and Locks — the formal JMM specification
- JSR 133: the Java Memory Model and Thread Specification
- Causality: what formal guarantees the JMM gives
- The happens-before partial order definition

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems - memory model is foundational for concurrency) |
| 1114 Print in Order | Easy | Google, Apple | Visibility of ready flag |
| 1115 Print FooBar Alternately | Medium | Amazon, Microsoft | Volatile/atomic for turn control |
| 1116 Print Zero Even Odd | Medium | Google, Apple | Sequential consistency |

## Real Production Scenarios
- **LinkedIn**: ThreadLocal + volatile bug causing stale user session data across requests
- **Twitter**: A data race in a cache caused some servers to serve stale data for up to 30 seconds
- **Airbnb**: Double-checked locking on a configuration cache — missing volatile caused NPE

## Interview Patterns & Tips
- **Happens-before**: If one action happens-before another, the first is visible and ordered before the second
- **Volatile**: Provides visibility for single reads/writes but not compound actions
- **Safe publication**: Use final fields, volatile, or proper locking for safe object publishing

## Deep Dive Questions
- **Reordering**: What reordering does the JVM allow? What does volatile prevent?
- **Memory barriers**: How is volatile implemented on x86 vs ARM?
- **Final fields**: How does the JMM guarantee that final fields are visible after construction?
- **JIT**: Can the JIT remove a volatile read? (No, but it can optimize it in some cases)
- **Java 9+**: VarHandle and memory ordering modes: acquire/release/opaque/plain