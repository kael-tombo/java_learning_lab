# PRODUCTION SCENARIOS: Microservices at Scale
## Lab 06 | Production Engineering Academy

---

## Scenario 1: The JVM DNS Caching Incident (Stale IP Black Hole)

### Context
A core payment service running on AWS EKS was making REST calls to an internal microservice running behind an AWS Network Load Balancer (NLB) or Kubernetes ClusterIP. The target microservice underwent an automated rolling deployment.

### The Disaster
- Half the pods in the target service were terminated and replaced with new IP addresses.
- However, 50% of requests from the caller service began failing immediately with `ConnectException: Connection refused` or timing out.
- The failure persisted for hours despite the target deployment having finished successfully and all new pods being 100% healthy.

### Root Cause: Java's Default `networkaddress.cache.ttl`
Historically, if a security manager is enabled or by default in some JDK distributions, the JVM caches DNS lookup results **forever** (`networkaddress.cache.ttl = -1`).
- The caller resolved the service DNS name once upon startup to IP `10.0.12.45`.
- When Kubernetes destroyed `10.0.12.45` and spawned `10.0.14.88`, the caller JVM never re-resolved DNS! It continued sending TCP SYN packets to the dead IP address.

### The Fix
In JVM startup options or `java.security`:
```properties
# Cache successful lookups for max 10 seconds in dynamic container environments
networkaddress.cache.ttl=10
# Cache negative (failed) lookups for max 5 seconds
networkaddress.cache.negative.ttl=5
```
Or pass dynamically on JVM launch:
`-Dsun.net.inetaddr.ttl=10`

---

## Scenario 2: The Single gRPC Channel Overload Trap

### Context
Engineering migrated an internal service from REST to gRPC for performance. They correctly created a singleton `ManagedChannel` to take advantage of HTTP/2 multiplexing.

### The Failure Mode
- Under 80,000 queries per second, the service hit a latency wall: p99 jumped to 400ms while CPU was only at 35%.
- Why? HTTP/2 multiplexes streams over a **single TCP connection**.
- A single TCP socket is constrained by the Linux kernel TCP window size, single-core socket receive/transmit queue processing, and HTTP/2 stream identifier limits (max $2^{31}-1$ streams).
- In addition, an intermediate L4 AWS NLB pinned that single TCP connection to one single backend server pod, overwhelming that single pod while 19 other pods sat completely idle!

### The Architectural Fix
1. Implement a **gRPC Channel Pool** (e.g. 4–8 subchannels per target host) to utilize multiple TCP sockets and spread across multiple CPU cores.
2. Enable client-side round-robin load balancing (`ManagedChannelBuilder.forTarget("dns:///service-name:50051").defaultLoadBalancingPolicy("round_robin")`) so the client connects to all pod IPs discovered via DNS, rather than pinning to a single L4 IP.
