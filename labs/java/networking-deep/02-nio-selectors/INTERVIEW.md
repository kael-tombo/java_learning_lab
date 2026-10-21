# Interview Questions: NIO Selectors

## Company-Specific Focus

### Google
- NIO Selector: multiplexing multiple channels with a single thread
- SelectableChannel: channels that can be used with Selector
- SelectionKey: represents a channel's registration with a Selector

### Microsoft
- Java NIO vs .NET async I/O
- Selector: OS-level event notification (epoll, kqueue, select)

### Amazon
- Reactor pattern: single thread handles many connections
- NIO + Netty: Netty is built on top of NIO Selectors
- Performance: handling tens of thousands of connections with a few threads

### Meta
- OP_ACCEPT, OP_CONNECT, OP_READ, OP_WRITE: interest sets
- select() vs selectNow(): blocking vs non-blocking selector operation
- wakeup(): waking up a blocked selector

### Apple
- kqueue: macOS/BSD event notification mechanism
- epoll vs kqueue: platform-specific selector implementations

### Oracle
- java.nio.channels.Selector, SelectionKey, SelectableChannel
- SelectorProvider: platform-specific provider
- Selector.wakeup(): interrupt a blocked select operation

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — NIO Selectors are networking architecture) |

## Real Production Scenarios
- **Netflix**: NIO Selector-based event loop handles 50K+ concurrent connections per instance
- **Cloudflare**: Selector.wakeup() race condition caused missed events — careful handling required

## Interview Patterns & Tips
- **Reactor pattern**: one thread handles multiple connections
- **select() vs poll() vs epoll()**: Linux I/O multiplexing evolution
- **Channel registration**: register channels with a Selector for interest events
- **Selector loop**: typical pattern: select() -> process keys -> cancel -> repeat

## Deep Dive Questions
- **epoll vs select**: Why is epoll more scalable than select?
- **Selector loop**: Write the typical NIO selector event loop
- **SelectionKey**: What information does a SelectionKey hold?
- **wakeup()**: How does Selector.wakeup() work?
- **Platform implementations**: How does Selector differ across Linux, macOS, Windows?