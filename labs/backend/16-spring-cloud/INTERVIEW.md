# Interview: Spring Cloud

## Common Interview Questions

### Q1: Explain how Eureka service discovery works.
**Answer**: Eureka has a server (registry) and clients (services). Clients register on startup with their IP and port. They send heartbeats every 30 seconds to renew leases. If a heartbeat is missed for 90 seconds, the instance is evicted. Other services query Eureka to discover instances by application name. Eureka uses self-preservation mode to protect against network partitions.

### Q2: What is the difference between Eureka and Kubernetes DNS-based discovery?
**Answer**: Eureka provides application-level registration with health checks, metadata, and self-preservation. K8s DNS resolves service names to IPs via CoreDNS but doesn't provide the same level of health awareness or metadata. Eureka also works outside Kubernetes.

### Q3: How does Resilience4J circuit breaker work?
**Answer**: It wraps method calls and tracks successes/failures in a sliding window (default 100 calls). When failure rate exceeds threshold (default 50%), circuit opens. In OPEN state, calls fail immediately. After a wait time (default 60s), it transitions to HALF_OPEN and allows limited test calls. If successful, circuit closes.

### Q4: Explain the differences between thread pool and semaphore bulkheads.
**Answer**: Thread pool bulkhead allocates a separate thread pool for each dependency, providing complete isolation but higher overhead. Semaphore bulkhead limits concurrent calls without creating new threads, lighter but caller thread blocks. Thread pool is preferred for blocking I/O, semaphore for non-blocking.

### Q5: How do you secure a Spring Cloud Gateway?
**Answer**: Implement OAuth2 resource server with JWT validation, add rate limiting with Redis-based RequestRateLimiter, configure CORS policies, and use custom filters for API key validation. Also secure actuator endpoints.

### Q6: What is Spring Cloud Config and how does it work?
**Answer**: Config Server provides externalized configuration via Git, Vault, or JDBC. Services bootstrap by connecting to Config Server, which resolves environment/property files, decrypts encrypted values, and returns PropertySources. Changes propagate via /actuator/refresh or Spring Cloud Bus.

### Q7: How does distributed tracing work across microservices?
**Answer**: A Trace ID is created at the entry point and propagated via HTTP headers. Each service creates spans tagged with the Trace ID. Micrometer/Brave instruments HTTP calls, database queries, and messaging. Spans are sent to Zipkin/Jaeger which assembles traces for visualization.

### Q8: What strategies exist for service-to-service authentication?
**Answer**: OAuth2 client credentials flow, mutual TLS, API keys in headers, JWT tokens propagated from gateway, and service mesh sidecar authentication.
