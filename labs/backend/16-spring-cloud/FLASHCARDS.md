# Flashcards: Spring Cloud

## Card 1
**Front**: What annotation enables a Eureka server?
**Back**: @EnableEurekaServer on a @SpringBootApplication class.

## Card 2
**Front**: Default Eureka heartbeat interval?
**Back**: 30 seconds.

## Card 3
**Front**: What is the circuit breaker half-open state?
**Back**: State where limited test requests are allowed to check if the service has recovered.

## Card 4
**Front**: What replaced Netflix Hystrix in Spring Cloud?
**Back**: Resilience4J.

## Card 5
**Front**: What replaced Netflix Ribbon?
**Back**: Spring Cloud LoadBalancer.

## Card 6
**Front**: What replaced Netflix Zuul?
**Back**: Spring Cloud Gateway.

## Card 7
**Front**: Default port for Spring Cloud Config Server?
**Back**: 8888.

## Card 8
**Front**: What does @LoadBalanced do?
**Back**: Enables client-side load balancing on RestTemplate beans using service discovery.

## Card 9
**Front**: What is Eureka self-preservation mode?
**Back**: A safety mechanism that stops instance eviction during network partitions to prevent cascading failures.

## Card 10
**Front**: Default Resilience4J failure rate threshold?
**Back**: 50%.

## Card 11
**Front**: What is a Trace ID?
**Back**: A unique identifier for a complete request flow across multiple services in distributed tracing.

## Card 12
**Front**: What does a bulkhead pattern prevent?
**Back**: Thread exhaustion by isolating thread pools for different service calls.

## Card 13
**Front**: What is the default sliding window size in Resilience4J?
**Back**: 100 calls.

## Card 14
**Front**: How do you refresh configuration without restarting?
**Back**: Call /actuator/refresh endpoint or use Spring Cloud Bus to broadcast refresh events.

## Card 15
**Front**: What does the API Gateway provide?
**Back**: Single entry point with routing, authentication, rate limiting, and cross-cutting concerns.

## Card 16
**Front**: What is the token bucket algorithm used for?
**Back**: Rate limiting — tokens refill at a fixed rate, each request consumes one token.

## Card 17
**Front**: What happens when a circuit breaker is OPEN?
**Back**: All requests fail immediately without calling the underlying service, often using a fallback method.

## Card 18
**Front**: What is the purpose of @RefreshScope?
**Back**: Marks beans to be recreated when configuration properties are refreshed.
