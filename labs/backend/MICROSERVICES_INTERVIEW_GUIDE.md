# Microservices Architecture Interview Guide — Wave 6

> Target: 400+ lines covering design patterns, communication, deployment, company-specific architectures
> Format: Question → Answer → Code → Company Context

---

## 1. Design Patterns

### Q: Service decomposition strategies — domain-driven vs business capability

**Answer:**

| Strategy | Approach | Based On | Example |
|----------|----------|----------|---------|
| **Domain-driven (DDD)** | Bounded contexts, aggregates, ubiquitous language | Domain model | `OrderContext`, `BillingContext`, `ShippingContext` |
| **Business capability** | Align to business functions | Org structure | `UserService`, `ProductService`, `OrderService` |
| **Subdomain** | Core, supporting, generic subdomains | Business value | Core: `Payment`, Supporting: `Inventory`, Generic: `Notification` |
| **Verb-based (action)** | Group by use-cases | Action flows | `CheckoutService`, `SearchService`, `RecommendationService` |

**When to choose:**
- **DDD**: Complex domains with rich business rules (Finance, Healthcare)
- **Business capability**: Simple CRUD, clear org boundaries (E-commerce, CMS)
- **Subdomain**: Strategic investment decisions

```java
// DDD — bounded context with aggregate root
@Aggregate
public class Order {
    @AggregateIdentifier
    private OrderId orderId;
    private OrderStatus status;
    private List<OrderLineItem> items;
    private Money total;

    public Order(OrderId id, List<OrderLineItem> items) {
        this.orderId = id;
        this.items = items;
        this.status = OrderStatus.CREATED;
    }

    public void confirm() {
        if (status != OrderStatus.CREATED)
            throw new IllegalStateException("Cannot confirm order in " + status + " state");
        this.status = OrderStatus.CONFIRMED;
    }
}
```

**Company Frequency:** Amazon (always), Google (often), Netflix (often), Uber (always)

**Follow-ups:**
- How do you identify bounded contexts?
- What if services need to share data?

---

### Q: API Gateway pattern

**Answer:**
An API Gateway is a single entry point that handles:
- Request routing, aggregation, authentication, rate limiting, caching, protocol translation

**Spring Cloud Gateway example:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - name: CircuitBreaker
              args:
                name: orderCircuitBreaker
                fallbackUri: forward:/fallback/orders
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
            - StripPrefix=1
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=1
```

**Gateway patterns:**
| Pattern | Description | Tools |
|---------|-------------|-------|
| Reverse proxy | Route requests to services | Nginx, Kong, Envoy |
| Edge gateway | Auth, TLS, rate limiting | Spring Cloud Gateway, Zuul |
| Aggregation gateway | Composite responses | GraphQL, BFF |
| Service mesh sidecar | L7 routing, traffic mgmt | Istio, Linkerd |

**Company Frequency:** Netflix (Zuul author), Amazon (ALB + custom), Google (Istio), Uber (custom)

**Follow-ups:**
- Why did Netflix move from Zuul to Spring Cloud Gateway? (Zuul 1.x is blocking/servlet-based; Gateway is reactive)
- What is the Backend for Frontend (BFF) pattern?

---

### Q: Service discovery — Eureka, Consul, Kubernetes DNS

**Answer:**

| Solution | Type | How It Works | Spring Integration |
|----------|------|-------------|-------------------|
| **Eureka** | Client-side | Service registers itself; clients query registry | `spring-cloud-starter-netflix-eureka-client` |
| **Consul** | Client + Server-side | KV store + health checking | `spring-cloud-starter-consul-discovery` |
| **Kubernetes DNS** | DNS-based | `service-name.namespace.svc.cluster.local` | `spring-cloud-kubernetes` |

**Eureka setup:**
```java
// Server
@SpringBootApplication
@EnableEurekaServer
public class EurekaServer { }

// Client
@SpringBootApplication
@EnableDiscoveryClient // optional since boot 2.x (auto if eureka on classpath)
public class OrderService { }
```

```yaml
# application.yml — eureka client
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/
  instance:
    preferIpAddress: true
    lease-renewal-interval-in-seconds: 10
    lease-expiration-duration-in-seconds: 30
