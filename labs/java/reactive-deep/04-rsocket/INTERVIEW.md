# Interview Questions: RSocket

## Company-Specific Focus

### Google
- RSocket: binary protocol for reactive communication
- Four interaction models: request-response, request-stream, fire-and-forget, channel
- Multiplexing: multiple streams over a single connection

### Microsoft
- RSocket vs SignalR (.NET): similar real-time communication
- Backpressure: RSocket natively supports reactive backpressure

### Amazon
- RSocket for microservices: alternative to HTTP/gRPC
- Brokers: RSocket brokers for routing and load balancing
- Integration: Spring RSocket for Spring Boot applications

### Meta
- Channel: bidirectional streaming model
- Lease: reactive backpressure for connection acceptance
- Resume: connection resilience with token-based resumption

### Apple
- Multiplexing: efficient connection use
- Reactive streams: RSocket carries reactive streams semantics
- Well-known transports: TCP, WebSocket

### Oracle
- RSocket is a protocol (not JDK standard)
- Reactive Streams foundation: RSocket implements reactive streams
- Java implementation: RSocket-Java

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — RSocket is a communication protocol) |

## Real Production Scenarios
- **Netflix**: RSocket for real-time recommendation updates using bidirectional streaming
- **LinkedIn**: RSocket with backpressure for event ingestion pipeline

## Interview Patterns & Tips
- **Request-Response**: 1-to-1 (like HTTP)
- **Request-Stream**: 1-to-N (like SSE)
- **Fire-and-Forget**: 1-to-0 (no response)
- **Channel**: N-to-N (bidirectional)

## Deep Dive Questions
- **Protocol framing**: How is an RSocket frame structured?
- **Stream IDs**: How are streams multiplexed?
- **Resume**: How does RSocket resume a broken connection?
- **Backpressure**: How does demand flow through RSocket?
- **RSocket vs gRPC**: How do the protocols compare?