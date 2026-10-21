# gRPC Networking -- Mathematical Foundation

## 1. HTTP/2 Frame Mathematics
Frame header: 9 bytes
Payload: up to 16384 bytes (default), configurable to 16777215 bytes
Maximum frame size: 16MB

### Stream Multiplexing
N concurrent streams per connection
Default max concurrent streams: 100
Default initial window: 65535 bytes

## 2. Flow Control Mathematics
window_update = (buffer_capacity - current_buffer_usage) * threshold
Connection-level and stream-level windows
Window size >= BDP for optimal throughput

## 3. Deadline Propagation
client_deadline = request_deadline - transmission_time
server_deadline = client_remaining - processing_time
Buffer time: 20-30% of total deadline

## 4. Keepalive Timing
interval = minimum_expected_idle_time / 2
Typical: 10-30 seconds
Keepalive timeout = RTT * safety_factor (1-5 seconds)

## 5. Load Balancing
- Round Robin: even distribution, good for homogeneous backends
- Weighted Round Robin: capacity_ratio = weight_i / sum(weights)
- Least Load: best for variable-length requests
- Pick First: simple, no distribution, first address until failure
