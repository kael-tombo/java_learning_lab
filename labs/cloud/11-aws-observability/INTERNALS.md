# 11 — AWS Observability — Internals

## Internal Architecture

## Initialization Sequence

1. Configuration loader reads properties from environment and config files
2. Connection pool is initialized with configured min/max parameters
3. Service components are instantiated via dependency injection
4. Health checks register with the monitoring system
5. Metrics exporters begin collecting application data

## Threading Model

The service uses Java 21 virtual threads for I/O-bound operations and a fixed thread pool for CPU-bound tasks. Virtual threads provide massive concurrency with low overhead.

## Memory Layout

- **Heap**: Service objects, caches, request processing buffers
- **Off-Heap**: Direct byte buffers for high-performance I/O operations
- **Metaspace**: Class metadata for loaded classes and methods
- **Thread Stacks**: Configurable per-thread stack size for virtual threads

## Connection Management

- Connection pooling with configurable min/max connections
- Automatic health checking of idle connections at configurable intervals
- Graceful degradation when the pool is exhausted
- Connection timeout and retry with exponential backoff

## Error Propagation

The service follows a consistent error propagation pattern:
1. Method throws typed exception (checked or unchecked)
2. Controller layer catches and maps to appropriate HTTP status code
3. Global exception handler logs the error with full context
4. Metrics increment the error counter for alerting

## Caching Architecture

- L1 Cache: In-memory Caffeine cache for frequently accessed data
- L2 Cache: Distributed Redis cache for shared state across instances
- Cache-aside pattern: Load on cache miss, invalidate on write

