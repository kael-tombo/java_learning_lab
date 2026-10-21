# Reactive Testing -- How It Works
## How Reactive Streams Work
### Subscription Setup
1. Publisher.subscribe(Subscriber) called
2. Publisher calls subscriber.onSubscribe(Subscription)
3. Subscriber calls subscription.request(N)
4. Publisher emits up to N items via onNext()
5. When complete: onComplete(). On error: onError().
