# Step by Step: Spring Cloud

## Setting Up a Complete Microservices Stack

### Step 1: Create Eureka Server
`java
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
`

`yaml
# application.yml
server:
  port: 8761
eureka:
  client:
    register-with-eureka: false
    fetch-registry: false
  server:
    enable-self-preservation: false
`

### Step 2: Create Config Server
`java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
`

`yaml
# application.yml
server:
  port: 8888
spring:
  cloud:
    config:
      server:
        git:
          uri: (link removed)
          search-paths: '{application}'
`

### Step 3: Create a Client Service
`java
@SpringBootApplication
@EnableDiscoveryClient
public class ProductServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
}
`

`yaml
# bootstrap.yml
spring:
  application:
    name: product-service
  cloud:
    config:
      uri: http://localhost:8888

# application.yml
server:
  port: 0  # Random port
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    instance-id: :
`

### Step 4: Add Circuit Breaker
`java
@Service
public class ProductService {
    
    @CircuitBreaker(name = "inventoryService", fallbackMethod = "getDefaultInventory")
    public Inventory getInventory(String productId) {
        return inventoryClient.getInventory(productId);
    }
    
    private Inventory getDefaultInventory(String productId, Throwable t) {
        return new Inventory(productId, 0, "UNAVAILABLE");
    }
}
`

`yaml
# application.yml
resilience4j:
  circuitbreaker:
    instances:
      inventoryService:
        sliding-window-size: 20
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10000
        permitted-number-of-calls-in-half-open-state: 5
`

### Step 5: Create API Gateway
`java
@SpringBootApplication
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
    
    @Bean
    public RouteLocator customRoutes(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("products", r -> r.path("/api/products/**")
                .filters(f -> f
                    .circuitBreaker(config -> config
                        .setName("productsCB")
                        .setFallbackUri("forward:/fallback/products"))
                    .retry(3))
                .uri("lb://product-service"))
            .route("orders", r -> r.path("/api/orders/**")
                .uri("lb://order-service"))
            .build();
    }
}
`

### Step 6: Add Distributed Tracing
`xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
`

`yaml
management:
  tracing:
    sampling:
      probability: 1.0
  zipkin:
    tracing:
      endpoint: http://localhost:9411/api/v2/spans
`

### Step 7: Verify the Stack
`ash
# 1. Start Eureka
mvn spring-boot:run -pl eureka-server

# 2. Start Config Server
mvn spring-boot:run -pl config-server

# 3. Start services
mvn spring-boot:run -pl product-service
mvn spring-boot:run -pl order-service

# 4. Start Gateway
mvn spring-boot:run -pl gateway-service

# 5. Test end-to-end
curl http://localhost:8080/api/products
curl http://localhost:8080/api/orders
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\16-spring-cloud "VISUAL_GUIDE.md") @"
# Visual Guide: Spring Cloud

## Architecture Diagram

`
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                        External Clients                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
                             â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     API Gateway (Port 8080)                          â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Security Filter â†’ Rate Limiter â†’ Route Matcher â†’ Load Balanceâ”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”‚              â”‚              â”‚
              â–¼              â–¼              â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Product Service     â”‚ â”‚ Order       â”‚ â”‚ User Service        â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚ â”‚ Service     â”‚ â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ Circuit Breakerâ—„â”€â”¼â”€â”¼â”€â”¤             â”‚ â”‚ â”‚ Circuit Breakerâ—„â”€â”¼â”€â”¼â”€â”€â”
â”‚ â”‚ Bulkhead        â”‚ â”‚ â”‚ â”‚             â”‚ â”‚ â”‚ Bulkhead        â”‚ â”‚  â”‚
â”‚ â”‚ Retry           â”‚ â”‚ â”‚ â”‚             â”‚ â”‚ â”‚ Retry           â”‚ â”‚  â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚ â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
        â”‚                        â”‚                                      â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                 â”‚
                                 â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     Service Registry (Eureka)                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ Product     â”‚ â”‚ Order       â”‚ â”‚ User        â”‚ â”‚ Gateway     â”‚  â”‚
â”‚  â”‚ Svc:8081    â”‚ â”‚ Svc:8082    â”‚ â”‚ Svc:8083    â”‚ â”‚ Svc:8080    â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                 â”‚
                                 â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     Config Server (Port 8888)                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Git Repo â†’ EnvironmentRepository â†’ Encrypted Property Decode â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

## Circuit Breaker State Machine

