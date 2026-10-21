# WebFlux Deep Dive -- Mathematical Foundation
## 1. Backpressure Mathematics
### Request-N Pattern
Subscriber requests N items: downstream produces at most N.
### Buffer Sizing
buffer_size >= production_rate * processing_time
## 2. Operator Complexity
- map: O(1) per element
- flatMap: O(n * m) where n=source, m=inner
- concatMap: O(n) sequential
- merge: O(n) concurrent
## 3. Scheduler Mathematics
- parallel(): N threads for N CPU cores
- elastic(): unbounded thread pool
- boundedElastic(): bounded thread pool with max size
