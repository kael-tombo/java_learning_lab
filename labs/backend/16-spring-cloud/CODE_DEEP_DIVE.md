# Code Deep Dive: Spring Cloud Infrastructure

## Eureka Server Implementation

### @EnableEurekaServer
The @EnableEurekaServer annotation activates the Eureka server components. It imports EurekaServerMarkerConfiguration which creates a marker bean. Spring Cloud's auto-configuration detects this bean and initializes:
- EurekaServerConfig: Server-side configuration
- PeerEurekaNodes: Cluster replication
- EurekaServerContext: Application context for the registry
- ApplicationResource/InstanceResource: REST endpoints

### Registration Endpoint
Eureka clients POST to /apps/{appName} with instance metadata. The server:
1. Validates the instance info
2. Adds to ConcurrentHashMap registry
3. Replicates to peer nodes
4. Returns 204 No Content

## Circuit Breaker with Resilience4J

### State Machine Implementation
Resilience4J's CircuitBreaker uses a finite state machine internally:

`
CircuitBreakerStateMachine
â”œâ”€â”€ ClosedState
â”‚   â”œâ”€â”€ onSuccess(): Increment success count
â”‚   â”œâ”€â”€ onFailure(): Increment failure count, check threshold
â”‚   â””â”€â”€ checkThreshold(): If failure rate > threshold, transition to OPEN
â”œâ”€â”€ OpenState
â”‚   â”œâ”€â”€ acquirePermission(): Throw CallNotPermittedException
â”‚   â””â”€â”€ onSuccess()/onFailure(): No-op (requests blocked)
â””â”€â”€ HalfOpenState
    â”œâ”€â”€ acquirePermission(): Allow limited requests
    â”œâ”€â”€ onSuccess(): If enough successes, transition to CLOSED
    â””â”€â”€ onFailure(): Transition to OPEN
`

### Sliding Window Implementation
Two types of sliding windows:
1. **Count-based**: Circular array of size N
2. **Time-based**: Ring buffer of time buckets

The internal AggregationCircuitBreaker stores:
- totalSuccess count
- totalFailure count
- currentTimestamp for time-based windows

## Load Balancing Strategy

### RoundRobinLoadBalancer
Spring Cloud LoadBalancer's default implementation:
1. ServiceInstanceListSupplier provides instances
2. RoundRobinLoadBalancer maintains AtomicInteger position
3. position.getAndIncrement() % instanceCount selects instance
4. Returns selected instance as Mono<Response<ServiceInstance>>

### Reactive Load Balancing
For WebFlux applications:
- ReactiveLoadBalancer interface
- ExchangeFilterFunction intercepts outgoing requests
- Chooses instance before creating ClientRequest

## API Gateway Route Resolution

### RouteDefinitionRouteLocator
The gateway's RouteLocator:
1. Reads RouteDefinition from configuration or RouteDefinitionLocator
2. Converts to Route objects via RouteDefinitionRouteLocator
3. Each Route has predicates, filters, URI, and order
4. Routes are sorted by order (lower = higher priority)

### Request Matching
When a request arrives:
1. GatewayHandlerMapping gets candidate routes
2. For each route, all predicates must match
3. First matching route is chosen
4. Filter chain is built from route filters + global filters

## Config Server

### EnvironmentRepository
The EnvironmentController exposes:
- /{application}/{profile}[/{label}]
- Reads from EnvironmentRepository (Git, Vault, JDBC, etc.)
- Returns Environment object with PropertySources

### Property Resolution
1. EnvironmentComposite combines multiple repositories
2. PropertySource created for each configuration file
3. Ordered by priority: application override, profile-specific
4. Encrypted values decrypted using {cipher} prefix

## Distributed Tracing with Micrometer

### ObservationRegistry
Micrometer Tracing integrates via Observation API:
1. Observation.createNotStarted() creates observation
2. Context captures trace/span IDs
3. Handlers (TracingAwareMeterObservationHandler) create spans
4. Span is exported to Zipkin, Jaeger, or OTEL collector

### Automatic Instrumentation
Spring Boot auto-configures:
- ObservedAspect for @Observed annotations
- WebMvcObservationFilter for HTTP requests
- RestTemplate/WebClient interceptors for outgoing calls
- Messaging instrumentation for Kafka, RabbitMQ