`
      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
      â”‚                                            â”‚
      â–¼                                            â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   Failure > threshold    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  CLOSED  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚   OPEN   â”‚ â”‚
â”‚ (Normal) â”‚                          â”‚ (Blocked)â”‚ â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
      â–²                                    â”‚       â”‚
      â”‚         Wait duration expires      â”‚       â”‚
      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚
                  â–¼                                 â”‚
         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                          â”‚
         â”‚  HALF_OPEN   â”‚                          â”‚
         â”‚  (Testing)   â”‚                          â”‚
         â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜                          â”‚
                â”‚                                  â”‚
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”                          â”‚
        â–¼               â–¼                          â”‚
   Success >        Failure >                      â”‚
   threshold        threshold                       â”‚
        â”‚               â”‚                          â”‚
        â–¼               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â”‚  CLOSED  â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

## Request Flow with Tracing

`
Trace ID: abc123
â”œâ”€â”€ Span 1: [Gateway] receiveRequest â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   â”œâ”€â”€ Span 2: [Gateway] rateLimitCheck (2ms)             â”‚
â”‚   â”œâ”€â”€ Span 3: [Gateway] authenticate (5ms)              â”‚
â”‚   â”œâ”€â”€ Span 4: [Gateway] routeToProductService (1ms)     â”‚
â”‚   â””â”€â”€ Span 5: [Product Service] handleRequest â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚       â”œâ”€â”€ Span 6: [Product] getFromCache (0.5ms)        â”‚
â”‚       â”œâ”€â”€ Span 7: [Product] circuitBreakerCheck (0.1ms) â”‚
â”‚       â””â”€â”€ Span 8: [Product] inventoryCall â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚           â””â”€â”€ Span 9: [Inventory] checkStock (10ms)     â”‚
â””â”€â”€â”€â”€ Total: 45ms â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

## Configuration Hierarchy

`
application.yml (service-specific)
  â””â”€â”€ application-{profile}.yml (profile-specific)
      â””â”€â”€ bootstrap.yml (config server connection)
          â””â”€â”€ Config Server:
              â””â”€â”€ {application}.yml (Git repository)
                  â””â”€â”€ {application}-{profile}.yml
                      â””â”€â”€ application.yml (shared defaults)
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\16-spring-cloud "INTERNALS.md") @"
# Internals: Spring Cloud

## Eureka Server Internals

### Registry Data Structure
Eureka uses a ConcurrentHashMap for instance registry:
`java
// InstanceRegistry.java
private final ConcurrentHashMap<String, Map<String, Lease<InstanceInfo>>> registry
    = new ConcurrentHashMap<>();
// Key: appName, Value: Map<instanceId, Lease<InstanceInfo>>
`

### Lease Management
Each registered instance has a Lease object:
- **lastRenewalTimestamp**: Updated on heartbeat
- **evictionTimestamp**: Set when evicted
- **serviceUpTimestamp**: When first registered
- **duration**: Lease period in seconds

### Peer Replication
Eureka replicates state changes to peer nodes via:
1. HTTP replication requests to /eureka/v2/peerreplication
2. Batch or individual replication modes
3. Exponential backoff on replication failure
4. Consistent hash ring for peer distribution

## Config Server Internals

### EnvironmentRepository Composition
The EnvironmentController delegates to EnvironmentRepository:
`java
public interface EnvironmentRepository {
    Environment findOne(String application, String profile, String label);
}
`

Implementations:
1. **GitEnvironmentRepository**: Clones Git repo, reads files
2. **NativeEnvironmentRepository**: Reads local filesystem
3. **VaultEnvironmentRepository**: Reads from HashiCorp Vault
4. **JdbcEnvironmentRepository**: Reads from database

### Property Source Resolution
Multiple property sources are merged with priority:
1. Overrides (highest priority)
2. {application}-{profile}.yml
3. {application}.yml
4. application-{profile}.yml (lowest priority shared config)

## Circuit Breaker Internals (Resilience4J)

### Ring Bit Buffer
Resilience4J uses a Ring Bit Buffer for the sliding window:
- Bit array of size N (sliding window size)
- Each bit represents success (1) or failure (0)
- New results overwrite oldest results
- Failure rate = count_failures / N

### State Transition Logic
`java
// AbstractCircuitBreaker.java
private void handleFailure() {
    if (state.get() instanceof ClosedState) {
        closedState.onFailure(); // increment failure count
        if (closedState.isThresholdExceeded()) {
            state.set(new OpenState()); // transition to OPEN
            publishEvent(CircuitBreakerOnStateTransitionEvent);
        }
    }
}
`

## Gateway Internals

### Route Resolution
RouteDefinitionRouteLocator converts RouteDefinition to Route:
1. Read RouteDefinition from YAML/properties or RouteDefinitionLocator
2. Create Predicate instances from PredicateDefinition
3. Create GatewayFilter instances from FilterDefinition
4. Combine predicates and filters into Route object
5. Cache routes for performance

### Request Handling Flow
`
WebHandler
  â””â”€â”€ DispatcherHandler
      â””â”€â”€ SimpleHandlerAdapter
          â””â”€â”€ GatewayHandlerMapping.getHandler()
              â””â”€â”€ RoutePredicateHandlerMapping.getHandler()
                  â””â”€â”€ FilteringWebHandler.handle()
                      â””â”€â”€ Route.getFilters() ordered + GlobalFilters
                          â””â”€â”€ Target service call
