# NIO Selectors -- Debugging

## Debugging Strategies

### 1. Network Debugging Tools
- Wireshark: packet-level analysis of network traffic
- tcpdump: command-line packet capture
- netstat/ss: connection state monitoring
- lsof: open file descriptors (including sockets)
- curl: HTTP request testing and debugging

### 2. Java Network Debugging

#### JVM Flags
- -Djava.net.debug=all: detailed network debugging output
- -Djavax.net.debug=ssl: TLS/SSL debugging
- -Dsun.net.client.defaultConnectTimeout=5000: connection timeout
- -Dsun.net.client.defaultReadTimeout=5000: read timeout

#### Code-Level Debugging
- Set breakpoints in socket read/write methods
- Log connection lifecycle events
- Monitor thread states during network operations
- Use CompletableFuture for async debugging

### 3. Common Network Issues

#### Connection Refused
Causes: Server not running, wrong port, firewall blocking
Solution: Verify server status, check port and firewall

#### Connection Timeout
Causes: Network unreachable, server overloaded, firewall dropping
Solution: Check network connectivity, increase timeout, check server load

#### Connection Reset
Causes: Server crashed, connection closed abruptly, protocol mismatch
Solution: Check server logs, verify protocol compatibility, add retry logic

### 4. Performance Debugging
- Thread dump analysis for blocked threads
- Heap dump analysis for buffer/memory issues
- JFR events for network operations
- Profiling with async-profiler

### 5. Debugging Checklist
- [ ] Wireshark/tcpdump captures show expected traffic
- [ ] Java network debugging enabled for initial investigation
- [ ] Connection lifecycle logging implemented
- [ ] Timeouts configured appropriately
- [ ] Thread dumps collected during issues
- [ ] Resource limits (file descriptors) checked
- [ ] Firewall and security group rules verified
