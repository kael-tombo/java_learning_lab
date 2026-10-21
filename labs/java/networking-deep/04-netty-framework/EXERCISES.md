# Netty Framework -- Exercises
## Beginner Exercises
### Exercise 1: Basic Server
Implement a simple echo server that responds with the same message it receives.

### Exercise 2: Basic Client
Write a client that connects to the echo server and sends multiple messages.

### Exercise 3: Multiple Clients
Test your server with multiple concurrent clients. Verify all receive correct responses.

## Intermediate Exercises
### Exercise 4: Thread Pool Server
Replace thread-per-connection with a fixed thread pool. Measure memory savings.

### Exercise 5: Timeout Handling
Add connection timeout and read timeout to your server implementation.

### Exercise 6: Protocol Design
Design a simple application protocol (length-prefixed messages) and implement it.

## Advanced Exercises
### Exercise 7: Non-Blocking IO
Rewrite your server using NIO Selector with a single thread.

### Exercise 8: Connection Pool
Implement a client-side connection pool that manages reusable connections.

### Exercise 9: Performance Benchmark
Benchmark throughput: thread-per-connection vs thread pool vs NIO event loop.

### Exercise 10: Fault Tolerance
Add reconnection logic, heartbeat detection, and graceful shutdown.

## Challenge Exercise
Build a simple HTTP server from scratch that handles GET/POST requests, serves static files, and supports keep-alive connections.
