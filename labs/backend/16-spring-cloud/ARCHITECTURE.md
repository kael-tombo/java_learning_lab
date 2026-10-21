# Architecture: Spring Cloud Microservices Infrastructure

## System Architecture Overview

`
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚   External       â”‚
                         â”‚   Clients        â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                  â”‚
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚   API Gateway    â”‚
                         â”‚ (Spring Cloud    â”‚
                         â”‚   Gateway)       â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                  â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚             â”‚             â”‚
            â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”
            â”‚ Product      â”‚ â”‚ Order     â”‚ â”‚ User      â”‚
            â”‚ Service      â”‚ â”‚ Service   â”‚ â”‚ Service   â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                    â”‚             â”‚             â”‚
            â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”
            â”‚         Service Registry (Eureka)       â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚      Config Server (Git-backed)         â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚      Git Repository (Configuration)     â”‚
            â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

## Component Architecture

### Eureka Server (Port 8761)
- **Type**: Service Registry
- **Persistence**: In-memory registry with peer replication
- **Protocol**: REST API
- **High Availability**: Multi-node peer awareness

### Config Server (Port 8888)
- **Type**: Configuration Management
- **Backend**: Git, Vault, JDBC, or native filesystem
- **Encryption**: Symmetric/asymmetric key encryption
- **Refresh**: Actuator endpoint, Spring Cloud Bus

### API Gateway (Port 8080)
- **Type**: Reverse Proxy + Router
- **Engine**: Spring WebFlux (Netty)
- **Filters**: Authentication, Rate Limiting, Logging
- **Service Discovery**: Integrated with Eureka

### Microservices
- **Type**: Spring Boot applications
- **Communication**: HTTP/REST with LoadBalancer
- **Resilience**: Circuit breaker, Retry, Bulkhead
- **Observability**: Micrometer tracing, Actuator

## Data Flow

### Request Lifecycle
1. External client sends request to Gateway
2. Gateway authenticates, rate limits, and logs
3. Gateway discovers target service via Eureka
4. Gateway routes request to appropriate service
5. Service may call other services (discovered via Eureka)
6. Each call uses LoadBalancer to select instance
7. Circuit breakers protect against failures
8. Responses flow back through Gateway to client

### Configuration Flow
1. Service starts, contacts Config Server
2. Config Server reads from Git repository
3. Encrypted values decrypted by server
4. Configuration returned to service
5. Service registers with Eureka
6. Configuration changes via Bus refresh

## Deployment Architecture

### Development
`
Single machine, all services via:
- Docker Compose
- or spring-boot:run with different ports
`

### Production
`
Kubernetes deployment with:
- Eureka optionally replaced by K8s DNS
- Config Server as Deployment
- Each service as separate Deployment
- Ingress instead of Gateway if using K8s
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\16-spring-cloud "REFACTORING.md") @"
# Refactoring: Spring Cloud

## 1. Monolith to Microservices Migration Strategy

### Step 1: Extract Configuration
Before:
`yaml
# monolithic application.yml
server.port: 8080
spring.datasource.url: jdbc:postgresql://localhost:5432/mydb
`

After:
`yaml
# config-repo/application.yml
shared:
  database:
    url: jdbc:postgresql://:5432/
`

### Step 2: Add Service Discovery
Before:
`java
// Hardcoded URL
restTemplate.getForObject("http://localhost:8081/api/products", ...);
`

After:
`java
@LoadBalanced
@Bean
public RestTemplate restTemplate() { return new RestTemplate(); }

// Discovered via service name
restTemplate.getForObject("http://product-service/api/products", ...);
`

### Step 3: Add Circuit Breakers
Before:
`java
public Order createOrder(OrderRequest request) {
    Product product = productClient.getProduct(request.productId());
    // If product service is down, this throws exception
}
`

After:
`java
@CircuitBreaker(name = "productService", fallbackMethod = "fallbackProduct")
public Product getProduct(String id) {
    return productClient.getProduct(id);
}

private Product fallbackProduct(String id, Throwable t) {
    log.warn("Product service unavailable, using cached product", t);
    return cache.get(id);
}
`

### Step 4: API Gateway Introduction
Before: Client calls services directly
`
client -> product-service:8081
client -> order-service:8082
`

After: All traffic through gateway
`
client -> gateway:8080/api/products/**
client -> gateway:8080/api/orders/**
`

## 2. Removing Legacy Patterns

