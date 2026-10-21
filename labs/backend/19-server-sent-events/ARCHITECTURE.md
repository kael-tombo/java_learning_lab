# Architecture: Server-Sent Events

`
Client â”€â”€â–¶ HTTP GET /events/stream
              â”‚
              â–¼
        [SSE Controller]
              â”‚
        [Event Publisher]
              â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  Event Sources     â”‚
    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
    â”‚ - Timer events     â”‚
    â”‚ - Database changes â”‚
    â”‚ - Queue messages   â”‚
    â”‚ - External APIs    â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â”‚
              â–¼
        text/event-stream
              â”‚
              â–¼
        Client receives events
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\19-server-sent-events "STEP_BY_STEP.md") @"
# Step by Step: Server-Sent Events

## Step 1: MVC SSE
`java
@GetMapping(path = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter stream() {
    SseEmitter emitter = new SseEmitter(60_000L);
    executor.execute(() -> {
        for (int i = 0; i < 10; i++) {
            emitter.send(SseEmitter.event().id(String.valueOf(i)).data("Event " + i));
            Thread.sleep(1000);
        }
        emitter.complete();
    });
    return emitter;
}
`

## Step 2: WebFlux SSE
`java
@GetMapping(produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> stream() {
    return Flux.interval(Duration.ofSeconds(1))
        .map(i -> ServerSentEvent.<String>builder()
            .id(String.valueOf(i))
            .event("tick")
            .data("Tick #" + i)
            .build());
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\19-server-sent-events "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: Server-Sent Events

## SseEmitter Internals

SseEmitter uses a DeferredResult under the hood. When created:
1. Sets response headers (Content-Type: text/event-stream)
2. Returns PENDING status to Servlet container
3. Calls to send() write to response OutputStream
4. Flushes after each event for real-time delivery

## WebFlux SSE

Spring WebFlux uses the Flux<ServerSentEvent<T>> return type:
1. WebFlux detects text/event-stream produces
2. ServerSentEventHttpMessageWriter serializes events
3. Each event is flushed to the response sink
4. Backpressure is handled via Reactor's demand mechanism
