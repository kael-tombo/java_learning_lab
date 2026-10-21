# Interview Questions: Circular Buffers

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| (No dedicated LeetCode problems — system design focus) | — | Google, Amazon, Meta, Microsoft, Apple | Producer-consumer / ring buffer |
| [LC 622 Design Circular Queue](https://leetcode.com/problems/design-circular-queue/) | Medium | Amazon, Microsoft, Google, Meta | Array-based ring buffer |
| [LC 641 Design Circular Deque](https://leetcode.com/problems/design-circular-deque/) | Medium | Amazon, Google, Meta | Double-ended ring buffer |
| [LC 346 Moving Average from Data Stream](https://leetcode.com/problems/moving-average-from-data-stream/) | Easy | Amazon, Meta, Google, Microsoft | Circular buffer average |

## NeetCode Reference
Not in NeetCode 150. Circular buffers appear in system design for streaming, logging, and low-latency systems.

## Company-Specific Questions

### Google
- Implement a circular buffer with enqueue, dequeue, isFull, isEmpty — handle wrap-around correctly
- Design a producer-consumer system using a ring buffer with blocking behavior (wait when full/empty)
- How would you make a circular buffer thread-safe without locks (lock-free ring buffer using CAS)?
- Design a logging system that uses a circular buffer and flushes periodically to disk

### Microsoft
- Design a real-time audio processing pipeline using a ring buffer between capture and playback
- How does Windows kernel use ring buffers for I/O completion ports?
- Compare ArrayDeque vs hand-rolled circular buffer — which is more efficient and why?

### Meta
- Implement a moving average calculator using a circular buffer (LC 346)
- Design a real-time metrics collection system using a ring buffer (collect N metrics, flush every N)
- How would you implement a sliding window rate limiter using a circular buffer of timestamps?

### Amazon
- Design a producer-consumer buffer for a streaming data pipeline (Kinesis-like)
- How would you implement backpressure in a ring buffer (block vs overwrite vs drop)?
- Design a circular buffer for database transaction logs (WAL, write-ahead log)

### Apple
- How does Core Audio use circular buffers between audio units?
- Design a ring buffer for video frame capture with vsync timing
- How would you implement a lock-free ring buffer for high-frequency sensor data?

### Oracle
- What is the difference between overwrite mode and blocking mode for a circular buffer?
- How would you implement a circular buffer that supports bulk reads (drain N elements at once)?
- Design a circular buffer for batch processing — elements accumulate and are processed in batches

## Real Production Scenarios

- **Scenario 1: Real-Time Audio Processing** — An audio application captures microphone input and streams it to speakers with a ring buffer. The producer (microphone thread) writes samples to the buffer; the consumer (playback thread) reads samples. The buffer smooths out jitter between the two rates. When the buffer is nearly empty, the consumer inserts silence (underrun protection). When nearly full, samples are dropped.

- **Scenario 2: Network Packet Capture** — A network monitoring tool captures packets into a ring buffer. The buffer has a fixed capacity (e.g., last 10K packets). When full, new packets overwrite the oldest. Users can pause to save the current buffer contents. The overwrite policy ensures the tool can run indefinitely without memory growth.

- **Scenario 3: Log Buffering** — A high-throughput logging library uses a ring buffer in each application thread. Log events are written to the thread-local ring buffer without synchronization. A dedicated "flusher" thread periodically drains all ring buffers and writes them to disk. This avoids per-log-entry locking.

## Interview Tips

- Time: O(1) for enqueue/dequeue/peek in proper implementation
- Space: O(capacity) — fixed-size array pre-allocated at construction
- Common edge cases: empty buffer (dequeue/peek fails), full buffer (enqueue blocks or overwrites), wrap-around (head > tail after wrap)
- Head pointer: next position to read; Tail pointer: next position to write
- Use (head % capacity) or (tail % capacity) to wrap — but modulo is expensive; bitwise AND if capacity is power of 2
- Distinguish "buffer full" vs "buffer empty" — classic trick: leave one slot empty, or store a count/size field
- Thread-safe ring buffer: use atomic counters, CAS for head/tail, memory barriers for visibility

## Java-Specific Considerations

- `ArrayDeque<E>` — resizable array-based deque, uses power-of-2 capacity, but grows dynamically (not fixed-size ring buffer)
- `LinkedBlockingQueue<E>` — optionally bounded, but node-based (not array ring buffer)
- `ArrayBlockingQueue<E>` — bounded blocking queue backed by fixed array — closest Java standard to a ring buffer with blocking
- `Disruptor` (LMAX) — third-party library: ultra-high-performance ring buffer for multi-threaded event processing
- Custom ring buffer: `class RingBuffer { final Object[] buffer; int head, tail, size; final int capacity; }`
- For threading: `AtomicInteger head, tail;` with CAS for lock-free operation
- Capacity as power of 2 enables fast wrap: `int index = head & (capacity - 1);`
- `java.util.logging.FileHandler` internally uses a ring buffer of recent log messages
- Performance hint: use `Unsafe` or `sun.misc.Contended` to avoid false sharing between head and tail counters
- Java 8+: `VarHandle` provides atomic operations on array elements with memory order semantics
