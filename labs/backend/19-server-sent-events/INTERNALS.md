# Internals: Server-Sent Events

## Netty Event Loop
WebFlux SSE runs on Netty event loop threads. Each connection gets:
1. Reactor Netty handler
2. Response body encoded as text/event-stream
3. Chunked transfer encoding for streaming

## Backpressure
Reactor's demand signals control event emission rate. When client reads slowly, backpressure slows server-side event production.