### Replace Hystrix with Resilience4J
Hystrix is in maintenance mode, replace with Resilience4J:

Before:
`java
@HystrixCommand(fallbackMethod = "fallback")
public String callExternal() { ... }
`

After:
`java
@CircuitBreaker(name = "external", fallbackMethod = "fallback")
public String callExternal() { ... }
`

### Replace Zuul with Spring Cloud Gateway
Zuul 1.x is blocking and deprecated:

Before:
`java
@EnableZuulProxy
public class GatewayApplication { ... }
`

After:
`java
@Bean
public RouteLocator customRoutes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("product-service", r -> r.path("/api/products/**")
            .uri("lb://product-service"))
        .build();
}
`

### Replace Ribbon with Spring Cloud LoadBalancer
Ribbon is in maintenance mode:

Before:
`xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-ribbon</artifactId>
</dependency>
`

After:
`xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-loadbalancer</artifactId>
</dependency>
`

## 3. Configuration Refactoring

### Externalizing Hardcoded URLs
Before:
`java
@Value("http://localhost:8081/api/products")
private String productServiceUrl;
`

After:
`yaml
# bootstrap.yml
spring:
  application:
    name: order-service
  cloud:
    config:
      uri: http://config-server:8888
`

`java
@Value("")
private String productServiceUrl;
`

## 4. Service Decomposition

### Database Separation
Before: Shared database
`java
@Entity
@Table(name = "orders")
public class Order { @ManyToOne private Product product; }
`

After: Separate databases, service calls
`java
// Order service only knows orderId, not Product entity
public class Order {
    private String id;
    private String productId;  // References product-service
}
`

## 5. Observability Migration

### Adding Distributed Tracing
Before:
`java
log.info("Processing order {}", orderId);
`

After:
`java
@Observed(name = "order.process",
    contextualName = "processing-order")
public Order processOrder(String orderId) {
    // Automatic span creation
}
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\16-spring-cloud "DEBUGGING.md") @"
# Debugging: Spring Cloud

## 1. Eureka Registration Issues

### Service Not Registering
**Symptoms**: Service starts but not visible in Eureka dashboard

**Checklist**:
1. Verify @EnableDiscoveryClient annotation
2. Check eureka.client.serviceUrl.defaultZone property
3. Ensure spring.application.name is set
4. Check network connectivity to Eureka server port 8761
5. Verify Eureka server is running

**Debug commands**:
`ash
# Check Eureka health
curl http://localhost:8761/actuator/health

# Check registered instances
curl http://localhost:8761/eureka/apps

# Check service registration
curl http://localhost:8080/actuator/health
`

### Heartbeat Failures
**Symptoms**: Service registered but intermittently disappears

**Causes**:
1. Network latency causing heartbeat timeout
2. High load preventing heartbeat thread from running
3. Self-preservation mode threshold crossed

**Solution**:
`yaml
eureka:
  instance:
    lease-renewal-interval-in-seconds: 10  # Default 30, reduce if needed
    lease-expiration-duration-in-seconds: 30  # Default 90
`

## 2. Config Server Issues

### Cannot Load Configuration
**Symptoms**: Service fails to start, cannot connect to config server

**Checklist**:
1. Verify bootstrap.yml has correct spring.cloud.config.uri
2. Check config server is running on expected port
3. Verify Git repository URL and credentials
4. Check label/branch exists in repository

**Debug**:
`ash
# Test config server directly
curl http://localhost:8888/myapp/default

# Check config server logs for Git errors
# Test with native profile
curl http://localhost:8888/myapp/default --header "X-Config-Token: native"
`

### Encrypted Values Not Decrypting
**Symptoms**: Cipher text appears in resolved properties

**Causes**:
1. Encryption key not set in config server
2. {cipher} prefix missing
3. Wrong key used for encryption

**Fix**:
`ash
# Set encryption key
export ENCRYPT_KEY=mysecretkey