`

## Load Balancer Internals

### RoundRobinLoadBalancer
`java
public Mono<Response<ServiceInstance>> choose(Request request) {
    return serviceInstanceListSupplier.get().collectList()
        .map(instances -> {
            int pos = position.incrementAndGet() % instances.size();
            return new DefaultResponse(instances.get(pos));
        });
}
`

## Resilience4J Thread Pool Bulkhead

### Internal Structure
`java
public class ThreadPoolBulkhead {
    private final ThreadPoolExecutor executorService;
    private final Semaphore semaphore; // Controls queue depth
    private final BulkheadConfig config;
    
    public CompletionStage<T> acquirePermission() {
        if (semaphore.tryAcquire()) {
            return CompletableFuture.supplyAsync(() -> {
                // Execute in isolated thread pool
                return supplier.get();
            }, executorService);
        }
        throw new BulkheadFullException("Bulkhead is full");
    }
}
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\16-spring-cloud "HOW_IT_WORKS.md") @"
# How It Works: Spring Cloud

## How Service Discovery Works

When a microservice starts, it sends a registration request to the Eureka server with metadata (hostname, port, health check URL, app name). The Eureka server stores this in an in-memory registry. Other services query Eureka to find available instances by logical service name. Eureka clients cache the registry locally and refresh periodically. The load balancer uses the local cache to select an instance without querying Eureka on every request.

## How Configuration Management Works

Spring Cloud Config works through a bootstrap phase. When a service starts, its bootstrap.yml tells it to contact the Config Server. The Config Server reads configuration files from a Git repository and returns them as property sources. The service merges these with its own application.yml. The @RefreshScope annotation allows beans to be recreated with new property values when /actuator/refresh is called.

## How Circuit Breakers Work

The circuit breaker wraps a method call. It tracks successes and failures in a sliding window. When the failure rate exceeds a threshold, the circuit opens and subsequent calls fail immediately (or use a fallback). After a configurable wait time, the circuit transitions to half-open and allows a few test calls. If these succeed, the circuit closes again.

## How API Gateway Works

The gateway intercepts incoming HTTP requests. It matches requests against configured routes using predicates (path patterns, headers, query parameters). For the first matching route, it applies a chain of filters (authentication, rate limiting, header modification) and forwards the request to the target service using load-balanced HTTP calls.

## How Load Balancing Works

Spring Cloud LoadBalancer uses a ServiceInstanceListSupplier to get available instances (from Eureka). The RoundRobinLoadBalancer cycles through instances using an atomic counter. Each call to choose() increments the counter and picks instances.get(counter % size). The response contains the selected instance's host and port.

## How Distributed Tracing Works

Micrometer Tracing generates a Trace ID when a request enters the system. This ID is propagated to downstream services via HTTP headers (traceparent, tracestate). Each service creates spans for its work. Spans include start/end timestamps, duration, and annotations. All spans are sent to a collector (Zipkin, Jaeger) which assembles them into a complete trace.

## How Bulkheads Work

Bulkheads isolate resources to prevent one failing component from taking down the system. Thread pool bulkheads create separate thread pools for each service call. If a pool is exhausted, subsequent calls fail immediately instead of queuing up and consuming all threads. Semaphore bulkheads limit concurrent calls without creating new threads.

## How Rate Limiting Works

Rate limiting uses the token bucket algorithm. A bucket holds a number of tokens. Tokens are added at a fixed rate (refill rate). Each request consumes a token. If the bucket is empty, the request is rejected (HTTP 429). The bucket capacity allows for bursts of traffic up to the maximum token count.
