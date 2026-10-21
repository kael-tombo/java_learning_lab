# Interview Questions: Netty Framework

## Company-Specific Focus

### Google
- Netty: asynchronous event-driven network application framework
- ChannelHandler: processing I/O events
- ChannelPipeline: chain of ChannelHandlers
- EventLoop: thread that handles I/O events for channels

### Microsoft
- Netty vs .NET Kestrel/ASP.NET Core
- NIO integration: Netty is built on top of NIO

### Amazon
- Netty for high-performance microservices: gRPC, HTTP/2
- ByteBuf: Netty's buffer API (pooled, direct buffers)
- Netty's memory management: reducing GC overhead

### Meta
- EventLoopGroup: thread group managing EventLoops
- Bootstrapping: ServerBootstrap, Bootstrap
- ChannelInitializer: configuring the pipeline

### Apple
- Netty in production: used by many large-scale systems
- Backpressure: Netty handles writability changes
- SSL/TLS: SslHandler for secure connections

### Oracle
- Netty is a third-party framework (not in JDK)
- Used by: Spring WebFlux, gRPC, Apache Cassandra, Apache Spark
- Netty is the foundation of reactive networking in Java

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Netty is a networking framework) |

## Real Production Scenarios
- **Netflix**: Netty-based Zuul API gateway handles millions of requests per second
- **LinkedIn**: Netty for real-time messaging infrastructure

## Interview Patterns & Tips
- **EventLoop**: each channel is assigned to an EventLoop for its lifetime
- **ChannelPipeline**: handlers are executed in order
- **ByteBuf**: poolable, reference-counted buffer
- **Bootstrap**: helper class for channel initialization

## Deep Dive Questions
- **EventLoop**: How does EventLoop handle multiple channels?
- **ChannelPipeline**: How do handlers process events?
- **ByteBuf**: How does ByteBuf differ from ByteBuffer?
- **Pooled buffers**: How does Netty's buffer pooling work?
- **Backpressure**: How does Netty handle write buffer backpressure?