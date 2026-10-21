# Interview Questions: Reactive Programming

## Company-Specific Focus

### Google
- Reactive Streams specification: Publisher, Subscriber, Subscription, Processor
- Project Reactor vs RxJava: choosing the right reactive library
- Backpressure handling: how reactive streams handle demand

### Microsoft
- Reactive in Java vs .NET Reactive Extensions (Rx.NET)
- Spring WebFlux: building reactive web services
- Observable vs Flowable vs Flux: backpressure support

### Amazon
- Reactive patterns in microservices: event-driven architecture
- Non-blocking I/O: WebFlux with Netty for high throughput
- Backpressure: how to handle load spikes in reactive systems

### Meta
- Reactive testing: StepVerifier, TestPublisher
- Error handling in reactive chains: onErrorResume, onErrorReturn
- Schedulers: parallel vs elastic vs boundedElastic

### Apple
- Memory management in reactive: avoiding object buildup
- Reactive streams and virtual threads: performance comparison

### Oracle
- Reactive Streams specification integration in Java 9 (Flow API)
- java.util.concurrent.Flow classes: Publisher, Subscriber, Subscription
- Reactive landscape in Java: Project Reactor, RxJava

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (Reactive patterns apply architecturally to many problems) |
| 146 LRU Cache | Medium | Google, Amazon | Reactive cache invalidation patterns |

## Real Production Scenarios
- **Netflix**: Backpressure handling failure in Hystrix caused cascading failure
- **LinkedIn**: Using reactive streams for data ingestion pipeline processing 1M events/sec
- **Twitter**: WebFlux migration from Spring MVC improved throughput by 200%

## Interview Patterns & Tips
- **Cold vs Hot publishers**: cold emits per subscriber, hot broadcasts
- **Backpressure**: subscriber controls the demand via request(n)
- **Schedulers**: control on which thread the reactive chain runs
- **Mono vs Flux**: 0-1 vs 0-N elements

## Deep Dive Questions
- **Reactive Streams spec**: What are the rules about onNext?
- **Backpressure**: How does Project Reactor implement backpressure?
- **Schedulers**: How does parallel scheduler differ from boundedElastic?
- **Testing**: How to test reactive streams with StepVerifier?
- **Java 9 Flow**: How does the Flow API compare with Reactive Streams?