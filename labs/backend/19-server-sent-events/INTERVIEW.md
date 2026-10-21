# Interview: SSE

Q: SSE vs WebSocket? A: SSE is simpler, auto-reconnects, unidirectional. WebSocket is bidirectional, lower latency, full-duplex.

Q: How to handle SSE backpressure? A: WebFlux handles natively via Reactor demand signals. MVC requires manual queue management.
