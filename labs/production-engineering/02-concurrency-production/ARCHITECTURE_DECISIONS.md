# ARCHITECTURE DECISIONS: Concurrency Model Selection
## Lab 02 | Production Engineering Academy

---

## ADR-01: Platform Threads vs Virtual Threads vs Reactive

### Status: Reference Guide

### Context
New Java service, Java 21 available. Service is I/O-bound: REST calls to 3 downstream services, 2 DB queries per request. Expected: 5,000 concurrent requests.

### Options Analysis

| Criterion | Platform Threads | Virtual Threads | Reactive (WebFlux) |
|-----------|-----------------|-----------------|-------------------|
| Code complexity | Low | Low | High |
| Debugging | Easy stack traces | Easy stack traces | Complex (operator chains) |
| Memory per 5000 users | 5GB (1MB/thread) | ~50MB (10KB/VT) | ~50MB |
| Throughput (I/O-bound) | Limited by threads | Excellent | Excellent |
| Throughput (CPU-bound) | Excellent | No benefit | No benefit |
| Library compatibility | All | Most (avoid `synchronized`+I/O) | Reactive-compatible only |
| Learning curve | None | Low | High |
| Recommendation (Java 21) | No | **YES** | Only if already reactive |

### Decision
Use Virtual Threads (`spring.threads.virtual.enabled=true` in Spring Boot 3.2+).

### Consequences
- Refactor any `synchronized`+I/O to `ReentrantLock`
- Add `Semaphore` to bound DB connection usage
- Replace `ThreadLocal` context with `ScopedValue` where possible
- Gain: simplified code vs reactive, 100x more concurrent requests for same memory

---

## ADR-02: Lock Granularity for Account Operations

### Context
Payment service. Multiple concurrent operations on the same account (debit, credit, balance check). Need thread safety.

### Options

**Option 1: Single global lock** — Simple. Bottleneck: all account ops serialized.

**Option 2: Per-account lock** — Lock striping. Better throughput. More complex.
```java
Map<String, ReentrantLock> accountLocks = new ConcurrentHashMap<>();
ReentrantLock lock = accountLocks.computeIfAbsent(accountId, k -> new ReentrantLock());
```

**Option 3: Database optimistic locking** — No Java locks. Use DB `version` column.
```java
@Version Long version;  // JPA optimistic lock: throws OptimisticLockException on conflict
```

**Option 4: Event sourcing** — No mutable state. Events serialized per account.

### Decision
Database optimistic locking for single-instance, event sourcing for high-throughput.

**Rationale**: Database is the source of truth anyway. Java-level locks don't protect against concurrent access from multiple service instances. DB-level locking (optimistic or pessimistic) is the correct boundary.

---

## ADR-03: Thread Pool Strategy for Mixed Workload

### Context
Service handles: 60% fast queries (2ms), 30% slow external calls (200ms), 10% CPU computation (100ms).

### Decision: Separate Pools (Bulkhead)

```java
// Fast I/O pool: many threads, short queue
ExecutorService fastPool = new ThreadPoolExecutor(10, 50, 60, SECONDS,
    new ArrayBlockingQueue<>(500), namedFactory("fast-io"));

// Slow I/O pool: separate — doesn't block fast pool
ExecutorService slowPool = Executors.newVirtualThreadPerTaskExecutor();

// CPU pool: exactly CPU count — no benefit from more
ExecutorService cpuPool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors(), namedFactory("cpu"));
```

### Rationale
If mixed in one pool: slow tasks fill all thread slots, fast tasks queue behind them (head-of-line blocking). Separate pools = bulkhead isolation. One pool slow doesn't affect others.

---

## Thread Pool Sizing Reference Card

```
Service Type        │ Pool Size Formula           │ Queue    │ Rejection
────────────────────┼─────────────────────────────┼──────────┼──────────────
API handler         │ VTs (unlimited)             │ N/A      │ N/A
DB queries          │ 2× DB pool size             │ 200      │ CallerRuns
External HTTP       │ VTs or 100 platform threads │ 500      │ CallerRuns
CPU computation     │ CPU cores                   │ 50       │ AbortPolicy
Background jobs     │ 5-10 threads                │ 1000     │ DiscardOldest
Batch processing    │ CPU cores × 2               │ Unbounded│ CallerRuns
```
