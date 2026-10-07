# Code Deep Dive - Reactive Java Deep Dive (reactive-deep)

Six topics, each with a short mechanism note, a complete snippet, the output observed when it was run, and one pitfall.

Conventions used in this file:

- Snippets whose first line is not a `// Requires ...` comment use only the JDK (`java.util.concurrent.Flow`, `SubmissionPublisher`, `CompletableFuture`). They were extracted, compiled with `javac --release 21 -proc:none`, run on JDK 23, and the printed output is pasted verbatim.
- Snippets marked `// Requires io.projectreactor:reactor-core / reactor-test; not compiled in this repo` need Reactor on the classpath. They have no observed output because they were not run here.
- `java.util.concurrent.Flow` is the JDK's copy of the Reactive Streams interfaces (`Publisher`, `Subscriber`, `Subscription`, `Processor`). `SubmissionPublisher` is the only Publisher implementation the JDK ships.

## Snippet 1: Publisher/Subscriber

A `Flow.Publisher` hands a `Flow.Subscription` to each subscriber in `onSubscribe`; after that the publisher may send at most as many `onNext` signals as the subscriber has asked for through `Subscription.request(n)`. `SubmissionPublisher` keeps a per-subscriber buffer and delivers from an `Executor`, so signals for one subscriber arrive serially but on a different thread than the caller of `submit`. Closing the publisher (here via try-with-resources) sends `onComplete` only after buffered items have been delivered.

The subscriber below asks for 2 items, and every time it has consumed 2 it asks for 2 more.

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;

public class FlowRequestDemo {

    static final class BatchSubscriber implements Flow.Subscriber<Integer> {
        private final int batch;
        private final CountDownLatch done;
        private Flow.Subscription subscription;
        private int receivedInBatch;

        BatchSubscriber(int batch, CountDownLatch done) {
            this.batch = batch;
            this.done = done;
        }

        @Override
        public void onSubscribe(Flow.Subscription s) {
            subscription = s;
            System.out.println("onSubscribe -> request(" + batch + ")");
            s.request(batch);
        }

        @Override
        public void onNext(Integer item) {
            System.out.println("onNext " + item);
            if (++receivedInBatch == batch) {
                receivedInBatch = 0;
                System.out.println("batch consumed -> request(" + batch + ")");
                subscription.request(batch);
            }
        }

        @Override
        public void onError(Throwable t) {
            System.out.println("onError " + t);
            done.countDown();
        }

        @Override
        public void onComplete() {
            System.out.println("onComplete");
            done.countDown();
        }
    }

    public static void main(String[] args) throws Exception {
        CountDownLatch done = new CountDownLatch(1);
        try (SubmissionPublisher<Integer> publisher = new SubmissionPublisher<>()) {
            publisher.subscribe(new BatchSubscriber(2, done));
            for (int i = 1; i <= 5; i++) {
                publisher.submit(i);
            }
        }
        done.await();
    }
}
```

Observed output (`java FlowRequestDemo`):

```text
onSubscribe -> request(2)
onNext 1
onNext 2
batch consumed -> request(2)
onNext 3
onNext 4
batch consumed -> request(2)
onNext 5
onComplete
```

**Pitfall:** `request(n)` is cumulative and `Long.MAX_VALUE` means "unbounded". A subscriber that forgets to call `request` in `onSubscribe` (or calls it only from `onNext`, which then never fires) receives nothing and never completes; the publisher simply sits on its buffer. The failure is silent: there is no exception, just a latch or test that waits forever.

## Snippet 2: Flux/Mono

`Mono<T>` is a Publisher of at most one element and `Flux<T>` of zero to N. Calling operators (`map`, `filter`, `doOnSubscribe`) only builds a chain of decorator objects ("assembly"); the source is not touched until `subscribe`, and each `subscribe` on a cold source such as `Flux.range` replays the whole chain from the start.

The first block is Reactor code. The second block is a JDK-only miniature of the same assembly-versus-subscription split, so the ordering can be observed without Reactor.

```java
// Requires io.projectreactor:reactor-core; not compiled in this repo
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public class ReactorAssembly {
    public static void main(String[] args) {
        Flux<Integer> numbers = Flux.range(1, 5)
                .doOnSubscribe(s -> System.out.println("subscribed"))
                .map(i -> i * 10)
                .filter(i -> i > 20);

        System.out.println("assembled; nothing has run yet");
        numbers.subscribe(i -> System.out.println("first subscriber got " + i));
        numbers.subscribe(i -> System.out.println("second subscriber got " + i));

        Mono<String> one = Mono.fromSupplier(() -> "computed").map(String::toUpperCase);
        System.out.println(one.block());
    }
}
```

JDK-only analogue (a cold, lazy sequence with `map`):

```java
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;

