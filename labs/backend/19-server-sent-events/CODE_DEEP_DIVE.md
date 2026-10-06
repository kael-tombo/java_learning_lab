# Code Deep Dive: Server-Sent Events in Spring

## SseEmitter broadcast endpoint

```java
@RestController
public class NotificationController {
    private final CopyOnWriteArrayList<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream() {
        SseEmitter emitter = new SseEmitter(0L);       // no timeout for long streams
        emitters.add(emitter);
        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError(e -> emitters.remove(emitter));
        return emitter;
    }

    public void broadcast(String event, Object payload) {
        for (SseEmitter e : emitters) {
            try {
                e.send(SseEmitter.event().name(event).data(payload));
            } catch (IOException ex) {
                emitters.remove(e);                    // client gone; drop quietly
            }
        }
    }
}
```

Pitfalls: `CopyOnWriteArrayList` copies on every removal — fine at thousands of
clients, not millions. `emitter.send` is not thread-safe per instance; guard
sending if multiple threads publish simultaneously.

## Resumable stream with Last-Event-ID

```java
@GetMapping("/orders/stream")
public SseEmitter orderStream(@RequestHeader(value = "Last-Event-ID", required = false) String lastId) {
    SseEmitter emitter = new SseEmitter(0L);
    long cursor = lastId == null ? currentOffset() : Long.parseLong(lastId);
    executor.execute(() -> {
        for (Event e : eventLog.eventsAfter(cursor)) {     // durable backlog
            try {
                emitter.send(SseEmitter.event()
                        .id(String.valueOf(e.offset()))
                        .name("order-update")
                        .data(e.payload()));
            } catch (IOException io) { return; }           // stop; client will reconnect
        }
    });
    return emitter;
}
```

Pitfall: skipping the resume logic and always streaming only live events means
every reconnect silently loses events that arrived during the gap — the exact
bug "customers report missing notifications after airport Wi-Fi."

## Heartbeat via Scheduled task

```java
@Scheduled(fixedDelay = 15_000)
public void heartbeat() {
    for (SseEmitter e : emitters) {
        try {
            e.send(SseEmitter.event().comment("ping"));    // IGNORED by EventSource
        } catch (Exception ignored) { emitters.remove(e); }
    }
}
```

Pitfall: WebFlux `Flux<ServerSentEvent>` supports `.comment("ping")` similarly;
MVC's `SseEmitter.event().comment(...)` emits the same `: ping` line. Without
it, nginx/ELB idle timeouts sever clients mid-stream.

## Reactive variant with keepalive

```java
@GetMapping(value = "/flux", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<Order>> fluxStream() {
    return Flux.merge(liveOrders, heartbeat())
            .map(o -> ServerSentEvent.<Order>builder()
                    .id(o.id()).event("order").data(o).build());
}

private Flux<ServerSentEvent<Order>> heartbeat() {
    return Flux.interval(Duration.ofSeconds(15))
            .map(t -> ServerSentEvent.<Order>builder().comment("ping").build());
}
```

Pitfall: `Flux.interval` emits `Long`; mapping must return the same generic
type — a common compile error is returning a raw comment event mixing with
typed events.

## Backpressure policy

```java
Sinks.Many<Order> sink = Sinks.many().multicast().onBackpressureBuffer(256);

Flux.from(sink.asFlux())
    .onBackpressureDrop(dropped -> metrics.counter("sse.dropped").increment())
    .subscribe();
```

Pitfall: unbounded buffering lets a slow consumer grow the heap until OOM;
dropping silently corrupts the client's view. Emit a `resync-required` event
when drops occur so clients refetch state instead of continuing with a
gapped timeline.

## Client-side reconnect

```javascript
const es = new EventSource("/orders/stream");
es.addEventListener("order-update", e => render(JSON.parse(e.data)));
es.onerror = () => {
  // EventSource auto-retries with Last-Event-ID; surface state in UI
  statusEl.textContent = "reconnecting…";
};
```

Pitfall: closing `es` in `onerror` defeats auto-reconnect; leave it open and
let the spec handle the backoff.
