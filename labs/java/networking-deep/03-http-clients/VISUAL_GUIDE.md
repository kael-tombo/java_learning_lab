# HTTP Clients (Java 11+) -- Visual Guide
## Network Architecture Diagram
`
    +-----------+     +-----------+     +-----------+
    |  Client   | <-> |  Network  | <-> |  Server   |
    | Application|   |  Layer    |   | Application|
    +-----------+     +-----------+     +-----------+
    | TCP/IP   |     | IP Routing|     | TCP/IP   |
    | Stack    |     | Switching |     | Stack    |
    +-----------+     +-----------+     +-----------+

## Connection Lifecycle
CLOSED -> SYN_SENT -> ESTABLISHED -> FIN_WAIT_1 -> FIN_WAIT_2 -> TIME_WAIT -> CLOSED

## Threading Models
### Thread-per-Connection
Main Thread -> Accept -> Worker Thread 1 -> Handle Client 1
                        -> Worker Thread 2 -> Handle Client 2
                        -> Worker Thread N -> Handle Client N

### Event Loop (Reactor)
Event Loop -> Selector.select() -> OP_ACCEPT -> Accept Handler
                                 -> OP_READ -> Read Handler
                                 -> OP_WRITE -> Write Handler

## Data Flow
Client App -> Socket -> TCP -> IP -> Network -> IP -> TCP -> Socket -> Server App
                                                                              
Each layer adds headers and passes to the next layer down (sending) or up (receiving).
