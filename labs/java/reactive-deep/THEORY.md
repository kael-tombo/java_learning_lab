# THEORY — Reactive Programming Deep Dive

## Overview

Reactive programming with Project Reactor, RxJava, and Reactive Streams specification. Covers backpressure, operators, schedulers, and integration patterns.

---

## Reactive Streams Specification

### Core Interfaces

```java
// Publisher produces items
interface Publisher<T> {
    void subscribe(Subscriber<? super T> subscriber);
}

// Subscriber consumes items
interface Subscriber<T> {
    void onSubscribe(Subscription subscription);
    void onNext(T item);
    void onError(Throwable throwable);
    void onComplete();
}

// Subscription controls flow
interface Subscription {
    void request(long n);  // Demand
    void cancel();         // Cancel
}
```

### Flow Control (Backpressure)

```
Publisher → Subscriber
    subscribe(Subscriber)
    → onSubscribe(Subscription)
    → request(n)  [Demand signaled upstream]
    → onNext(T) × N  [Up to n items]
    → onComplete() / onError(Throwable)
```

---

## Project Reactor (Recommended for Spring)

### Flux (0..N elements)

```java
// Creation
Flux.just(1, 2, 3)
Flux.fromIterable(list)
Flux.fromArray(array)
Flux.range(1, 10)
Flux.interval(Duration.ofSeconds(1))
Flux.generate(() -> 0, (state, sink) -> sink.next(state++))

// Transform
flux.map(x -> x * 2)
flux.flatMap(x -> fetchData(x))
flux.filter(x -> x > 5)
flux.distinct()
flux.sorted()

// Combine
Flux.merge(flux1, flux2)
Flux.concat(flux1, flux2)
Flux.zip(flux1, flux2, (a, b) -> a + b)
Flux.combineLatest(flux1, flux2, (a, b) -> a + b)

// Side effects
flux.doOnNext(System.out::println)
flux.doOnError(err -> log.error(err))
flux.doOnComplete(() -> log.info("Done"))
```

### Mono (0..1 element)

```java
Mono.just(value)
Mono.empty()
Mono.error(new Exception("fail"))
Mono.fromFuture(future)
Mono.fromCallable(() -> compute())

mono.flatMap(x -> fetchRelated(x))
mono.switchIfEmpty(Mono.just(defaultValue))
mono.onErrorResume(err -> fallback())
```

### Backpressure Strategies

```java
// Request all (unbounded)
flux.subscribe()

// Request n
flux.subscribe(new BaseSubscriber<>() {
    @Override
    protected void hookOnSubscribe(Subscription s) {
        request(10);
    }
    @Override
    protected void hookOnNext(T value) {
        process(value);
        request(1); // Request one more
    }
});

// Operators for backpressure
flux.onBackpressureBuffer()      // Buffer all (OOM risk)
flux.onBackpressureBuffer(1000)  // Buffer with limit
flux.onBackpressureDrop()        // Drop new
flux.onBackpressureLatest()      // Keep latest only
flux.onBackpressureError()       // Error on overflow
```

### Schedulers

```java
// Parallel (CPU-bound)
flux.subscribeOn(Schedulers.parallel())
flux.publishOn(Schedulers.parallel())

// Bounded elastic (I/O, legacy blocking)
flux.subscribeOn(Schedulers.boundedElastic())

// Single (sequential)
flux.publishOn(Schedulers.single())

// Virtual threads (Java 21+)
flux.subscribeOn(Schedulers.fromExecutor(
    Executors.newVirtualThreadPerTaskExecutor()
))

// Custom
Scheduler custom = Schedulers.newParallel("custom", 4);
```

### Error Handling

```java
flux.onErrorReturn(defaultValue)
flux.onErrorResume(err -> fallbackFlux)
flux.onErrorMap(err -> new BusinessException(err))
flux.retry(3)
flux.retryWhen(Retry.backoff(3, Duration.ofSeconds(1))
    .filter(err -> err instanceof TransientException))
flux.doOnError(err -> log.error(err))
```

### Testing

```java
StepVerifier.create(flux)
    .expectNext(1, 2, 3)
    .expectComplete()
    .verify();

StepVerifier.create(mono)
    .expectNext(value)
    .verifyComplete();

StepVerifier.create(flux)
    .expectErrorMessage("expected error")
    .verify();
```

