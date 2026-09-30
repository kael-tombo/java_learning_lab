# EXERCISES: Microservices Scaling & Load Balancing
## Lab 06 | Production Engineering Academy

---

## Exercise 1: Build and Benchmark a High-Throughput gRPC Channel Pool

### Objective
Create a multi-channel gRPC client that spreads 50,000 RPC requests per second across multiple TCP sockets and backend server pods.

### Tasks
1. Implement a gRPC echo service with a mock server that simulates 5ms processing time.
2. Build a single-channel gRPC client: benchmark throughput under 100 concurrent virtual threads.
3. Build `GrpcChannelPool` with 8 channels: benchmark throughput under identical load.
4. Compare throughput (req/s), CPU utilization, and TCP socket metrics.

---

## Exercise 2: Implement the Peak EWMA Load Balancer

### Tasks
1. Create a simulated backend pool with 5 endpoints:
   - 3 fast endpoints (latency 5ms)
   - 1 fluctuating endpoint (latency randomly varying between 10ms and 150ms)
   - 1 degrading endpoint (latency steadily climbing from 10ms to 2000ms)
2. Implement the Peak EWMA / Power of Two Choices algorithm from `CODE_DEEP_DIVE.md`.
3. Route 10,000 requests through the balancer.
4. Verify that traffic automatically shifts away from the degrading endpoint without hard failures.
