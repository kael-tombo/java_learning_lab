# Quiz: Spring Cloud

## Question 1
What is the default heartbeat interval for Eureka clients?
A) 10 seconds
B) 30 seconds
C) 60 seconds
D) 90 seconds

**Answer: B** - Default heartbeat interval is 30 seconds.

## Question 2
Which annotation enables a Spring Boot application to act as a Eureka server?
A) @EnableEurekaClient
B) @EnableDiscoveryServer
C) @EnableEurekaServer
D) @EurekaServer

**Answer: C** - @EnableEurekaServer activates the Eureka server components.

## Question 3
In Resilience4J, what is the default failure rate threshold for opening a circuit breaker?
A) 25%
B) 50%
C) 75%
D) 90%

**Answer: B** - Default failure rate threshold is 50%.

## Question 4
What is the purpose of the HALF_OPEN state in a circuit breaker?
A) All requests are blocked
B) Limited test requests are allowed to check if service recovered
C) The circuit breaker is disabled
D) All requests pass through with reduced timeout

**Answer: B** - HALF_OPEN allows limited requests to test if the underlying service has recovered.

## Question 5
Which Spring Cloud Gateway predicate matches requests by HTTP method?
A) PathRoutePredicateFactory
B) MethodRoutePredicateFactory
C) HeaderRoutePredicateFactory
D) QueryRoutePredicateFactory

**Answer: B** - MethodRoutePredicateFactory matches on HTTP methods (GET, POST, etc.).

## Question 6
What is the default port for Spring Cloud Config Server?
A) 8080
B) 8761
C) 8888
D) 9411

**Answer: C** - Config Server defaults to port 8888.

## Question 7
Which annotation enables load-balanced RestTemplate?
A) @LoadBalanced
B) @LoadBalancer
C) @EnableBalancing
D) @Balanced

**Answer: A** - @LoadBalanced on the RestTemplate bean enables client-side load balancing.

## Question 8
What happens when Eureka enters self-preservation mode?
A) All instances are immediately evicted
B) Instances are not evicted even if heartbeats fail
C) The server shuts down
D) New registrations are rejected

**Answer: B** - Self-preservation stops instance eviction to protect against network partitions.

## Question 9
What is the default sliding window size in Resilience4J circuit breaker?
A) 10
B) 50
C) 100
D) 200

**Answer: C** - Default sliding window size is 100.

## Question 10
Which filter type in Spring Cloud Gateway is applied to all routes?
A) Route filters
B) Global filters
C) Predicate filters
D) Custom filters

**Answer: B** - Global filters are applied to all routes automatically.

## Question 11
What is a Trace ID in distributed tracing?
A) Unique ID for each log statement
B) Unique ID for an entire request flow across services
C) Server instance identifier
D) Application version identifier

**Answer: B** - Trace ID traces a request end-to-end across multiple services.

## Question 12
Which Resilience4J pattern limits the number of concurrent calls?
A) CircuitBreaker
B) Retry
C) Bulkhead
D) RateLimiter

**Answer: C** - Bulkhead limits concurrent calls by isolating resources.
