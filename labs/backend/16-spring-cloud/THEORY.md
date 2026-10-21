# Theory: Spring Cloud Microservice Infrastructure

## 1. Service Discovery (Eureka)

Service discovery is a key pattern in microservices where services register themselves with a registry and discover other services at runtime.

### Eureka Architecture
- **Eureka Server**: The registry that maintains service instances
- **Eureka Client**: Each microservice instance registers with the server
- **Heartbeat**: Clients send heartbeats every 30 seconds to renew leases
- **Self-Preservation**: Eureka protects against network partitions by not evicting instances

### Registration Flow
1. Service starts and registers with Eureka Server
2. Eureka Server assigns a lease with expiry time
3. Client sends heartbeats every 30 seconds
4. If heartbeats fail for 90 seconds, the instance is evicted
5. Other services query Eureka to discover available instances

## 2. Distributed Configuration (Spring Cloud Config)

Centralized configuration management across all microservices.

### Config Server Architecture
- Git-backed configuration repository
- Environment-specific property files (application-dev.yml, application-prod.yml)
- Dynamic refresh via /actuator/refresh
- Encryption/decryption of sensitive properties

### Configuration Resolution Order
1. Application-level properties
2. Profile-specific properties
3. Label/branch-based properties

## 3. Circuit Breaker (Resilience4J)

Prevents cascading failures by detecting when a remote service is failing.

### Circuit Breaker States
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Failures exceed threshold, requests fail immediately
- **HALF_OPEN**: After wait duration, test requests allowed

### Configuration Parameters
- **slidingWindowSize**: Number of calls in sliding window (default 100)
- **failureRateThreshold**: Percentage of failures to open circuit (default 50%)
- **waitDurationInOpenState**: Time before half-open (default 60s)
- **permittedNumberOfCallsInHalfOpenState**: Test calls (default 10)

## 4. Load Balancing (Spring Cloud LoadBalancer)

Client-side load balancing distributes requests across service instances.

### Load Balancing Strategies
- Round-robin (default)
- Random
- Weighted response time
- Custom via ServiceInstanceListSupplier

## 5. API Gateway (Spring Cloud Gateway)

Single entry point for all microservices providing cross-cutting concerns.

### Gateway Features
- Route configuration via RouteLocator DSL
- Filters: add headers, rate limiting, authentication
- Predicates: path, header, query, method matching
- Request/response transformation

## 6. Distributed Tracing (Micrometer Tracing)

End-to-end request tracing across microservice boundaries.

### Tracing Concepts
- **Trace ID**: Unique ID for an entire request flow
- **Span ID**: Unique ID for a single service call
- **Parent Span**: Links spans across services
- **Propagation**: Trace context forwarded via HTTP headers

## References
- Spring Cloud Documentation
- Netflix Eureka Wiki
- Resilience4J Documentation
- Spring Cloud Gateway Reference