```

**Company Frequency:** Netflix (Eureka/RIB), Google (K8s DNS + Istio), Amazon (Route53 + ALB)

**Follow-ups:**
- Self-preservation mode in Eureka? (Network partition protection)
- What happens when Eureka server is down?

---

### Q: Circuit breaker — Resilience4j vs Hystrix

**Answer:**

| Feature | Hystrix (Deprecated) | Resilience4j |
|---------|---------------------|--------------|
| State | Maintenance mode (Netflix, 2018) | Actively maintained |
| Architecture | Thread pool isolation (heavy) | Semaphore/thread pool configurable |
| Reactive | Limited (RxJava) | Native Reactor/RxJava support |
| Configuration | Properties | Declarative or programmatic |
| Composite | Single circuit breaker | CircuitBreaker + Retry + RateLimiter + Bulkhead + TimeLimiter |

**Why Hystrix was deprecated:**
1. Complex thread pool model with high overhead
2. Netflix shifted focus to RxJava → Resilience4j aligned with Spring WebFlux
3. Resilience4j is modular, lightweight (single jar per module)
4. Better reactive stack support

**Resilience4j example:**
```java
@CircuitBreaker(name = "inventoryService", fallbackMethod = "inventoryFallback")
@Retry(name = "inventoryService", maxAttempts = 3, backoff = @Backoff(delay = 1000))
@TimeLimiter(name = "inventoryService")
@Bulkhead(name = "inventoryService", type = Bulkhead.Type.THREADPOOL)
public CompletableFuture<InventoryResponse> checkInventory(String sku) {
    return CompletableFuture.supplyAsync(() ->
        inventoryClient.check(sku));
}

private CompletableFuture<InventoryResponse> inventoryFallback(String sku, Throwable t) {
    return CompletableFuture.completedFuture(new InventoryResponse(sku, 0, false));
}
```

**Configuration:**
```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventoryService:
        sliding-window-size: 10
        minimum-number-of-calls: 5
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        permitted-number-of-calls-in-half-open-state: 3
  retry:
    instances:
      inventoryService:
        max-attempts: 3
        wait-duration: 1s
```

**Company Frequency:** Netflix (created Hystrix, now migrated), Amazon (uses own, but questions about Resilience4j), Google (often)

**Follow-ups:**
- Circuit breaker state machine (CLOSED → OPEN → HALF_OPEN → CLOSED)
- What is the difference between thread pool and semaphore isolation?

---

### Q: Externalized configuration — Spring Cloud Config vs ConfigMap

**Answer:**

**Spring Cloud Config:**
```yaml
# bootstrap.yml
spring:
  application:
    name: order-service
  cloud:
    config:
      uri: http://config-server:8888
      fail-fast: true
      retry:
        initial-interval: 1000
        max-attempts: 5
```

**Config Server (Git-backed):**
```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServer { }
```

```yaml
# application.yml
spring:
  cloud:
    config:
      server:
        git:
          uri: (link removed)
          search-paths: '{application}'
          default-label: main
```

**Kubernetes ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
data:
  application.yml: |
    server:
      port: 8080
    spring:
      datasource:
        url: jdbc:postgresql://postgres:5432/orders
---
# Pod mounts ConfigMap as volume or env
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: order-service
      envFrom:
        - configMapRef:
            name: order-service-config
```

**Comparison:**

| Feature | Spring Cloud Config | K8s ConfigMap + Secrets |
|---------|-------------------|----------------------|
| Encryption | Built-in (`{cipher}`) | External (SealedSecrets, SOPS) |
| Refresh | `/actuator/refresh` or bus | Pod restart or reloader |
| Versioning | Git-backed by default | Manual or GitOps |
| Complexity | Requires Config Server | Native K8s |

**Company Frequency:** Netflix (Spring Cloud Config), Google (K8s ConfigMap/Secret), Amazon (AWS AppConfig/SSM+Secrets Manager)

---

### Q: Distributed tracing — Sleuth → Micrometer Tracing

**Answer:**

```xml
<!-- Spring Boot 3.x: Micrometer Tracing -->
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
spring:
  application:
    name: order-service
management:
  tracing:
    sampling:
      probability: 0.1  # 10% sampling
    propagation:
      type: w3c  # W3C tracecontext (default)
```

```java
// Automatic: WebClient, RestTemplate, Kafka, gRPC — all instrumented

// Manual tracing
@Service
public class OrderService {
    private final Tracer tracer;

    @Autowired
    public OrderService(Tracer tracer) {
        this.tracer = tracer;
    }

    public Order createOrder(OrderRequest req) {
        Span span = tracer.nextSpan().name("order.create").start();
        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            span.tag("customerId", req.customerId());
            return processOrder(req);
        } finally {
            span.end();
        }
    }
}
```

