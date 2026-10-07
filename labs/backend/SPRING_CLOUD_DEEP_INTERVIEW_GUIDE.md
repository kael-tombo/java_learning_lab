# Spring Cloud Ecosystem — Deep Interview Guide

## Table of Contents
1. [Service Discovery](#service-discovery)
2. [Load Balancing](#load-balancing)
3. [Configuration Management](#configuration-management)
4. [API Gateway](#api-gateway)
5. [Resilience Patterns](#resilience-patterns)
6. [Distributed Tracing](#distributed-tracing)
7. [Java Code Examples](#java-code-examples)
8. [20+ Interview Questions](#20-interview-questions)

---

## Service Discovery

Service discovery allows microservices to locate each other dynamically without hardcoding hostnames and ports.

### Client-Side Discovery

The client queries the registry to get available instances and uses a load-balancing strategy to pick one.

```
Service A ──→ Service Registry ──→ Service B Instance 1
    │                                    │
    └──── Load Balancer (Ribbon/LB) ──────┘
```

### Server-Side Discovery

A load balancer (AWS ALB, Kubernetes) queries the registry and forwards requests.

### Eureka — Netflix OSS

Eureka is a REST-based service registry. Services register themselves and send heartbeats.

| Concept | Description |
|---------|-------------|
| **Eureka Server** | Central registry — maintains instance metadata |
| **Eureka Client** | Registers itself, renews lease, fetches registry |
| **Lease** | Contract between instance and server (renewal every 30s) |
| **Self-Preservation** | Stops evicting instances if >85% heartbeats fail (for network partitions) |
| **Peer Awareness** | Multiple servers replicate state |

```java
@SpringBootApplication
@EnableEurekaServer
public class ServiceRegistryApplication {
    public static void main(String[] args) {
        SpringApplication.run(ServiceRegistryApplication.class, args);
    }
}
```

Client configuration:

```yaml
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    lease-renewal-interval-in-seconds: 30
    lease-expiration-duration-in-seconds: 90
    prefer-ip-address: true
```

### Consul

HashiCorp Consul provides service discovery, health checking, and K/V store. It uses the gossip protocol for membership.

### Kubernetes-native Discovery

With k8s, services use DNS (`my-service.namespace.svc.cluster.local`) and kube-proxy for load balancing. Spring Cloud Kubernetes can integrate with the k8s API.

**Tradeoffs:**

| Registry | Pros | Cons |
|----------|------|------|
| Eureka | Mature, Spring-native | No multi-DC, eventual consistency |
| Consul | Health checks, K/V, multi-DC | External dependency |
| K8s DNS | No extra infra | K8s-only, no client-side LB |
| ZooKeeper | Strong consistency | Heavy, not designed for discovery |

---

## Load Balancing

### Ribbon (Deprecated)

Netflix Ribbon provided client-side load balancing with rules:
- RoundRobinRule, WeightedResponseTimeRule, AvailabilityFilteringRule
- RetryRule — retries failed servers
- ZoneAvoidanceRule — avoids faulty zones

### Spring Cloud LoadBalancer (Replacement)

Reactive and declarative, integrates with Blockhound, uses `ServiceInstanceListSupplier`.

```java
@Bean
public ServiceInstanceListSupplier instanceListSupplier(ConfigurableApplicationContext ctx) {
    return ServiceInstanceListSupplier.builder()
        .withDiscoveryClient()
        .withCaching()
        .withRetry()
        .build(ctx);
}

// Custom load-balancing strategy
@Bean
public ReactorLoadBalancer<ServiceInstance> loadBalancer(
        Environment env, LoadBalancerClientFactory factory) {
    String name = env.getProperty("loadbalancer.client.name");
    return new RandomLoadBalancer(
        factory.getLazyProvider(name, ServiceInstanceListSupplier.class), name);
}
```

**Key Features:**
- Retry, caching, health-check integration
- Reactive (`Mono<Response<T>>`) and imperative support
- Works with Eureka, Consul, K8s

---

## Configuration Management

### Spring Cloud Config Server

Centralized configuration with environment-specific overrides.

```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
```

```yaml
# application.yml (Config Server)
spring:
  cloud:
    config:
      server:
        git:
          uri: (link removed)
          search-paths: '{application}'
          default-label: main
```

**Configuration resolution order:**
1. Application properties (local)
2. Profile-specific (`application-{profile}.yml`)
3. Config Server
4. Environment variables
5. `@RefreshScope` beans

### Refresh Scope

```java
@RefreshScope
@ConfigurationProperties(prefix = "app")
public class AppConfig {
    private String featureFlag;
    private int maxConnections;
    // getters/setters
}
```

Trigger refresh: `POST /actuator/refresh`

### Spring Cloud Bus

Propagates config changes across all instances:

```bash
POST /actuator/busrefresh
POST /actuator/busenv?name=featureFlag&value=true
```

```
Config Server
    │
    ├── Bus (RabbitMQ/Kafka)
    │
Service-A:1 ── Service-A:2 ── Service-B:1
```

```yaml
spring:
  cloud:
    bus:
      enabled: true
  rabbitmq:
    host: localhost
```

### Vault Integration

Spring Cloud Config can fetch secrets from HashiCorp Vault:

```yaml
spring:
  cloud:
    config:
      server:
        vault:
          host: localhost
          port: 8200
          backend: secret
          default-key: application
```

---

## API Gateway

### Spring Cloud Gateway

A reactive API Gateway built on Spring WebFlux, Project Reactor, and Netty.

```java
@Bean
public RouteLocator customRoutes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("order-service", r -> r
            .path("/api/orders/**")
            .filters(f -> f
                .circuitBreaker(c -> c
                    .setName("orderCB")
                    .setFallbackUri("forward:/fallback/orders"))
                .retry(3)
                .requestRateLimiter(c -> c
                    .setRateLimiter(redisRateLimiter())))
            .uri("lb://order-service"))
        .route("product-service", r -> r
            .path("/api/products/**")
            .filters(f -> f
                .addRequestHeader("X-Gateway", "true")
                .rewritePath("/api/products/(?<seg>.*)", "/${seg}"))
            .uri("lb://product-service"))
        .build();
}
```

### Route Predicates

| Predicate | Example | Description |
|-----------|---------|-------------|
| Path | `path=/api/**` | Match request path |
| Header | `header=X-Requested-By, \d+` | Match request header |
| Method | `method=GET,POST` | Match HTTP method |
| Query | `query=page, \\d+` | Match query parameter |
| Cookie | `cookie=session, [a-z]+` | Match cookie value |
| Host | `host=**.example.com` | Match Host header |
| Weight | `weight=group1, 80` | Traffic weighting |

### Filters (Pre/Post)

```java
@Component
public class CustomPreFilter implements GatewayFilterFactory<CustomPreFilter.Config> {
    // Custom filter implementation
}
```

---

## Resilience Patterns

### CircuitBreaker with Resilience4j

```java
@Bean
public Customizer<Resilience4JCircuitBreakerFactory> defaultCB() {
    return factory -> factory.configureDefault(id -> new Resilience4JConfigBuilder(id)
        .circuitBreakerConfig(CircuitBreakerConfig.custom()
            .slidingWindowSize(10)
            .failureRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(5))
            .permittedNumberOfCallsInHalfOpenState(3)
            .build())
        .timeLimiterConfig(TimeLimiterConfig.custom()
            .timeoutDuration(Duration.ofSeconds(2))
            .build())
        .build());
}
```

### Retry

```java
@Bean
public Retryer retryer() {
    return Retryer.builder()
        .maxAttempts(3)
        .waitDuration(Duration.ofMillis(500))
        .retryExceptions(TimeoutException.class)
        .build();
}
```

### RateLimiter

```java
@Bean
public RedisRateLimiter redisRateLimiter() {
    return new RedisRateLimiter(10, 20, 1); // replenishRate, burstCapacity, requestedTokens
}
```

---

## Distributed Tracing

### Spring Cloud Sleuth (Legacy — replaced by Micrometer Tracing)

Added trace IDs and span IDs to logs and propagated them via headers.

### Micrometer Tracing (Modern)

Part of the Micrometer ecosystem, integrates with OpenTelemetry.

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

```yaml
management:
  tracing:
    sampling:
      probability: 0.1  # 10% sampling
  zipkin:
    tracing:
      endpoint: http://localhost:9411/api/v2/spans
```

```java
@Bean
public ObservationHandler<Observation.Context> customHandler() {
    return new ObservationHandler<Observation.Context>() {
        @Override
        public void onStart(Observation.Context context) {
            context.put("startTime", System.currentTimeMillis());
        }
        @Override
        public boolean supportsContext(Observation.Context context) {
            return true;
        }
    };
}
```

### Trace Propagation Headers

```
X-B3-TraceId: 4bf92f3577b34da6a3ce929d0e0e4736
X-B3-SpanId: 00f067aa0ba902b7
X-B3-ParentSpanId: 0000000000000000
X-B3-Sampled: 1
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

---

## Java Code Examples

### 1. Service Discovery Client

```java
@RestController
@RequestMapping("/api/discovery")
public class DiscoveryClientController {

    private final DiscoveryClient discoveryClient;

    public DiscoveryClientController(DiscoveryClient discoveryClient) {
        this.discoveryClient = discoveryClient;
    }

    @GetMapping("/services")
    public List<String> getServices() {
        return discoveryClient.getServices();
    }

    @GetMapping("/instances/{serviceId}")
    public List<ServiceInstance> getInstances(@PathVariable String serviceId) {
        return discoveryClient.getInstances(serviceId);
    }
}
```

### 2. Gateway with Custom Route and Circuit Breaker

```java
@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator customRoutes(RouteLocatorBuilder builder,
                                      RedisRateLimiter rateLimiter) {
        return builder.routes()
            .route("user-service", r -> r
                .path("/api/users/**")
                .and().method("GET", "POST", "PUT", "DELETE")
                .filters(f -> f
                    .circuitBreaker(c -> c
                        .setName("userServiceCB")
                        .setStatusCodes("500", "502", "503")
                        .setFallbackUri("forward:/fallback/users"))
                    .retry(config -> config
                        .setRetries(3)
                        .setStatuses(HttpStatus.SERVICE_UNAVAILABLE))
                    .requestRateLimiter(c -> c.setRateLimiter(rateLimiter))
                    .addResponseHeader("X-Gateway-Response", "true"))
                .uri("lb://user-service"))
            .route("inventory-service", r -> r
                .header("X-Region", "us-east|us-west")
                .and().weight("inventory", 80)
                .filters(f -> f
                    .prefixPath("/api/v2")
                    .stripPrefix(1))
                .uri("lb://inventory-service"))
            .route("inventory-service-canary", r -> r
                .header("X-Canary", "true")
                .and().weight("inventory", 20)
                .uri("lb://inventory-service-canary"))
            .build();
    }
}
```

### 3. Config Client with Refresh

```java
@SpringBootApplication
@EnableConfigurationProperties
public class ConfigClientApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigClientApplication.class, args);
    }
}

@RefreshScope
@Component
@ConfigurationProperties(prefix = "app.config")
class DynamicConfig {
    private String featureToggle;
    private int connectionPoolSize = 10;
    private List<String> allowedOrigins = new ArrayList<>();

    public String getFeatureToggle() { return featureToggle; }
    public void setFeatureToggle(String featureToggle) { this.featureToggle = featureToggle; }
    public int getConnectionPoolSize() { return connectionPoolSize; }
    public void setConnectionPoolSize(int connectionPoolSize) { this.connectionPoolSize = connectionPoolSize; }
    public List<String> getAllowedOrigins() { return allowedOrigins; }
    public void setAllowedOrigins(List<String> allowedOrigins) { this.allowedOrigins = allowedOrigins; }
}

@RestController
@RequestMapping("/api/config")
class ConfigController {
    private final DynamicConfig config;

    ConfigController(DynamicConfig config) {
        this.config = config;
    }

    @GetMapping
    public DynamicConfig getConfig() { return config; }

    @GetMapping("/feature")
    public Map<String, String> checkFeature() {
        return Map.of("featureToggle", config.getFeatureToggle());
    }
}
```

### 4. Service Discovery with Load-Balanced RestClient

```java
@Configuration
public class LoadBalancedConfig {

    @Bean
    @LoadBalanced
    public RestClient.Builder restClientBuilder() {
        return RestClient.builder();
    }

    @Bean
    public RestClient restClient(RestClient.Builder builder) {
        return builder.build();
    }
}

@Service
public class OrderServiceClient {
    private final RestClient restClient;

    public OrderServiceClient(RestClient restClient) {
        this.restClient = restClient;
    }

    public Order getOrder(String orderId) {
        return restClient.get()
            .uri("http://order-service/api/orders/{id}", orderId)
            .retrieve()
            .body(Order.class);
    }
}
```

### 5. Resilience4j with Spring Boot

```java
@Service
public class PaymentService {
    private static final Logger log = LoggerFactory.getLogger(PaymentService.class);

    @CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
    @Retry(name = "paymentService")
    @RateLimiter(name = "paymentService")
    @TimeLimiter(name = "paymentService")
    public CompletableFuture<PaymentResponse> processPayment(PaymentRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            return paymentGateway.charge(request);
        });
    }

    public CompletableFuture<PaymentResponse> paymentFallback(
            PaymentRequest request, Throwable t) {
        log.warn("Payment fallback for {}: {}", request.orderId(), t.getMessage());
        return CompletableFuture.completedFuture(
            new PaymentResponse(request.orderId(), "FALLBACK", "TRY_LATER"));
    }
}
```

### 6. Custom Trace Propagation with Micrometer

```java
@Component
public class TracingFilter implements WebFilter {
    private final Tracer tracer;

    public TracingFilter(Tracer tracer) {
        this.tracer = tracer;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        Span span = tracer.nextSpan().name("http-filter")
            .tag("http.method", exchange.getRequest().getMethod().name())
            .tag("http.path", exchange.getRequest().getURI().getPath())
            .start();
        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            return chain.filter(exchange)
                .doFinally(signalType -> span.end());
        }
    }
}
```

---

## 20+ Interview Questions

### Basic

1. **How does Eureka client registration work?** — Client sends heartbeat every 30s; server evicts after 90s. Self-preservation mode prevents eviction during network partitions.

2. **What is the difference between client-side and server-side discovery?** — Client-side: client queries registry. Server-side: load balancer handles routing. Client-side gives more control but adds complexity.

3. **How does Spring Cloud Config prioritize properties?** — Local first → profile-specific → Config Server → env vars → `@RefreshScope` beans. See `EnvironmentDecryptorEnvironmentRepository`.

4. **Explain the Spring Cloud Bus architecture.** — Bus uses RabbitMQ/Kafka to broadcast config changes. `POST /actuator/busrefresh` sends refresh events to all bound services.

5. **How do you implement canary deployments with Spring Cloud Gateway?** — Use Weight route predicate. Route 80% to stable, 20% to canary based on header or weight.

### Intermediate

6. **How does `@RefreshScope` work internally?** — Creates a scoped proxy. When context refreshes, the proxy destroys and recreates the bean. All dependent beans get the new instance.

7. **What is the difference between Sleuth and Micrometer Tracing?** — Sleuth is deprecated. Micrometer Tracing is the successor, built on OpenTelemetry APIs, supports Brave and OTel exporters.

8. **How do you handle distributed configuration with encryption?** — Config Server supports {cipher} prefix with symmetric/asymmetric keys. `spring.cloud.config.server.encrypt.enabled=true`. Use `encrypt` and `decrypt` endpoints.

9. **Explain Eureka self-preservation mode.** — If >85% of heartbeats fail in 1 minute, Eureka stops evicting instances. This protects against network partitions but means dead instances may serve traffic.

10. **How does Spring Cloud LoadBalancer differ from Ribbon?** — Ribbon is imperative, deprecated. LoadBalancer is reactive, integrated with WebFlux, supports ServiceInstanceListSupplier for discovery.

### Advanced

11. **Design a multi-region service discovery strategy.** — Each region has its own Eureka cluster. Services register in their local region. Cross-region calls use DNS-based failover. Consul WAN gossip can link regions.

12. **How do you implement blue-green deployment with Spring Cloud Gateway?** — Use Header predicate to route `X-Env: blue` vs `X-Env: green`. Or use Weight predicate with gradual traffic shift.

13. **Explain the Config Server's environment repository chain.** — `EnvironmentRepository` collects from: `NativeEnvironmentRepository` (local), `GitEnvironmentRepository`, `VaultEnvironmentRepository`, `JdbcEnvironmentRepository`. Order is configurable.

14. **How do you propagate tracing context across async boundaries?** — Use `Tracer.nextSpan()` to create child spans, pass context via `ContextSnapshot` or `Hooks.enableAutomaticContextPropagation()` in Reactor.

15. **Design a rate-limiting strategy across multiple gateway instances.** — Use Redis-based rate limiter (`RedisRateLimiter`). Each gateway instance checks Redis for token bucket. Coordinated via Redis atomic operations.

16. **How does the Config Server handle large-scale concurrent refreshes?** — Bus batches refresh events. Config Server can cache Git repos with `basedir`. Use `spring.cloud.config.server.git.clone-on-start` to pre-warm.

17. **Explain the Gateway's filter ordering mechanism.** — Filters have `getOrder()`. Shortcut filters (via DSL) are ordered: retry → circuit breaker → rate limiter → path rewrite. Custom filters implement `Ordered` interface.

18. **How do you implement a custom health indicator for a circuit breaker?** — Extend `HealthIndicator`. Check `CircuitBreaker.getState()`. Return `up` if closed, `down` if open, `unknown` if half-open.

19. **Design a configuration strategy for 1000+ microservices.** — Hierarchical repos: `common-config` → `domain-config` → `app-config`. Use labels (`main`, `prod`, `us-east`). Vault for secrets. Bus for propagation.

20. **How does Spring Cloud Gateway handle WebSocket connections?** — Uses `WebSocketHandler` with `ws://` scheme in route URI. Forwarding headers: `Upgrade`, `Connection`, `Sec-WebSocket-Key`, `Sec-WebSocket-Version`.

21. **Explain Zipkin's data model and how Micrometer tracing maps to it.** — Zipkin has `Span` (traceId, parentId, id, name, timestamp, duration). Micrometer's `Span` maps directly. `HttpClientHandler` and `HttpServerHandler` create spans from observations.

22. **How do you test a circuit breaker in integration tests?** — Wiremock/stub server that returns 503 for N calls. Assert circuit opens after threshold. Verify fallback method. Test half-open recovery.

23. **What happens when the Config Server is down during startup?** — Client fails fast if `spring.cloud.config.fail-fast=true`. Otherwise, client starts with local config. Retry with `spring.cloud.config.retry.*`. Bus health check alerts.

24. **Compare Eureka, Consul, and ZooKeeper for service discovery.** — Eureka: AP (availability + partition tolerance), eventual consistency. Consul: CP + AP via gossip, health checks. ZooKeeper: CP, strong consistency but complex.

25. **How do you trace Kafka message flows across services?** — Use `TracingProducerInterceptor` / `TracingConsumerInterceptor`. Micrometer tracing bridges to Kafka client interceptor API. Headers carry trace context.