# Interview Questions: gRPC Networking

## Company-Specific Focus

### Google
- gRPC: high-performance RPC framework using HTTP/2 and Protocol Buffers
- Service definition: .proto file defining RPC methods
- Four call types: unary, server streaming, client streaming, bidirectional streaming

### Microsoft
- gRPC vs Azure Service Bus/REST
- HTTP/2: multiplexed connections for efficiency

### Amazon
- gRPC in microservices: type-safe, high-performance inter-service communication
- Load balancing: gRPC requires L7 (not L4) load balancing
- TLS: mutual TLS for service-to-service authentication

### Meta
- Deadlines/timeouts: client-side deadline propagation
- Interceptors: cross-cutting concerns (logging, metrics, auth)
- Error handling: gRPC status codes

### Apple
- Streaming: server streaming for real-time data
- Bidirectional streaming: full-duplex communication
- Client-side streaming: aggregating data on the server

### Oracle
- gRPC uses HTTP/2 and Protocol Buffers
- gRPC-Java: the Java gRPC implementation
- Service stubs: generated blocking and async stubs
- Channels: managing connections to gRPC servers

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — gRPC is a framework for service communication) |

## Real Production Scenarios
- **Uber**: gRPC for inter-service communication reduced latency by 30% over REST
- **Netflix**: gRPC with bidirectional streaming for real-time recommendation updates

## Interview Patterns & Tips
- **Protocol Buffers**: gRPC uses Protobuf as the interface definition language
- **HTTP/2**: built-in multiplexing, header compression, streaming
- **Stubs**: auto-generated client and server code
- **Deadline**: client sets timeout propagated server-side

## Deep Dive Questions
- **HTTP/2**: How does gRPC leverage HTTP/2 features?
- **Streaming**: How does gRPC implement server/client streaming?
- **Load balancing**: Why does gRPC need client-side load balancing?
- **Interceptors**: How do gRPC interceptors work?
- **Performance**: How does gRPC compare to REST for service-to-service communication?