# Verify encryption
curl -X POST http://localhost:8888/encrypt -d 'test'
`

## 3. Circuit Breaker Issues

### Circuit Never Opens
**Symptoms**: No fallback method executed despite failures

**Check**:
1. Is the annotation on a method called from another bean?
2. Is the exception type in the configurations ecordExceptions list?
3. Is the sliding window large enough?

**Fix**:
`java
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
// Must be called from another bean, not internally
`

### Circuit Never Closes
**Symptoms**: Circuit stays open after service recovers

**Check**:
1. waitDurationInOpenState configuration
2. Half-open test calls still failing
3. Different exception types not recorded

## 4. Gateway Routing Issues

### 503 Service Unavailable
**Symptoms**: Gateway returns 503 for all routes

**Causes**:
1. Eureka not running or service not registered
2. Load balancer can't find instances
3. Circuit breaker open on gateway

**Debug**:
`ash
# Check registered routes
curl http://localhost:8080/actuator/gateway/routes

# Check global filters
curl http://localhost:8080/actuator/gateway/globalfilters
`

## 5. Distributed Tracing Issues

### Missing Spans
**Symptoms**: Traces incomplete or missing

**Causes**:
1. Trace context not propagated (missing headers)
2. Sampling rate too low
3. Missing instrumentation

**Fix**:
`yaml
management:
  tracing:
    sampling:
      probability: 1.0  # Temporarily set to 100%
`

### Tools for Debugging
`ash
# Zipkin UI - view traces
http://localhost:9411

# Eureka Dashboard
http://localhost:8761

# Config Server health
curl http://localhost:8888/actuator/health

# Gateway actuator
curl http://localhost:8080/actuator/gateway/routes
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\16-spring-cloud "COMMON_MISTAKES.md") @"
# Common Mistakes: Spring Cloud

## 1. Forgetting bootstrap.yml
**Mistake**: Using application.yml for config server connection
**Impact**: Service doesn't load remote configuration
**Fix**: Use bootstrap.yml or bootstrap.properties for config server bootstrap configuration

## 2. Missing @LoadBalanced
**Mistake**: Using plain RestTemplate with service names
**Impact**: UnknownHostException when using logical service names
**Fix**: Annotate the RestTemplate bean with @LoadBalanced

## 3. Self-Preservation Misconfiguration
**Mistake**: Disabling self-preservation in production
**Impact**: Instance flapping during network issues
**Fix**: 
`yaml
eureka:
  server:
    enable-self-preservation: true
    renewal-percent-threshold: 0.85
`

## 4. Circuit Breaker Non-Reentrancy
**Mistake**: Calling @CircuitBreaker method from same class
**Impact**: Aspect not triggered, no circuit breaker applied
**Fix**: Call circuit breaker methods from a different bean

## 5. Gateway Filter Order
**Mistake**: Incorrect filter ordering
**Impact**: Authentication bypassed or applied too late
**Fix**: 
`java
@Bean
public GlobalFilter customFilter() {
    return (exchange, chain) -> {
        // Filters execute in order of getOrder()
        return chain.filter(exchange);
    };
}
`

## 6. Config Server Git Timeout
**Mistake**: Not setting Git timeout for large repos
**Impact**: Service startup fails if Git operation times out
**Fix**:
`yaml
spring:
  cloud:
    config:
      server:
        git:
          timeout: 30
          clone-on-start: true
`

## 7. Exposing Actuator Endpoints
**Mistake**: Not securing /actuator endpoints
**Impact**: Anyone can view/toggle circuit breakers, routes, etc.
**Fix**:
`yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info
`

## 8. Hardcoding Service URLs
**Mistake**: Using IP addresses or hostnames
**Impact**: Not leveraging service discovery; brittle
**Fix**: Use logical service names from Eureka

## 9. Missing Fallback for All Circuit Breakers
**Mistake**: Only providing fallback for specific exception types
**Impact**: Unexpected exceptions still propagate
**Fix**:
`java
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
public String call() { ... }

// Catch-all fallback
public String fallback(Throwable t) { return "default"; }
`

## 10. Ignoring Bulkhead Configuration
**Mistake**: Using default thread pool size for all services
**Impact**: Thread starvation for slow services affecting fast ones
**Fix**: Configure per-service bulkhead:
`yaml
resilience4j:
  bulkhead:
    configs:
      default:
        max-concurrent-calls: 25
`

## 11. Not Handling Gateway Timeouts
**Mistake**: Default gateway timeout too short
**Impact**: Slow services get cut off
**Fix**:
`yaml
spring:
  cloud:
    gateway:
      httpclient:
        response-timeout: 30s
`

## 12. Sharing Configuration Repositories
**Mistake**: Multiple unrelated services sharing one config repo
**Impact**: Configuration changes affect unintended services
**Fix**: Separate repos per domain or bounded context
