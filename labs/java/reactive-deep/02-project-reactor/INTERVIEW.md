# Interview Questions: Project Reactor

## Company-Specific Focus

### Google
- Project Reactor: reactive library implementing Reactive Streams
- Flux: 0..N elements reactive sequence
- Mono: 0..1 element reactive sequence

### Microsoft
- Project Reactor vs .NET Rx.NET: similar reactive foundations
- Flux and Mono: publishers with backpressure

### Amazon
- Operators: map, flatMap, filter, reduce, transform
- Threading: Schedulers for controlling execution threads
- Error handling: onErrorResume, onErrorReturn, onErrorContinue

### Meta
- FlatMap: asynchronous concurrency with concurrent inner subscriptions
- ConcatMap: ordered, sequential inner subscriptions
- Schedulers: parallel, boundedElastic, immediate, single

### Apple
- Backpressure: configurable strategy (latest, error, drop, buffer)
- Hot vs Cold: share, replay, cache operators
- Testing: StepVerifier testing utilities

### Oracle
- Project Reactor is the foundation of Spring WebFlux
- Reactor Core: reactive types (Flux, Mono)
- Reactor Test: StepVerifier, TestPublisher
- Reactor Extra: additional operators

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Project Reactor is a reactive library) |

## Real Production Scenarios
- **Netflix**: Reactor-based pipeline for stream processing with backpressure handling
- **Uber**: Flux-based data pipeline for real-time analytics processing

## Interview Patterns & Tips
- **Mono**: 0-1 element publisher (like Optional)
- **Flux**: 0-N element publisher (like Stream)
- **Schedulers**: control thread execution
- **StepVerifier**: testing reactive sequences

## Deep Dive Questions
- **Assembly vs subscription**: How does lazy evaluation work in Reactor?
- **Operator fusion**: How does Reactor optimize operator chains?
- **Schedulers**: How are different schedulers implemented?
- **Backpressure**: How does Flux handle backpressure strategies?
- **Hooks**: What debugging hooks does Reactor provide?