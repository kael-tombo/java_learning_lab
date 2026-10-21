# Exercises: Spring Cloud

## Exercise 1: Service Registry Setup
**Objective**: Set up a Eureka server and register a client.

### Task
1. Create a Spring Boot application annotated with @EnableEurekaServer
2. Configure application.yml with server port 8761 and self-preservation
3. Create a simple REST service and annotate with @EnableDiscoveryClient
4. Register the client with the Eureka server
5. Verify registration on Eureka dashboard at http://localhost:8761

### Expected Outcome
- Eureka dashboard lists the registered service
- Heartbeat renewals visible in logs
- Service instance shows IP, port, and status

## Exercise 2: Configuration Server
**Objective**: Implement distributed configuration with Spring Cloud Config.

### Task
1. Create a config server with @EnableConfigServer
2. Set up a Git-backed repository for configuration files
3. Create application.yml for a client service with database configuration
4. Create profile-specific files: application-dev.yml, application-prod.yml
5. Test configuration resolution with curl http://localhost:8888/myapp/dev

### Expected Outcome
- Config server returns merged properties
- Profile-specific values override defaults
- Client can bootstrap configuration from config server

## Exercise 3: Circuit Breaker
**Objective**: Implement circuit breaker pattern with Resilience4J.

### Task
1. Add spring-cloud-starter-circuitbreaker-resilience4j dependency
2. Create a service that calls an external HTTP API
3. Wrap the call with @CircuitBreaker annotation
4. Configure failure threshold (50%), wait duration (5s), window size (20)
5. Create a fallback method for when the circuit is open
6. Test by stopping the external service

### Expected Outcome
- Circuit opens after 50% failures in the window
- Fallback method executes during open circuit
- Circuit transitions to half-open after wait duration

## Exercise 4: API Gateway
**Objective**: Configure Spring Cloud Gateway as an API Gateway.

### Task
1. Create a gateway service with spring-cloud-starter-gateway
2. Configure routes to product-service and order-service
3. Add a global filter for request logging
4. Add a rate-limiting filter using RequestRateLimiter
5. Configure path-based routing: /api/products/** -> product-service

### Expected Outcome
- Requests to gateway are routed to correct services
- Rate limiting returns 429 when exceeded
- Request logging shows incoming requests and routing

## Exercise 5: Complete Microservices Stack
**Objective**: Build a complete microservices system.

### Task
1. Start Eureka server, Config server, and Gateway
2. Create two microservices: inventory-service and cart-service
3. Each service registers with Eureka and loads config from Config server
4. Services communicate via RestTemplate with LoadBalanced annotation
5. Add circuit breakers for inter-service calls
6. Verify end-to-end request flow through gateway

### Expected Outcome
- Full system starts and all components register
- Gateway routes to appropriate services
- Circuit breakers handle service failures gracefully
- Configuration changes propagate via /actuator/refresh
