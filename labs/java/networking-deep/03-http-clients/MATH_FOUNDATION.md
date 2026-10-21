# HTTP Clients (Java 11+) -- Mathematical Foundation

## 1. HTTP Protocol Mathematics

### Request/Response Size
Minimum request: ~100 bytes (GET without body)
Typical request with headers: ~500 bytes

### HTTP/2 Multiplexing
Multiple streams share a single TCP connection
Reduces connection overhead (no repeated TLS handshakes)
Eliminates head-of-line blocking at HTTP level

### WebSocket Frame Overhead
Base frame: 2 bytes (small payload)
Extended frame: 2 + 4/10 bytes (large payload)
Masking key: 4 bytes (client-to-server)
Total overhead: 2-14 bytes per message

### Connection Pooling
Pool size = max_concurrent_requests * (1 + buffer)
Typical pool: 5-20 connections per route

## 2. Timeout Mathematics

### Connection Timeout
- LAN: 1-2 seconds
- Internet: 5-10 seconds
- Safety factor: 2-3x

### Read Timeout
- Fast API (<100ms): 1-2 seconds
- Slow API (<1s): 5-10 seconds

### Retry Mathematics
Expected attempts = 1 / (1 - failure_rate)
- 10% failure: 1.11 expected attempts
- 50% failure: 2 expected attempts

## 3. Bandwidth Calculation
throughput = min(client, server, network bandwidth) / concurrent_connections
HTTP/2 multiplexing improves utilization over HTTP/1.1
