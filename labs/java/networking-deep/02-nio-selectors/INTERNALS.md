# NIO Selectors -- Internal Implementation

## Internal Architecture

### 1. Connection Lifecycle
- Connection established (TCP handshake complete)
- TLS handshake (if encrypted)
- Protocol negotiation (HTTP/2, WebSocket upgrade)
- Data exchange with keepalive
- Connection teardown (FIN handshake)

### 2. Event Demultiplexing
The event loop uses operating system mechanisms:
- select(): cross-platform, limited to 1024 FDs
- poll(): no FD limit, O(n) scanning
- epoll (Linux): O(1) event notification
- kqueue (macOS): O(1) event notification
- IOCP (Windows): completion port model

### 3. Buffer Architecture
- DirectByteBuffer for I/O operations (off-heap)
- Heap buffers for application processing
- Reference counting for buffer lifecycle
- Pooled allocators for performance

### 4. Threading Internals
- Boss threads: accept connections, register with workers
- Worker threads: read/write data, execute pipeline
- Event loop: process ready channels in single thread
- Task queue: schedule asynchronous tasks

### 5. Memory Management
- Direct memory pooling reduces GC pressure
- Reference counting prevents memory leaks
- Watermark thresholds for flow control
- Configurable buffer allocation strategies
