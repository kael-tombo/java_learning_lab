# Performance: Server-Sent Events

- Each SSE connection consumes server resources (thread pool)
- WebFlux SSE scales better than MVC SseEmitter
- Use Flux.interval for periodic events instead of Thread.sleep
- Configure connection timeouts and keepalive
- Monitor active connection count
- Use backpressure-aware event sources
- Consider compression for large event payloads
