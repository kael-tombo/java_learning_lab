# Socket Programming -- History
## Historical Evolution

### Early Networking (1980s)
Berkeley sockets introduced in BSD 4.2 (1983). Became the standard API for TCP/IP programming.

### Java Networking (1995-1997)
Java 1.0 introduced java.net.Socket and java.net.ServerSocket.
Basic blocking I/O model with thread-per-connection pattern.

### Java NIO (2002 - JDK 1.4)
New I/O (NIO) introduced with Selector, SocketChannel, and ByteBuffer.
Enabled non-blocking I/O and multiplexed connections in Java.

### Netty Framework (2008-Present)
Netty 3.x released as a high-performance NIO framework.
Netty 4.x (2013) introduced threading model improvements and ByteBuf.
Netty 5.x abandoned; Netty 4 continues as the primary version.

### Java HTTP Client (2018 - JDK 11)
java.net.http.HttpClient introduced as a modern HTTP client.
Supports HTTP/2, WebSocket, and both sync/async programming models.

### gRPC (2015-Present)
gRPC developed by Google, based on HTTP/2 and Protocol Buffers.
Supports streaming, bidirectional communication, and polyglot services.

### Virtual Threads (2023 - JDK 21)
Project Loom's virtual threads enable thread-per-request without overhead.
Simplifies concurrent programming while maintaining scalability.
