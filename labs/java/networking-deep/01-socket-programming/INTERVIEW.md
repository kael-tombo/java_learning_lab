# Interview Questions: Socket Programming

## Company-Specific Focus

### Google
- Socket: endpoint for communication between two machines
- TCP sockets: Socket (client), ServerSocket (server)
- UDP sockets: DatagramSocket, DatagramPacket

### Microsoft
- Java sockets vs .NET TcpClient/TcpListener
- Socket options: SO_TIMEOUT, SO_REUSEADDR, TCP_NODELAY

### Amazon
- Connection pooling: reusing sockets for efficiency
- Socket timeouts: connect timeout, read timeout
- Non-blocking sockets: setting channel to non-blocking mode

### Meta
- BIO (Blocking I/O): thread per connection model
- Socket state: connected, closed, bound
- Half-close: shutdownOutput vs shutdownInput

### Apple
- SSL/TLS: SSLSocket for secure connections
- SocketChannel: NIO channel for socket communication

### Oracle
- java.net.Socket and ServerSocket
- java.net.DatagramSocket for UDP
- TCP vs UDP: reliability vs performance
- Socket exceptions: ConnectException, BindException, SocketTimeoutException

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — socket programming is networking) |

## Real Production Scenarios
- **Cloudflare**: TCP connection pool exhaustion caused 502 errors — increased pool size
- **Uber**: Socket timeout not set caused threads to block indefinitely — setting SO_TIMEOUT resolved

## Interview Patterns & Tips
- **TCP**: reliable, ordered, connection-oriented
- **UDP**: unreliable, unordered, connectionless
- **Socket timeout**: always set connect and read timeouts
- **TCP_NODELAY**: disable Nagle's algorithm for low-latency

## Deep Dive Questions
- **TCP handshake**: How does TCP three-way handshake work?
- **Socket state machine**: What are the states of a TCP socket?
- **SO_TIMEOUT**: What happens when a read times out?
- **TCP_NODELAY**: What is Nagle's algorithm and why disable it?
- **Half-close**: What happens when one end closes the connection?