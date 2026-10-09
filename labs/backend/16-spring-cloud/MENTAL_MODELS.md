# Mental Models: Spring Cloud

## 1. The Phone Book Model (Service Discovery)
Think of Eureka as a phone book. Services register their contact details (IP, port) like listing a phone number. When one service needs to call another, it looks up the phone book instead of memorizing numbers. If a service moves (new IP), it updates the phone book. This way, no one needs to remember specific addresses.

## 2. The Circuit Breaker Model
A circuit breaker in your house trips when there's a fault, preventing electrical fires. Similarly, Resilience4J trips when a service fails repeatedly, preventing cascading failures. The half-open state is like trying one appliance after the breaker trips to see if the fault is cleared.

## 3. The Mail Forwarding Model (API Gateway)
The API Gateway is like a mail forwarding service. External clients send mail to one address (the gateway). The gateway reads the address and forwards to the correct person (microservice). It can also reject mail from unknown senders (authentication) and limit how much mail each person receives (rate limiting).

## 4. The Hotel Key Model (Configuration)
Spring Cloud Config is like a hotel front desk. When you arrive (service starts), you ask the front desk for your room key and information. If you need updated info later, you call the front desk again (/actuator/refresh). The Git repository is the hotel's master book of all room assignments.

## 5. The Bucket Brigade Model (Distributed Tracing)
Distributed tracing is like firefighters passing buckets of water. Each firefighter (service) adds their time and action to the bucket's log. The Trace ID is the bucket number. At the end, all logs are collected to see how fast the bucket moved through the entire brigade.

## 6. The Lifeboat Model (Bulkhead)
A ship has multiple watertight compartments (bulkheads). If one compartment floods, the others keep the ship afloat. Similarly, thread pool bulkheads isolate failures. If the inventory service thread pool is flooded with slow requests, the order service thread pool remains unaffected.

## 7. The Token Booth Model (Rate Limiting)
Rate limiting is like a toll booth with a limited number of tokens. Tokens are distributed at a fixed rate (like cars arriving at a set frequency). If too many cars arrive, they wait or are turned away. Burst capacity is like having extra tokens stored up from quiet periods.

## 8. The GPS Navigation Model (Load Balancing)
Load balancing is like GPS navigation with traffic awareness. When you ask for directions, the GPS checks multiple routes (service instances) and chooses the least congested one. If a road is closed (instance down), the GPS reroutes to an alternative.

## 9. The Restaurant Kitchen Model (Service Architecture)
The API Gateway is the host seating guests. Eureka is the reservation list. Config Server is the recipe book. Each station (appetizer, main course, dessert) is a microservice. The circuit breaker is the fire suppression system. The load balancer is the expediter who distributes orders to available chefs.

## 10. The Jenga Model (System Resilience)
Microservices with circuit breakers is like playing Jenga with safety nets. Each block is a service. If you remove one (service failure), the tower (system) should still stand. Circuit breakers prevent the whole tower from toppling by isolating weak blocks. Self-preservation mode in Eureka is like the tower settling — don't remove blocks too aggressively.