**Trace propagation headers (W3C Trace Context):**
- `traceparent`: `00-<trace-id>-<span-id>-<trace-flags>`
- `tracestate`: vendor-specific metadata

**Migration from Sleuth (Spring Boot 2.x → 3.x):**
- `spring-cloud-sleuth` → `micrometer-tracing`
- Brave / OpenTelemetry as tracer implementations
- Zipkin / Jaeger as backends

**Company Frequency:** Netflix (often), Google (often — Dapper paper), Uber (Jaeger), Amazon (X-Ray)

---

### Q: API Composition vs CQRS

**Answer:**

| Pattern | Approach | When to Use |
|---------|----------|-------------|
| **API Composition** | Orchestrator calls multiple services and aggregates results | Simple joins, read-heavy, low latency requirements |
| **CQRS** | Separate read and write models, optimized query side | Complex queries, high write load, different read/write concerns |

**API Composition example:**
```java
@Service
public class OrderCompositeService {
    private final OrderServiceClient orders;
    private final PaymentServiceClient payments;
    private final ShippingServiceClient shipping;
    private final UserServiceClient users;

    // Aggregator
    public OrderDetails getOrderDetails(String orderId) {
        Order order = orders.getOrder(orderId);
        // Parallel calls
        CompletableFuture<Payment> payment =
            CompletableFuture.supplyAsync(() -> payments.getPayment(order.getPaymentId()));
        CompletableFuture<Shipping> ship =
            CompletableFuture.supplyAsync(() -> shipping.getShipment(order.getShipmentId()));
        CompletableFuture<User> user =
            CompletableFuture.supplyAsync(() -> users.getUser(order.getUserId()));

        CompletableFuture.allOf(payment, ship, user).join();
        return new OrderDetails(order, payment.get(), ship.get(), user.get());
    }
}
```

**CQRS with separate read model:**
```java
// Write model — Command handler
@CommandHandler
public Order handle(CreateOrderCommand cmd) {
    Order order = new Order(cmd.orderId(), cmd.items());
    eventBus.publish(new OrderCreatedEvent(cmd.orderId(), cmd.items()));
    return order;
}

// Read model — Projection
@Component
public class OrderProjection {
    @EventHandler
    public void on(OrderCreatedEvent event) {
        orderViewRepository.save(new OrderView(
            event.orderId(),
            event.items(),
            OrderStatus.CREATED
        ));
    }
}

// Read side — optimized query
@RestController
public class OrderQueryController {
    @GetMapping("/orders/{id}/summary")
    public OrderSummary getSummary(@PathVariable String id) {
        return orderViewRepository.findSummaryById(id);
    }
}
```

**Company Frequency:** Amazon (often — API Comp), Netflix (often — CQRS), Google (medium)

---

### Q: Saga pattern — choreography vs orchestration

**Answer:**

| Type | Coordination | Pros | Cons | Example |
|------|-------------|------|------|---------|
| **Choreography** | Events (each service listens/reacts) | Decentralized, no single point of failure | Complex to trace, cyclic events | Kafka + Avro |
| **Orchestration** | Central orchestrator (Saga Coordinator) | Clear flow, easy to monitor/test | Single point of failure, orchestrator complexity | Temporal, Camunda, Axon |

**Choreography Saga (Kafka):**
```java
// Order Service publishes event
@Service
public class OrderSaga {
    private final KafkaTemplate<String, Object> kafka;

    @Transactional
    public void createOrder(CreateOrderCommand cmd) {
        orderRepo.save(new Order(cmd.orderId(), cmd.customerId(), cmd.amount(), "PENDING"));
        kafka.send("order-events", new OrderCreatedEvent(cmd.orderId(), cmd.customerId(), cmd.amount()));
    }
}

// Payment Service listens and compensates
@Service
public class PaymentSaga {
    @KafkaListener(topics = "order-events")
    public void handleOrderCreated(OrderCreatedEvent event) {
        try {
            paymentService.process(event.orderId(), event.amount());
            kafka.send("payment-events", new PaymentApprovedEvent(event.orderId()));
        } catch (Exception e) {
            kafka.send("payment-events", new PaymentFailedEvent(event.orderId()));
        }
    }
}

// Inventory Service listens and compensates
@Service
public class InventorySaga {
    @KafkaListener(topics = "payment-events")
    public void handlePaymentApproved(PaymentApprovedEvent event) {
        try {
            inventoryService.reserve(event.orderId());
        } catch (Exception e) {
            kafka.send("inventory-events", new InventoryFailedEvent(event.orderId()));
        }
    }
}

// Compensation listener
@KafkaListener(topics = "payment-events")
public void handlePaymentFailed(PaymentFailedEvent event) {
    orderRepo.updateStatus(event.orderId(), "FAILED");
    kafka.send("order-events", new OrderCancelledEvent(event.orderId()));
}
```

