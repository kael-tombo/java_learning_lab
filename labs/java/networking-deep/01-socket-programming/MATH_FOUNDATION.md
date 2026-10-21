# Socket Programming -- Mathematical Foundation

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
M/M/1 queue model: average queue length = utilization / (1 - utilization)

## 2. TCP Throughput Mathematics

### TCP Window Size
Max throughput = TCP_Window_Size / RTT
- Default window: 64KB, RTT=100ms: max = 655KB/s
- Window scaling extends to ~1GB

### Bandwidth-Delay Product
BDP = bandwidth * RTT
- 1Gbps link, 100ms RTT: BDP = 12.5MB

## 3. Connection Pool Sizing
Optimal pool size = expected_concurrent_requests * (1 + safety_margin)

## 4. Scalability Metrics (C10K)
- Thread-per-connection: 10K threads = 80GB minimum
- Event loop: handles 10K in ~100MB