public class LazyAssemblyDemo {

    static final class Seq<T> {
        private final Consumer<Consumer<T>> source;

        private Seq(Consumer<Consumer<T>> source) {
            this.source = source;
        }

        static <T> Seq<T> fromList(String name, List<T> items) {
            return new Seq<>(sink -> {
                System.out.println("  source '" + name + "' starts emitting");
                items.forEach(sink);
            });
        }

        <R> Seq<R> map(Function<T, R> f) {
            System.out.println("assembling map()");
            return new Seq<>(sink -> source.accept(t -> sink.accept(f.apply(t))));
        }

        void subscribe(String who, Consumer<T> onNext) {
            System.out.println(who + " subscribes");
            source.accept(onNext);
        }
    }

    public static void main(String[] args) {
        Seq<Integer> numbers = Seq.fromList("range", List.of(1, 2, 3)).map(i -> i * 10);
        System.out.println("assembled; nothing has run yet");
        numbers.subscribe("first", i -> System.out.println("  first got " + i));
        numbers.subscribe("second", i -> System.out.println("  second got " + i));
    }
}
```

Observed output (`java LazyAssemblyDemo`):

```text
assembling map()
assembled; nothing has run yet
first subscribes
  source 'range' starts emitting
  first got 10
  first got 20
  first got 30
second subscribes
  source 'range' starts emitting
  second got 10
  second got 20
  second got 30
```

**Pitfall:** because nothing runs without a subscriber, a method that builds a `Mono` for a side effect (for example `repository.save(x).then()`) and returns `void`, or discards the result, silently does nothing. The code compiles, the unit test that only calls the method passes, and the row is never written. Conversely, subscribing twice to a cold `Mono.fromCallable` runs the call twice (two HTTP requests, two inserts) unless you add `cache()`.

## Snippet 3: backpressure strategies

When a producer is faster than its consumer there are only three choices: buffer without limit, bound the buffer and drop (or fail), or block the producer. `SubmissionPublisher.offer(item, onDrop)` is the "bounded and drop" choice: when the subscriber's buffer is full, the `onDrop` callback runs on the caller's thread and, if it returns `false`, the item is discarded without retry. The return value of `offer` is negative when drops happened and otherwise an estimate of the maximum lag.

The subscriber below deliberately requests nothing until all 10 offers have been made, so only the buffer capacity (4) stands between the items and the drop handler.

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Flow;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.SubmissionPublisher;
import java.util.concurrent.atomic.AtomicReference;

public class DropOnOverflowDemo {

    public static void main(String[] args) throws Exception {
        CountDownLatch done = new CountDownLatch(1);
        AtomicReference<Flow.Subscription> held = new AtomicReference<>();
        SubmissionPublisher<Integer> publisher = new SubmissionPublisher<>(ForkJoinPool.commonPool(), 4);
        System.out.println("max buffer capacity = " + publisher.getMaxBufferCapacity());

        publisher.subscribe(new Flow.Subscriber<Integer>() {
            @Override
            public void onSubscribe(Flow.Subscription s) {
                held.set(s); // demand stays at zero
            }

            @Override
            public void onNext(Integer item) {
                System.out.println("consumed " + item);
            }

            @Override
            public void onError(Throwable t) {
                System.out.println("onError " + t);
                done.countDown();
            }

            @Override
            public void onComplete() {
                System.out.println("onComplete");
                done.countDown();
            }
        });

        while (held.get() == null) {
            Thread.onSpinWait();
        }

        for (int i = 1; i <= 10; i++) {
            int result = publisher.offer(i, (subscriber, dropped) -> {
                System.out.println("  onDrop handler saw " + dropped);
                return false; // do not retry
            });
            System.out.println("offer(" + i + ") returned " + result);
        }

        held.get().request(Long.MAX_VALUE);
        publisher.close();
        done.await();
    }
}
```

