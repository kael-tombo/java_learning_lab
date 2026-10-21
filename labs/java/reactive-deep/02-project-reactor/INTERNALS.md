# Project Reactor -- Internals
## Internal Architecture
### Publisher Subscription
Publisher creates Subscription on subscribe(). Subscription manages demand.
### Operator Implementation
Operators wrap the downstream Subscriber and implement Reactive Streams interfaces.
### Scheduler Workers
Schedulers provide Worker instances for executing tasks on threads.