**Orchestration Saga (Temporal):**
```java
// Saga orchestrator workflow
public class OrderWorkflowImpl implements OrderWorkflow {
    private final PaymentActivities payment = ActivityStubs.newActivityStubs(PaymentActivities.class);
    private final InventoryActivities inventory = ActivityStubs.newActivityStubs(InventoryActivities.class);
    private final NotificationActivities notification = ActivityStubs.newActivityStubs(NotificationActivities.class);

    @Override
    public OrderResult processOrder(Order order) {
        try {
            // Step 1: Reserve payment
            payment.authorize(order.getCustomerId(), order.getAmount());
            // Step 2: Reserve inventory
            inventory.reserve(order.getItems());
            // Step 3: Confirm
            payment.capture(order.getCustomerId(), order.getAmount());
            inventory.deduct(order.getItems());
            notification.send(order.getCustomerId(), "Order confirmed");
            return OrderResult.success(order.getId());
        } catch (PaymentException e) {
            // Compensation: nothing to do (payment not captured)
            throw new SagaException("Payment failed", e);
        } catch (InventoryException e) {
            // Compensation: release payment
            payment.refund(order.getCustomerId(), order.getAmount());
            throw new SagaException("Inventory failed", e);
        }
    }
}
```

**Company Frequency:** Amazon (high — they use orchestration internally), Netflix (high — choreography), Google (often)

**Follow-ups:**
- When to choose choreography vs orchestration?
- How to handle idempotency in sagas?

---

## 2. Communication Patterns

### Q: WebClient vs RestTemplate (deprecated)

**Answer:**

```java
// RestTemplate (deprecated since Boot 3.x, but still functional)
@Bean
public RestTemplate restTemplate(RestTemplateBuilder builder) {
    return builder
        .connectTimeout(Duration.ofSeconds(5))
        .readTimeout(Duration.ofSeconds(5))
        .build();
}

// WebClient (reactive, non-blocking)
@Bean
public WebClient webClient(WebClient.Builder builder) {
    return builder
        .baseUrl("http://inventory-service")
        .defaultHeader(HttpHeaders.CONTENT_TYPE, "application/json")
        .build();
}

// Using WebClient
@Service
public class OrderService {
    private final WebClient webClient;

    public Mono<InventoryResponse> checkInventory(String sku) {
        return webClient.get()
            .uri("/inventory/{sku}", sku)
            .retrieve()
            .onStatus(HttpStatus::is4xxClientError, resp ->
                Mono.error(new InventoryClientException(resp.statusCode())))
            .bodyToMono(InventoryResponse.class)
            .timeout(Duration.ofSeconds(3))
            .retryWhen(Retry.backoff(3, Duration.ofMillis(500)));
    }
}

// Blocking if needed
public InventoryResponse checkInventoryBlocking(String sku) {
    return webClient.get()
        .uri("/inventory/{sku}", sku)
        .retrieve()
        .bodyToMono(InventoryResponse.class)
        .block(Duration.ofSeconds(5));
}
```

**Why WebClient over RestTemplate:**
- Non-blocking by default
- Native reactive support
- Better error handling (`.onStatus`)
- Timeout/retry built-in
- Future-proof (RestTemplate deprecated in 3.x)

**Company Frequency:** Netflix (always WebClient), Google (often), Amazon (mixed)

---

### Q: Spring Cloud Stream — Kafka/RabbitMQ abstraction

**Answer:**

```java
// Function-based programming model (Spring Cloud Stream 3.x+)
@SpringBootApplication
public class OrderStreamApplication {

    // Consumer
    @Bean
    public Consumer<OrderCreatedEvent> handleOrderCreated() {
        return event -> {
            log.info("Order created: {}", event.orderId());
            orderService.process(event);
        };
    }

    // Supplier (source)
    @Bean
    public Supplier<OrderEvent> orderEvents() {
        return () -> {
            OrderEvent event = pollNextEvent();
            return event;
        };
    }

    // Processor (transform)
    @Bean
    public Function<OrderCreatedEvent, PaymentRequestEvent> processPayment() {
        return event -> new PaymentRequestEvent(event.orderId(), event.amount());
    }
}
```

