# gRPC Networking -- How It Works
## Detailed Mechanical Explanation

### 1. Socket Creation and Binding
A server socket is created and bound to a port. The operating system assigns
the socket to the specified port and starts listening for incoming connections.

### 2. Connection Establishment
The TCP three-way handshake establishes a connection between client and server.
SYN -> SYN-ACK -> ACK. After this, data can flow bidirectionally.

### 3. Data Transmission
Data is sent as a stream of bytes over the established TCP connection.
TCP ensures ordered, reliable delivery with retransmission of lost packets.

### 4. Connection Teardown
FIN or RST packets close the connection. FIN indicates graceful shutdown.
RST indicates abnormal termination. Resources are released after close.

### 5. Non-Blocking Operation
Non-blocking sockets return immediately from read/write operations.
The Selector notifies when data is available or space is free to write.

### 6. Event Loop Processing
The event loop repeatedly: select for events, process ready channels,
execute queued tasks, and repeat. This single-threaded model avoids
context switching and synchronization overhead.
