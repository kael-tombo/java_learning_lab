# Project Reactor -- Visual Guide
## Reactive Stream Flow
Publisher -> [Operator1] -> [Operator2] -> Subscriber
## Backpressure Flow
Subscriber.request(N) -> Subscription -> Publisher produces N items
## Hot vs Cold
Cold: each subscriber gets its own stream
Hot: all subscribers share the same stream
