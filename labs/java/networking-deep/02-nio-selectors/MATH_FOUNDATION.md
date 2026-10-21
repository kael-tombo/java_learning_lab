# NIO Selectors -- Mathematical Foundation

## 1. Network Latency Mathematics

### Propagation Delay
d_prop = distance / propagation_speed
- Fiber optic: ~2/3 speed of light (2x10^8 m/s)
- Transatlantic (~5000km): ~25ms
- Cross-country (~4000km): ~20ms

### Transmission Delay
d_trans = packet_size / link_bandwidth
- 1500 byte packet on 1Gbps link: 12 microseconds
- 1MB message on 100Mbps link: 80ms

### Queuing Delay
Varies with network load. At capacity, queuing delay approaches infinity.
M/M/1 queue model: average queue length = utilization / (1 - utilization)

## 2. TCP Throughput Mathematics

### TCP Window Size
Maximum throughput = TCP_Window_Size / RTT
- Default window: 64KB
- With RTT=100ms: max throughput = 65536/0.1 = 655KB/s
- Window scaling extends this to ~1GB window

### Bandwidth-Delay Product
BDP = bandwidth * RTT
- 1Gbps link with 100ms RTT: BDP = 12.5MB
- Optimal window size should be >= BDP

## 3. Connection Pool Sizing

### Little's Law
L = lambda * W (average connections = arrival rate * average service time)
Optimal pool size = expected_concurrent_requests * (1 + safety_margin)
- Safety margin typically 10-20% for burst handling

### Pool Saturation
When pool is exhausted, requests queue. Queue growth follows:
queue_size = arrival_rate * wait_time
- Monitor queue depth to detect pool exhaustion
- Pool too large wastes memory; too small causes queuing

## 4. Scalability Metrics

### C10K Problem
Handling 10,000 concurrent connections:
- Thread-per-connection: 10,000 threads ~ 8MB each = 80GB minimum
- Event loop: select/poll/epoll handles 10,000 in ~100MB
- NIO/Netty solution handles C10K with efficient event loops

### Amdahl's Law
Speedup = 1 / ((1-P) + P/N)
P = parallelizable fraction, N = processors
- Network applications are often I/O bound (limited by network, not CPU)
- Event loops use 1-2 threads; thread pools for blocking operations

## 5. Selector Performance

### select() vs poll() vs epoll()
- select(): O(n) scanning, 1024 FD limit
- poll(): O(n) scanning, no FD limit
- epoll: O(1) event notification, millions of FDs
- Event count per select() call impacts throughput linearly

## 6. Mathematical Optimization

### Buffer Sizing
Optimal buffer size = BDP / number_of_concurrent_streams
- Too small: underutilized bandwidth
- Too large: wasted memory, increased latency

### Thread Pool Sizing
N_threads = N_cpu * (1 + W/C)
W = wait time (I/O), C = compute time
- For network I/O bound: N_threads = 2-4 * N_cpu