```yaml
spring:
  cloud:
    stream:
      bindings:
        handleOrderCreated-in-0:
          destination: order-events
          group: order-service-group
        orderEvents-out-0:
          destination: order-events
        processPayment-in-0:
          destination: order-events
        processPayment-out-0:
          destination: payment-requests
      kafka:
        binder:
          brokers: kafka:9092
          auto-create-topics: true
          consumer-properties:
            auto.offset.reset: earliest
```

**Binder implementations:** Kafka, RabbitMQ, Kinesis, Google PubSub, Azure Event Hubs

**Company Frequency:** Netflix (often), Google (medium), Amazon (medium)

---

## 3. Deployment & Operations

### Q: Layered Docker builds for Spring Boot (optimization)

**Answer:**

```dockerfile
# Multi-stage build
FROM eclipse-temurin:17-jdk AS builder
WORKDIR /app
COPY . .
RUN ./mvnw package -DskipTests

# Extract layers for optimal caching
RUN java -Djarmode=layertools -jar target/app.jar extract --destination extracted

# Runtime
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/extracted/dependencies/ ./
COPY --from=builder /app/extracted/spring-boot-loader/ ./
COPY --from=builder /app/extracted/snapshot-dependencies/ ./
COPY --from=builder /app/extracted/application/ ./
EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.JarLauncher"]
```

**Layer benefits:**
| Layer | Contents | Change Frequency | Cache Impact |
|-------|----------|-----------------|--------------|
| `dependencies` | All `*.jar` deps | Rare | High — cached across builds |
| `spring-boot-loader` | Spring Boot loader | Rare | Very stable |
| `snapshot-dependencies` | Snapshot JARs | Moderate | Rebuilt on snapshot change |
| `application` | Your code | Every build | Small, fast rebuilds |

**Optimization tips:**
```yaml
# Optimize JVM for containers
spring:
  docker:
    compose:
      enabled: true
```

```bash
java -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 \
     -XX:+CrashOnOutOfMemoryError \
     -Djava.security.egd=file:/dev/./urandom \
     -jar app.jar
```

**Company Frequency:** All companies (universal)

---

### Q: Kubernetes deployment patterns — sidecar, ambassador, adapter

**Answer:**

**Sidecar pattern** (shared concerns in separate container):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:latest
        - name: istio-proxy   # Sidecar — service mesh
          image: docker.io/istio/proxyv2:1.20
        - name: log-agent     # Sidecar — log shipping
          image: fluent/fluent-bit:latest
```

**Ambassador pattern** (proxy external connectivity):
```yaml
spec:
  containers:
    - name: order-service
      image: order-service:latest
    - name: redis-ambassador  # Ambassador — local proxy to external Redis
      image: redis:7
      command: ["redis-server", "--slaveof", "external-redis.example.com", "6379"]
```

**Adapter pattern** (normalize output):
```yaml
spec:
  containers:
    - name: order-service
      image: order-service:latest
    - name: metrics-adapter  # Adapter — convert app metrics to Prometheus
      image: prometheus-adapter:latest
```

**Company Frequency:** Google (high — Istio), Netflix (high), all K8s users

---

### Q: Blue-green, canary, rolling deployments

**Answer:**

| Strategy | Approach | Traffic Shift | Rollback | Complexity |
|----------|----------|--------------|----------|------------|
| **Rolling** | Gradual pod replacement | Incremental (% pods) | Revert deployment | Low |
| **Blue-green** | Two identical environments | Switch all traffic at once | Switch back to blue | Medium |
| **Canary** | Small subset of traffic | Gradual (% traffic) | Stop sending traffic | High (needs traffic splitting) |

**Canary — Istio VirtualService:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
    - order-service
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: order-service
            subset: v2
          weight: 100
    - route:
        - destination:
            host: order-service
            subset: v1
          weight: 90
        - destination:
            host: order-service
            subset: v2
          weight: 10
```

**Kubernetes Rolling Update:**
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

**Company Frequency:** Netflix (canary heavy), Amazon (rolling + canary), Google (canary with Istio)

---

