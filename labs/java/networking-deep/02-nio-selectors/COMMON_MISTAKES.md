# NIO Selectors -- Common Mistakes

## Top 15 Common Mistakes

### 1. Blocking in Event Loop
Performing blocking operations (database calls, file I/O) in the event loop thread blocks all other connections.

### 2. Ignoring Connection Timeouts
Not setting connect and read timeouts causes threads to hang indefinitely on unresponsive peers.

### 3. Resource Leaks
Failing to close sockets, channels, or selectors causes file descriptor exhaustion.

### 4. Thread Safety on Shared State
Network handlers sharing mutable state without synchronization causes race conditions.

### 5. Synchronous Thinking in Async Code
Writing blocking code in asynchronous frameworks defeats the purpose of async I/O.

### 6. Buffer Under-Read
Assuming read() returns the full message in one call. TCP is a stream protocol.

### 7. Buffer Over-Read
Reading beyond the message boundary in the buffer, mixing data from different messages.

### 8. Ignoring Backpressure
Not implementing backpressure causes producers to overwhelm consumers with data.

### 9. Incorrect Thread Pool Sizing
Too many threads cause context switching overhead; too few cause queuing delays.

### 10. Not Handling Partial Writes
write() may not send all bytes in one call. Must check return value.

### 11. Missing Heartbeat Detection
Not detecting dead connections causes resource leaks and incorrect behavior.

### 12. Hardcoded Network Configuration
Using hardcoded hostnames, ports, and timeouts reduces deployment flexibility.

### 13. Ignoring Connection Reset
Not handling SocketException (connection reset) causes unexpected failures.

### 14. Overlooking Protocol Framing
Sending messages without length prefixes or delimiters makes parsing ambiguous.

### 15. Not Testing Under Load
Production failures often occur only under load. Load testing is essential.
