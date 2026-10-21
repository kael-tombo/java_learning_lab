# Netty Framework -- Mental Models
## Key Mental Models for Understanding Networking

### Model 1: The Telephone System
TCP is like a telephone call. You dial (establish connection), talk (exchange data),
and hang up (close connection). UDP is like sending postcards - you send without
knowing if it arrives.

### Model 2: The Restaurant Kitchen
Thread-per-connection is like each waiter handling one table.
Event loop is like a single expo chef coordinating all orders.

### Model 3: The Highway System
TCP is a controlled-access highway: on-ramps (connection), lanes (streams),
traffic lights (flow control), and exits (teardown).

### Model 4: The Water Pipe
Data flows through connections like water through pipes. Backpressure is
like a valve that restricts flow when the receiving end is full.

### Model 5: The Post Office
IP is the postal service delivering envelopes (packets). TCP is registered mail
with delivery confirmation. UDP is regular mail - no guarantees.
