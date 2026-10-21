# Interview Questions: Reactive Streams

## Company-Specific Focus

### Google
- Reactive Streams specification: Publisher, Subscriber, Subscription, Processor
- Backpressure: subscriber controls demand via request(n) method
- Subscription: linking publisher and subscriber

### Microsoft
- Reactive Streams vs .NET IObservable/IObserver (Rx.NET)
- Flow API: java.util.concurrent.Flow (Java 9+)

### Amazon
- Backpressure: protecting downstream from being overwhelmed
- Publisher design: creating custom publishers
- Demand management: batching, windowing, throttling

### Meta
- Cancellation: subscription.cancel() to stop receiving events
- OnError: error handling in reactive streams
- OnComplete: terminal event signaling end of stream

### Apple
- Flow API: java.util.concurrent.Flow classes
- SubmissionPublisher: built-in implementation of Publisher
- Processor: transforming elements in the stream

### Oracle
- Reactive Streams: initiative for asynchronous stream processing with non-blocking backpressure
- java.util.concurrent.Flow: introduced in JDK 9
- Four interfaces: Publisher, Subscriber, Subscription, Processor
- SubmissionPublisher: default Publisher implementation

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Reactive Streams is a specification) |

## Real Production Scenarios
- **Netflix**: Backpressure failure in Hystrix caused cascading failure — corrected with proper demand management
- **LinkedIn**: Reactive Streams pipeline processing 1M events/sec with bounded buffers

## Interview Patterns & Tips
- **Backpressure**: fundamental concept in reactive streams
- **Demand**: subscriber controls the rate
- **Non-blocking**: all interactions are asynchronous
- **Error propagation**: errors are communicated via onError

## Deep Dive Questions
- **Reactive Streams spec**: What are the rules governing onNext and request?
- **Backpressure**: How does backpressure flow through the system?
- **Specification**: What are the Rule 1.1 to 3.17 constraints?
- **Subscription**: How does demand management work?
- **Processor**: How do processors enable chaining of reactive operations?