---

## RxJava 3

### Core Types

```java
// Flowable (backpressure-aware, 0..N)
Flowable.just(1, 2, 3)
Flowable.fromIterable(list)
Flowable.interval(1, TimeUnit.SECONDS)

// Observable (no backpressure, 0..N)
Observable.just(1, 2, 3)
Observable.fromIterable(list)

// Single (0..1)
Single.just(value)
Single.fromCallable(() -> compute())

// Maybe (0..1, can be empty)
Maybe.just(value)
Maybe.empty()

// Completable (completion only)
Completable.fromAction(() -> action())
```

### Backpressure

```java
// Flowable operators
flowable.onBackpressureBuffer()
flowable.onBackpressureDrop()
flowable.onBackpressureLatest()

// Subscriber with request
flowable.subscribe(new Subscriber<Integer>() {
    Subscription s;
    public void onSubscribe(Subscription s) { this.s = s; s.request(10); }
    public void onNext(Integer t) { process(t); s.request(1); }
    public void onError(Throwable t) { }
    public void onComplete() { }
});
```

---

## RSocket (Reactive Protocol)

### Interaction Models

```java
// Request-Response
Mono<Response> requestResponse(Payload request);

// Request-Stream
Flux<Response> requestStream(Payload request);

// Fire-and-Forget
Mono<Void> fireAndForget(Payload request);

// Channel (bidirectional)
Flux<Response> channel(Flux<Payload> requests);
```

### Server

```java
RSocketFactory.receive()
    .acceptor((setup, sendingSocket) -> Mono.just(new AbstractRSocket() {
        @Override
        public Flux<Payload> requestStream(Payload request) {
            return Flux.interval(Duration.ofSeconds(1))
                .map(i -> DefaultPayload.create("Response " + i));
        }
    }))
    .transport(TcpServerTransport.create("localhost", 7000))
    .start()
    .subscribe();
```

---

## Spring WebFlux Integration

### Controller

```java
@RestController
@RequestMapping("/users")
public class UserController {
    
    @GetMapping
    public Flux<User> getAll() {
        return userRepository.findAll();
    }
    
    @GetMapping("/{id}")
    public Mono<User> getById(@PathVariable String id) {
        return userRepository.findById(id);
    }
    
    @PostMapping
    public Mono<User> create(@RequestBody Mono<User> userMono) {
        return userMono.flatMap(userRepository::save);
    }
    
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<User> stream() {
        return userRepository.findAll().delayElements(Duration.ofSeconds(1));
    }
}
```

### WebClient

```java
WebClient client = WebClient.builder()
    .baseUrl("https://api.example.com")
    .build();

Mono<User> user = client.get()
    .uri("/users/{id}", id)
    .retrieve()
    .bodyToMono(User.class);

Flux<User> users = client.get()
    .uri("/users")
    .retrieve()
    .bodyToFlux(User.class);
```

---

## Best Practices

| Do | Don't |
|----|-------|
| Use `Flux`/`Mono` for async boundaries | Block in reactive chain (`.block()`) |
| Handle backpressure explicitly | Ignore backpressure (unbounded buffer) |
| Use `subscribeOn` for source threading | Mix blocking and reactive code |
| Use `publishOn` for downstream threading | Subscribe multiple times to cold publisher |
| Test with `StepVerifier` | Use `Thread.sleep` in tests |

---

## Common Patterns

### Pagination

```java
Flux<User> paginated = Flux.generate(
    () -> 0,
    (page, sink) -> {
        Page<User> result = repo.findPage(page, 20);
        result.getContent().forEach(sink::next);
        if (!result.hasNext()) sink.complete();
        return page + 1;
    }
);
```

### Retry with Backoff

```java
flux.retryWhen(Retry.backoff(5, Duration.ofSeconds(1))
    .jitter(0.5)
    .doBeforeRetry(signal -> log.warn("Retry: {}", signal.failure()))
    .filter(err -> err instanceof TransientException))
```

### Timeout

```java
flux.timeout(Duration.ofSeconds(5))
    .onErrorResume(err -> fallback())
```