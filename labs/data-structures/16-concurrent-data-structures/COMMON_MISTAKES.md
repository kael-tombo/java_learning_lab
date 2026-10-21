# Common Mistakes with Concurrent Data Structures

1. **Not handling ABA**: Use AtomicStampedReference
2. **Forgetting memory ordering**: Missing volatile/Atomic
3. **Deadlock in lock-based**: Incorrect lock ordering
4. **Race conditions**: Non-atomic check-then-act
5. **False sharing**: Adjacent fields in same cache line
6. **Busy waiting**: CAS loop without backoff
7. **Thread interference**: Non-thread-safe iterators