### Q: Health checks, readiness probes, liveness probes

**Answer:**

```yaml
# Kubernetes probes for Spring Boot
spec:
  containers:
    - name: order-service
      image: order-service:latest
      ports:
        - containerPort: 8080
          name: http
        - containerPort: 8081
          name: management  # actuator port
      livenessProbe:
        httpGet:
          path: /actuator/health/liveness
          port: management
        initialDelaySeconds: 30
        periodSeconds: 10
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /actuator/health/readiness
          port: management
        initialDelaySeconds: 10
        periodSeconds: 5
        failureThreshold: 2
      startupProbe:
        httpGet:
          path: /actuator/health/readiness
          port: management
        initialDelaySeconds: 5
        periodSeconds: 5
        failureThreshold: 30  # generous for slow-starting apps
```

```yaml
# application.yml — separate management port
management:
  server:
    port: 8081
  endpoints:
    web:
      base-path: /actuator
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      probes:
        enabled: true  # enables /health/liveness & /health/readiness
      show-details: when-authorized
```

| Probe | Purpose | Failure Action |
|-------|---------|---------------|
| **Liveness** | Is app alive? | Restart container |
| **Readiness** | Can it serve traffic? | Remove from Service endpoints |
| **Startup** | Has it finished initializing? | Delays liveness checks |

**Company Frequency:** All companies (universal)

---

### Q: Graceful shutdown

**Answer:**

```yaml
# Spring Boot graceful shutdown
server:
  shutdown: graceful  # default: immediate

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # max wait for active requests
```

```java
// Custom graceful shutdown hook
@Component
public class GracefulShutdownHandler implements SmartLifecycle {
    private volatile boolean running;

    @Override
    public void start() { running = true; }

    @Override
    public void stop() {
        running = false;
        System.out.println("Stopping: no new requests accepted");
        // Drain active connections
    }

    @Override
    public boolean isRunning() { return running; }
}

// Kubernetes preStop hook
lifecycle:
  preStop:
    exec:
      command: ["sh", "-c", "sleep 5 && curl -X POST http://localhost:8081/actuator/shutdown"]
```

**Kubernetes Pod termination flow:**
1. Pod enters `Terminating` state
2. PreStop hook executes (if configured)
3. SIGTERM sent to PID 1
4. Grace period starts (default 30s)
5. After grace period → SIGKILL

**Company Frequency:** All companies (universal)

---

## 4. Company-Specific Architectures

### Q: [Netflix] How did Netflix build the microservices ecosystem?

**Answer:**
Netflix pioneered most of the Spring Cloud ecosystem:

| Component | Tool | Purpose |
|-----------|------|---------|
| Service Registry | **Eureka** | Service discovery |
| Client Load Balancing | **Ribbon** (deprecated) | Client-side load balancing |
| Circuit Breaker | **Hystrix** (deprecated) | Fault tolerance |
| API Gateway | **Zuul** (deprecated) | Routing, filtering |
| Configuration | **Archaius** | Dynamic properties |
| Distributed Tracing | **Sleuth** (now Micrometer) | Trace propagation |
| Chaos Engineering | **Chaos Monkey, Chaos Kong** | Resilience testing |

**Netflix's evolution:**
1. **Monolith → SOA** (2009): Broke catalog into services
2. **Cloud migration** (2010+): Moved to AWS, built resilience patterns
3. **OSS contributions** (2012+): Open-sourced entire stack as Netflix OSS
4. **Deprecation wave** (2018+): Hystrix → Resilience4j, Ribbon → Spring Cloud LoadBalancer, Zuul → Spring Cloud Gateway
5. **Current state**: Move towards service mesh (Istio), GraphQL BFF, reactive streams

**Key architecture principles:**
- Every service has its own database
- Stateless services → horizontal scaling
- Bulkheading per service
- Redundant deployments across AZs/regions
- Automated canary analysis (Automated Canary Analysis — Kayenta)

---

### Q: [Uber] How does Uber handle domain-oriented microservices?

**Answer:**
Uber's architecture evolved from a monolith (2010) to thousands of microservices:

**Domain-oriented model:**
- **Domain**: A group of related services (e.g., "Rides Domain", "Eats Domain", "Freight Domain")
- **Domain Service**: Entry point for a domain
- **Domain-specific scaling**: Each domain scales independently

