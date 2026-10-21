# Refactoring: Performance

Before: Synchronous blocking I/O
After: Asynchronous with WebFlux or virtual threads

Before: Database queries in loop (N+1)
After: Batch queries or join and cache

Before: Inefficient serialization (Java serialization)
After: JSON (Jackson) or binary (Protobuf)
