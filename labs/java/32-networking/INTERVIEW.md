# Interview Questions: Networking

## Company-Specific Focus

### Google
- Socket programming in Java: TCP and UDP sockets, ServerSocket
- NIO for high throughput networking: Selectors, Channels, Buffers
- gRPC: building high-performance RPC services over HTTP/2

### Microsoft
- Java networking vs C# socket programming
- HTTP client in Java 11+: making REST calls
- SSL/TLS in Java: SSLSocket, SSLContext, trust managers

### Amazon
- Netty vs NIO: when to use a framework vs raw NIO at scale
- HTTP/2: performance impact on service communication
- Connection pooling in HTTP clients: keep alive, retries

### Meta
- Non-blocking IO vs blocking: production scenarios
- DNS resolution in Java: InetAddress, caching
- Socket timeout: best practices at scale

### Apple
- Using DgramSocket for low-level network tests
- The URL class and URI handling nuances
- Secure socket configuration

### Oracle
- The java.net package: all core networking APIs
- SocketImpl: the abstract SPI for custom socket implementations
- Java 11 HttpClient: the modern replacement for HttpURLConnection
- The security of the TLS stack in the JDK

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 207 Course Schedule | Medium | Amazon, Google, Apple | Dependency graph resembles network connections |
| 210 Course Schedule II | Medium | Amazon, Google | Topological ordering of service calls |
| 127 Word Ladder | Hard | Amazon, Apple | BFS traversal |
| 399 Evaluate Division | Medium | Amazon, Google | Weighted graph traversal |
| 207 Course Schedule | Medium | Amazon, Microsoft, Google | Graph relationships |

## Real Production Scenarios
- **Cloudflare**: TCP connection pool exhaustion in the load balancer — increased max connections
- **Netflix**: TLS handshake latency added 200ms to each request — upgraded to TLS 1.3
- **LinkedIn**: DNS caching caused stale mapping after a failover — set networkaddress.cache.ttl=0

## Interview Patterns & Tips
- **Socket timeout**: Always set connect and read timeouts when using java.net.Socket.
- **HTTP/2**: Multiplexing reduces latency over HTTP/1.1 head-of-line blocking.
- **SSLContext**: Use TLSv1.2+ and avoid deprecated protocols.

## Deep Dive Questions
- **JVM networking**: How does the JVM implement a Socket.connect() call?
- **NIO**: How does a Selector work at the OS level? (epoll on Linux, kqueue on macOS)
- **Performance**: How does JVM handle high throughput networking?
- **Thread model**: Thread per connection vs Reactor based event loop.
- **Zero copy**: How does FileChannel.transferTo optimize network I/O?