Observed output (`java DropOnOverflowDemo`):

```text
max buffer capacity = 4
offer(1) returned 1
offer(2) returned 2
offer(3) returned 3
offer(4) returned 4
  onDrop handler saw 5
offer(5) returned -1
  onDrop handler saw 6
offer(6) returned -1
  onDrop handler saw 7
offer(7) returned -1
  onDrop handler saw 8
offer(8) returned -1
  onDrop handler saw 9
offer(9) returned -1
  onDrop handler saw 10
offer(10) returned -1
consumed 1
consumed 2
consumed 3
consumed 4
onComplete
```

Reading the output: the first four offers fit in the buffer (the return value is the growing lag 1 to 4), items 5 to 10 each hit the `onDrop` handler and `offer` returned -1, and once demand arrived the subscriber saw only items 1 to 4.

Reactor expresses the same decision as an operator on the upstream side of a slow consumer:

```java
// Requires io.projectreactor:reactor-core; not compiled in this repo
import java.time.Duration;
import org.reactivestreams.Subscription;
import reactor.core.publisher.BaseSubscriber;
import reactor.core.publisher.BufferOverflowStrategy;
import reactor.core.publisher.Flux;

public class ReactorBackpressure {
    public static void main(String[] args) throws InterruptedException {
        Flux<Long> fast = Flux.interval(Duration.ofMillis(1));

        fast.onBackpressureBuffer(16, dropped -> System.out.println("overflow " + dropped),
                        BufferOverflowStrategy.DROP_OLDEST)
                .subscribe(new BaseSubscriber<Long>() {
                    @Override
                    protected void hookOnSubscribe(Subscription subscription) {
                        request(1);
                    }

                    @Override
                    protected void hookOnNext(Long value) {
                        try {
                            Thread.sleep(50);
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                        }
                        request(1);
                    }
                });

        // Alternatives on the same upstream:
        //   fast.onBackpressureDrop()          discard what the subscriber has no demand for
        //   fast.onBackpressureLatest()        keep only the newest unrequested item
        //   fast.limitRate(32)                 replenish demand to upstream in batches of 32
        Thread.sleep(500);
    }
}
```

**Pitfall:** `Flux.interval` ignores demand: if the subscriber is slower than the tick, Reactor terminates the sequence with an `OverflowException` ("Could not emit tick ... due to lack of requests") instead of buffering. Developers who tested with a fast consumer see it only in production under load. The fix is choosing a strategy explicitly (`onBackpressureDrop`, `onBackpressureLatest`, bounded `onBackpressureBuffer`), not enlarging a queue.

## Snippet 4: schedulers

