package com.learning.reactive;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class Lab {

    public static void main(String[] args) throws Exception {
        System.out.println("=== Reactive Streams Lab ===\n");

        flowApi();
        submissionPublisher();
        backpressureStrategies();
        operators();
        schedulersExample();
        hotVsCold();
    }

    static void flowApi() {
        System.out.println("--- java.util.concurrent.Flow API ---");

        class SimplePublisher implements Flow.Publisher<String> {
            final List<String> items;
            SimplePublisher(List<String> items) { this.items = items; }

            public void subscribe(Flow.Subscriber<? super String> sub) {
                sub.onSubscribe(new Flow.Subscription() {
                    int index = 0;
                    volatile boolean cancelled = false;

                    public void request(long n) {
                        for (int i = 0; i < n && index < items.size() && !cancelled; i++) {
                            sub.onNext(items.get(index++));
                        }
                        if (index >= items.size() && !cancelled) sub.onComplete();
                    }

                    public void cancel() { cancelled = true; }
                });
            }
        }

        System.out.println("  Publisher emits 3 items:");
        new SimplePublisher(List.of("A", "B", "C")).subscribe(new Flow.Subscriber<>() {
            public void onSubscribe(Flow.Subscription s) { s.request(Long.MAX_VALUE); }
            public void onNext(String item) { System.out.println("    " + item); }
            public void onError(Throwable t) {}
            public void onComplete() { System.out.println("    Done"); }
        });
    }

    static void submissionPublisher() throws InterruptedException {
        System.out.println("\n--- SubmissionPublisher (Built-in) ---");
        var publisher = new SubmissionPublisher<String>();
        var results = new CopyOnWriteArrayList<String>();

        publisher.subscribe(new Flow.Subscriber<>() {
            Flow.Subscription s;
            public void onSubscribe(Flow.Subscription s) { this.s = s; s.request(3); }
            public void onNext(String item) { results.add("Got: " + item); s.request(1); }
            public void onError(Throwable t) {}
            public void onComplete() { results.add("Complete"); }
        });

        publisher.submit("X"); publisher.submit("Y"); publisher.submit("Z");
        publisher.close();
        Thread.sleep(100);
        results.forEach(r -> System.out.println("  " + r));
        System.out.println("  Max buffer: " + publisher.getMaxBufferCapacity());
    }

    static void backpressureStrategies() {
        System.out.println("\n--- Backpressure Strategies ---");

        class BufferedSubscriber implements Flow.Subscriber<Integer> {
            Flow.Subscription s;
            final String name;
            BufferedSubscriber(String name) { this.name = name; }
            public void onSubscribe(Flow.Subscription s) { this.s = s; s.request(2); }
            public void onNext(Integer i) {
                System.out.println("  " + name + " processing " + i);
                s.request(1);
            }
            public void onError(Throwable t) {}
            public void onComplete() { System.out.println("  " + name + " done"); }
        }

        var pub = new SubmissionPublisher<Integer>();
        pub.subscribe(new BufferedSubscriber("Slow1"));
        pub.subscribe(new BufferedSubscriber("Slow2"));
        for (int i = 0; i < 5; i++) pub.submit(i);
        pub.close();
        try { Thread.sleep(200); } catch (InterruptedException e) {}
        System.out.println("""
  Strategies:
  BUFFER - queue overflow items
  DROP   - discard overflow
  LATEST - keep only latest
  ERROR  - throw on overflow
    """);
    }

    static void operators() {
        System.out.println("\n--- Reactive Operators ---");

        class SimFlux<T> {
            final List<T> items;
            SimFlux(List<T> items) { this.items = items; }
            SimFlux<T> filter(java.util.function.Predicate<T> p) {
                return new SimFlux<>(items.stream().filter(p).toList());
            }
            <R> SimFlux<R> map(java.util.function.Function<T, R> f) {
                return new SimFlux<>(items.stream().map(f).toList());
            }
            SimFlux<T> skip(int n) {
                return new SimFlux<>(items.subList(Math.min(n, items.size()), items.size()));
            }
            SimFlux<T> take(int n) {
                return new SimFlux<>(items.subList(0, Math.min(n, items.size())));
            }
            List<T> collect() { return items; }
        }

        var flux = new SimFlux<>(List.of(1, 2, 3, 4, 5, 6));
        System.out.println("  Original:    " + flux.collect());
        System.out.println("  filter(even): " + flux.filter(n -> n % 2 == 0).collect());
        System.out.println("  map(sq):     " + flux.map(n -> n * n).collect());
        System.out.println("  skip(2):     " + flux.skip(2).collect());
        System.out.println("  take(3):     " + flux.take(3).collect());
        System.out.println("  map+filter:  " + flux.map(n -> n + 1).filter(n -> n % 3 == 0).collect());
    }

    static void schedulersExample() {
        System.out.println("\n--- Schedulers & Threading ---");
        var pool = Executors.newFixedThreadPool(3);

        System.out.println("  Tasks executing on thread pool:");
        for (int i = 0; i < 3; i++) {
            int task = i;
            pool.submit(() -> System.out.println("    Task " + task + " on " + Thread.currentThread().getName()));
        }
        pool.shutdown();

        System.out.println("""
  Reactor schedulers:
  Schedulers.parallel()       - CPU-bound (size = cores)
  Schedulers.boundedElastic() - I/O-bound (bounded pool)
  Schedulers.single()         - ordered single thread
  Schedulers.immediate()      - current thread

  subscribeOn: scheduler for source emission
  publishOn:   scheduler for downstream operators
    """);
    }

    static void hotVsCold() {
        System.out.println("--- Hot vs Cold Publishers ---");
        System.out.println("""
  Cold: each subscriber gets its own independent stream
    e.g., Flux.just, Flux.fromIterable
    Subscriber 1: ---1---2---3---|
    Subscriber 2:            ---1---2---3---|

  Hot:  all subscribers share the same stream
    e.g., Sinks.many, DirectProcessor
    Subscriber 1: ---1---2---3---|
    Subscriber 2:            ---3---|

  Connectable: cold but can be made hot via .publish().connect()
  Cache:       cold but materialized (replay for late subscribers)
    """);
    }
}
