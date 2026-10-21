# Interview Questions: Reactive Testing

## Company-Specific Focus

### Google
- StepVerifier: testing reactive sequences (Flux, Mono)
- expectNext, expectComplete, expectError: assertion methods
- VirtualTimeScheduler: testing time-based operators

### Microsoft
- Reactive testing vs .NET testing for reactive
- Step name: verifying specific steps in the sequence

### Amazon
- TestPublisher: creating test data streams
- then and thenCancel: continuing after verification
- Context testing: verifying reactive context values

### Meta
- Signal events: onNext, onError, onComplete verification
- Demand testing: verify backpressure behavior
- Assertions: verify specific elements and states

### Apple
- Virtual time: advanceTimeBy for testing delay operators
- Recording: StepVerifier.create(flux).recordWith() for collecting elements
- Duration: verifyWithVirtualTime for time-based tests

### Oracle
- StepVerifier is part of Project Reactor Test
- Reactor Test: TestPublisher, StepVerifier, VirtualTimeScheduler
- Testing is critical for reactive applications

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — reactive testing is a testing methodology) |

## Real Production Scenarios
- **Netflix**: StepVerifier caught a missing onComplete signal in critical reactive pipeline
- **Uber**: VirtualTimeScheduler regression test for timeout operators

## Interview Patterns & Tips
- **StepVerifier**: the primary testing tool for reactive sequences
- **Virtual time**: avoid real time in tests
- **TestPublisher**: create controlled reactive streams
- **Context**: test reactive context propagation

## Deep Dive Questions
- **StepVerifier**: How does StepVerifier subscribe and verify?
- **VirtualTimeScheduler**: How does virtual time work in tests?
- **TestPublisher**: How does TestPublisher create test sequences?
- **Backpressure testing**: How to verify backpressure behavior?
- **Context testing**: How to test reactive context values?