A scheduler decides which thread runs a stage. In Reactor, `subscribeOn(s)` moves the subscription (and so the source's work) onto `s`, while `publishOn(s)` moves everything downstream of that point; with neither operator, work stays on whichever thread calls `subscribe`. The JDK has the same two levers: the executor passed to `CompletableFuture` stages, and the executor passed to `SubmissionPublisher`, which decides where `onNext` runs.

```java
// Requires io.projectreactor:reactor-core; not compiled in this repo
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

public class ReactorSchedulers {
    static String loadBlocking(int id) {
        // stands in for a JDBC or file call that blocks its thread
        return "row-" + id + " on " + Thread.currentThread().getName();
    }

    public static void main(String[] args) throws InterruptedException {
        Mono.fromCallable(() -> loadBlocking(7))
                .subscribeOn(Schedulers.boundedElastic())   // blocking source gets an elastic worker
                .map(s -> s + " | mapped on " + Thread.currentThread().getName())
                .publishOn(Schedulers.parallel())           // downstream CPU work on a parallel worker
                .map(s -> s + " | finished on " + Thread.currentThread().getName())
                .subscribe(System.out::println);
        Thread.sleep(200);
    }
}
```

JDK-only analogue with two named single-thread executors:

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;
import java.util.concurrent.ThreadFactory;

public class ThreadHopDemo {

    static ThreadFactory named(String name) {
        return r -> new Thread(r, name);
    }

    static void log(String stage) {
        System.out.println(stage + " on " + Thread.currentThread().getName());
    }

    public static void main(String[] args) throws Exception {
        ExecutorService io = Executors.newSingleThreadExecutor(named("io-1"));
        ExecutorService cpu = Executors.newSingleThreadExecutor(named("cpu-1"));

        int result = CompletableFuture.supplyAsync(() -> { log("load"); return 20; }, io)
                .thenApplyAsync(v -> { log("compute"); return v * 2; }, cpu)
                .thenApplyAsync(v -> { log("save"); return v + 2; }, io)
                .join();
        System.out.println("result = " + result);

        CountDownLatch subscribed = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(1);
        try (SubmissionPublisher<String> publisher = new SubmissionPublisher<>(cpu, 8)) {
            publisher.subscribe(new Flow.Subscriber<String>() {
                @Override
                public void onSubscribe(Flow.Subscription s) {
                    log("onSubscribe");
                    s.request(Long.MAX_VALUE);
                    subscribed.countDown();
                }

                @Override
                public void onNext(String item) {
                    log("onNext(" + item + ")");
                }

                @Override
                public void onError(Throwable t) {
                    done.countDown();
                }

                @Override
                public void onComplete() {
                    log("onComplete");
                    done.countDown();
                }
            });
            subscribed.await();
            log("submit");
            publisher.submit("x");
        }
        done.await();
        io.shutdown();
        cpu.shutdown();
    }
}
```

Observed output (`java ThreadHopDemo`):

```text
load on io-1
compute on cpu-1
save on io-1
result = 42
onSubscribe on cpu-1
submit on main
onNext(x) on cpu-1
onComplete on cpu-1
```

**Pitfall:** blocking a thread that belongs to a non-blocking scheduler. Reactor's `parallel()` workers are sized to the CPU count; a `Thread.sleep`, JDBC call, or synchronous HTTP client inside a `map` after `publishOn(Schedulers.parallel())` stalls every other pipeline sharing those few workers. Calling `block()` on such a thread is rejected with an `IllegalStateException` saying `block()/blockFirst()/blockLast() are blocking, which is not supported in thread parallel-N`. Blocking work belongs behind `subscribeOn(Schedulers.boundedElastic())`.

## Snippet 5: error handling

In Reactive Streams an error is a terminal signal: after `onError` no further `onNext` or `onComplete` may be delivered, and the subscription is dead. `SubmissionPublisher` follows that contract in two ways: `closeExceptionally(t)` sends `onError(t)` to every subscriber, and if a subscriber's own `onNext` throws, the publisher cancels that subscription and delivers the exception to its `onError`. The demo uses `Runnable::run` as the executor so delivery happens synchronously inside `submit`, which makes the sequence of events deterministic.

```java
import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;

public class FlowErrorDemo {

    static final class Printing implements Flow.Subscriber<Integer> {
        private final String name;
        private final int failOn;

        Printing(String name, int failOn) {
            this.name = name;
            this.failOn = failOn;
        }

        @Override
        public void onSubscribe(Flow.Subscription s) {
            s.request(Long.MAX_VALUE);
        }

        @Override
        public void onNext(Integer item) {
            if (item == failOn) {
                throw new IllegalArgumentException("cannot handle " + item);
            }
            System.out.println(name + " onNext " + item);
        }

        @Override
        public void onError(Throwable t) {
            System.out.println(name + " onError " + t);
        }

        @Override
        public void onComplete() {
            System.out.println(name + " onComplete");
        }
    }

    public static void main(String[] args) {
        System.out.println("-- subscriber throws on item 3");
        try (SubmissionPublisher<Integer> p = new SubmissionPublisher<>(Runnable::run, 16)) {
            p.subscribe(new Printing("A", 3));
            for (int i = 1; i <= 5; i++) {
                p.submit(i);
            }
        }

        System.out.println("-- upstream fails after item 2");
        SubmissionPublisher<Integer> q = new SubmissionPublisher<>(Runnable::run, 16);
        q.subscribe(new Printing("B", -1));
        q.submit(1);
        q.submit(2);
        q.closeExceptionally(new IllegalStateException("upstream failed"));
    }
}
```

Observed output (`java FlowErrorDemo`):

```text
-- subscriber throws on item 3
A onNext 1
A onNext 2
A onError java.lang.IllegalArgumentException: cannot handle 3
-- upstream fails after item 2
B onNext 1
B onNext 2
B onError java.lang.IllegalStateException: upstream failed
```

Reactor's operators recover from or transform that terminal signal by swapping in another publisher:

```java
// Requires io.projectreactor:reactor-core; not compiled in this repo
import java.time.Duration;
import java.util.concurrent.TimeoutException;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;

public class ReactorErrors {
    static String remoteCall() throws Exception {
        throw new TimeoutException("upstream too slow");
    }

    public static void main(String[] args) {
        Mono<String> value = Mono.fromCallable(ReactorErrors::remoteCall)
                .doOnError(e -> System.out.println("attempt failed: " + e))
                .retryWhen(Retry.backoff(3, Duration.ofMillis(100)))   // 3 retries, exponential delay
                .onErrorResume(e -> Mono.just("cached-value"))          // replace the failed sequence
                .onErrorReturn("default");                               // never reached here: already recovered

        System.out.println(value.block());
    }
}
```

**Pitfall:** `onErrorResume` does not "continue where it left off". For a `Flux` that fails at element 3 of 10, the fallback publisher replaces the rest of the sequence, so elements 4 to 10 are never produced. Similarly `retryWhen(Retry.backoff(...))` resubscribes to the source from the start, so a non-idempotent source (a `POST`, a message publish) executes its side effect again on every retry, and when retries run out the original failure arrives wrapped in a retry-exhausted exception rather than as the original type.

## Snippet 6: testing with StepVerifier

`StepVerifier` subscribes to a Publisher and checks the sequence of signals (`expectNext`, `expectError`, `expectComplete`) in order; `verify()` blocks until a terminal signal. `withVirtualTime` swaps Reactor's scheduler for a virtual clock so `thenAwait(Duration)` can skip an hour without sleeping. The JDK-only version below does the underlying job by hand: record every signal into a list, then compare to the expected list.

```java
// Requires io.projectreactor:reactor-core and io.projectreactor:reactor-test; not compiled in this repo
import java.time.Duration;
import org.junit.jupiter.api.Test;
import reactor.core.publisher.Flux;
import reactor.test.StepVerifier;

class FluxContractTest {

    @Test
    void mapsAndCompletes() {
        StepVerifier.create(Flux.just("a", "b").map(String::toUpperCase))
                .expectNext("A", "B")
                .expectComplete()
                .verify();
    }

    @Test
    void failsAfterFirstElement() {
        Flux<Integer> source = Flux.concat(Flux.just(1), Flux.error(new IllegalStateException("boom")));
        StepVerifier.create(source)
                .expectNext(1)
                .expectErrorMessage("boom")
                .verify();
    }

    @Test
    void respectsDemand() {
        StepVerifier.create(Flux.range(1, 3), 1)   // initial request of 1
                .expectNext(1)
                .thenRequest(2)
                .expectNext(2, 3)
                .expectComplete()
                .verify();
    }

    @Test
    void skipsTimeWithVirtualClock() {
        StepVerifier.withVirtualTime(() -> Flux.interval(Duration.ofHours(1)).take(2))
                .expectSubscription()
                .thenAwait(Duration.ofHours(2))
                .expectNext(0L, 1L)
                .expectComplete()
                .verify();
    }
}
```

JDK-only signal recorder (a hand-rolled verifier over `Flow.Publisher`):

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Flow;
import java.util.concurrent.SubmissionPublisher;
import java.util.function.Consumer;

public class SignalRecorderDemo {

    static final class Recorder<T> implements Flow.Subscriber<T> {
        final List<String> signals = new ArrayList<>();

        @Override
        public void onSubscribe(Flow.Subscription s) {
            s.request(Long.MAX_VALUE);
        }

        @Override
        public void onNext(T item) {
            signals.add("next:" + item);
        }

        @Override
        public void onError(Throwable t) {
            signals.add("error:" + t.getClass().getSimpleName() + ":" + t.getMessage());
        }

        @Override
        public void onComplete() {
            signals.add("complete");
        }
    }

    static List<String> record(Consumer<SubmissionPublisher<Integer>> emit) {
        // Runnable::run makes delivery synchronous, so no sleeps or latches are needed
        SubmissionPublisher<Integer> publisher = new SubmissionPublisher<>(Runnable::run, 16);
        Recorder<Integer> recorder = new Recorder<>();
        publisher.subscribe(recorder);
        emit.accept(publisher);
        return recorder.signals;
    }

    static void expect(String name, List<String> actual, List<String> expected) {
        if (actual.equals(expected)) {
            System.out.println("PASS " + name);
        } else {
            System.out.println("FAIL " + name + ": expected " + expected + " but was " + actual);
        }
    }

    public static void main(String[] args) {
        List<String> ok = record(p -> {
            p.submit(1);
            p.submit(2);
            p.close();
        });
        expect("emits 1,2 then completes", ok, List.of("next:1", "next:2", "complete"));

        List<String> failing = record(p -> {
            p.submit(1);
            p.closeExceptionally(new IllegalStateException("boom"));
        });
        expect("fails after first element", failing, List.of("next:1", "error:IllegalStateException:boom"));

        List<String> wrongExpectation = record(p -> {
            p.submit(1);
            p.submit(2);
            p.close();
        });
        expect("deliberately wrong expectation", wrongExpectation, List.of("next:1", "complete"));
    }
}
```

Observed output (`java SignalRecorderDemo`):

```text
PASS emits 1,2 then completes
PASS fails after first element
FAIL deliberately wrong expectation: expected [next:1, complete] but was [next:1, next:2, complete]
```

**Pitfall:** forgetting the terminal `verify()` (or `verifyComplete()`): `StepVerifier.create(flux).expectNext(1)` only describes expectations and never subscribes, so the test passes even if the Flux is broken. A second trap is `withVirtualTime` with a Flux built outside the supplier lambda: the timers were already created on the real clock, so `thenAwait` has no effect and the test either hangs until timeout or runs for real hours.

## Verification notes

- Compiled snippets: `FlowRequestDemo`, `LazyAssemblyDemo`, `DropOnOverflowDemo`, `ThreadHopDemo`, `FlowErrorDemo`, `SignalRecorderDemo` (6 total), each compiled with `javac --release 21 -proc:none` and run with `java`.
- Not compiled (need Reactor): `ReactorAssembly`, `ReactorBackpressure`, `ReactorSchedulers`, `ReactorErrors`, and the `FluxContractTest` class.
- The outputs are order-stable by construction: snippets 1 and 2 print from a single thread at a time, snippet 3 withholds demand until all offers are done, snippet 4 waits for `onSubscribe` before submitting, and snippets 5 and 6 use a synchronous executor. Thread names in snippet 4 are fixed by the custom `ThreadFactory`.