**Uber technology stack:**
- **Language**: Go (primary), Java (legacy/backend), Python (ML)
- **Messaging**: Kafka (event bus for all services)
- **Storage**: Schemaless (MySQL-based), Cassandra, DocStore
- **RPC**: Thrift (internal), gRPC (newer services)
- **Service discovery**: Hyperbahn (Ringpop) → internal DNS
- **Circuit breaking**: Internal (ringpop failure detection)
- **Deployment**: Peloton (Uber's K8s-like platform)
- **Config**: Uber's internal config service (dynamic, feature flags)

**Uber interview focus:**
- Design a ride-matching system at scale
- Handle location-based queries (geospatial indexing)
- Design a pricing engine (surge pricing)
- Distributed systems trade-offs
- Very systems design heavy

---

### Q: [Amazon] Two-pizza teams and API-first design

**Answer:**
Amazon's internal microservices mandate (from Bezos' 2002 API mandate):

1. **Two-pizza teams** (~6-10 people): Own a service end-to-end
2. **API-first design**: Every team communicates via service APIs
3. **You build it, you run it**: Developers own operations (on-call)
4. **Internal APIs** are treated like external — versioned, documented, deprecated properly
5. **No direct DB access**: All data access through service API

**Internal API constraints:**
```
- All teams will expose their data and functionality through service interfaces
- Teams must communicate with each other through these interfaces
- No other form of interprocess communication is allowed
- All service interfaces, without exception, must be designed from the ground up to be externalizable
- Anyone who doesn't do this will be fired

— Jeff Bezos, 2002
```

**Amazon interview focus:**
- Design an e-commerce system (naturally)
- "How would you design Amazon's order processing?"
- Load balancing, caching, database sharding
- PR/FAQ: Amazon's unique interview format
- Leadership principles heavily tested

---

### Q: [Google] Service mesh and strict API versioning

**Answer:**

**Service mesh (Istio):**
```
Application Pod
┌─────────────────────────┐
│  order-service container │
│  istio-proxy (Envoy)    │ ← Sidecar: intercepts all traffic
└─────────────────────────┘
         ↕
Istio Control Plane (Istiod)
├── Pilot: Service discovery, traffic management
├── Citadel: mTLS cert management
└── Galley: Config validation, distribution
```

**Google's API versioning:**
```protobuf
// Strict versioning with proto3
syntax = "proto3";
package order.v1;  // version in package name

import "google/protobuf/timestamp.proto";

service OrderService {
    rpc GetOrder(GetOrderRequest) returns (Order);
    rpc CreateOrder(CreateOrderRequest) returns (Order);
}

message Order {
    string order_id = 1;
    string customer_id = 2;
    google.protobuf.Timestamp created_at = 3;
    // Field 4 was "status" (removed) — never reuse field numbers!
    reserved 4;
    reserved "status_v1";  // old field name reserved
}
```

**Google interview focus:**
- Deep DSA (not as relevant for backend roles)
- System design: scale to Google level
- API design, idempotency
- Distributed consensus (Paxos, Raft)
- Borg/Omega (predecessors to K8s)
- Very whiteboard-heavy

---

### Q: [Spotify] Squad model and event-driven backend

**Answer:**

**Squad model:**
```
Tribe
├── Squad (autonomous, ~6-8 people)
│   ├── Product Owner
│   ├── Engineers (backend, frontend, data)
│   └── Agile Coach
├── Chapter (guild across squads)
│   ├── Backend Chapter
│   └── Frontend Chapter
└── Tribe Lead
```

**Spotify's backend:**
- **Languages**: Java (primary), Python (ML/services)
- **Messaging**: Kafka (event backbone for all services)
- **Storage**: Cassandra, PostgreSQL, BigTable
- **Infrastructure**: GCP (Google Cloud), Kubernetes
- **Backend-for-frontend (BFF)**: Each client has its own API layer
- **Feature toggles**: Heavy feature flag usage for gradual rollout
- **Testing in production**: Gradual rollout, metrics-driven decisions

**Spotify event-driven patterns:**
- Every major action publishes events (play track, create playlist, etc.)
- Services communicate asynchronously via event streams
- Real-time features via WebSocket/PubSub

**Spotify interview focus:**
- Design a music recommendation system
- Design a real-time collaborative playlist feature
- Event-driven architecture design
- Less algorithm-heavy, more practical system design

---

> **End of MICROSERVICES_INTERVIEW_GUIDE.md**
> Total questions: ~30+ covering patterns, communication, deployment, company-specific
