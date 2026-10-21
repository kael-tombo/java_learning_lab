# Reactive Programming — Internal Mechanics

## How Project Reactor Works

### Publisher-Subscriber Protocol

Reactive streams follow a strict protocol:
1. Subscriber subscribes to Publisher
2. Publisher calls `onSubscribe(Subscription)`
3. Subscriber calls `request(n)` to demand data
4. Publisher calls `onNext(item)` up to the requested count
5. Publisher calls `onComplete()` or `onError(Throwable)`
6. No further signals are sent after terminal events

### Operator Fusion

Reactor optimizes operator chains through fusion:
- **Assembly**: Operators are chained during assembly time
- **Subscription**: Each operator wraps the downstream subscription
- **Fusion**: Adjacent operators can merge into a single step

### Schedulers

Reactors scheduling model:
- `Schedulers.parallel()` — Fixed pool for CPU-bound work
- `Schedulers.boundedElastic()` — Elastic pool for blocking I/O
- `Schedulers.single()` — Single-threaded scheduler
- `Schedulers.immediate()` — Runs on current thread

### Backpressure

Backpressure is implemented through the `request(n)` mechanism:
- Publisher tracks demand via an atomic counter
- `onNext` only delivers when demand > 0
- Buffer/drop/latest strategies handle overflow
- Operators propagate demand upstream
