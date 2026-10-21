# Project Reactor -- Theoretical Foundation
## Core Concepts
### 1. Reactive Manifesto
Reactive systems are Responsive, Resilient, Elastic, and Message-Driven.
### 2. Reactive Streams Specification
Publisher -> subscribe -> Subscriber (with backpressure via Subscription.request(n))
### 3. Key Principles
- Asynchronous data streams
- Backpressure-aware
- Non-blocking
- Resilient and elastic
## Reactive vs Imperative
- Imperative: blocking, synchronous, pull-based
- Reactive: non-blocking, asynchronous, push-based
## Backpressure Strategies
- BUFFER: buffer events until consumed
- DROP: drop events when overwhelmed
- LATEST: keep only latest event
- ERROR: error when downstream can't keep up
