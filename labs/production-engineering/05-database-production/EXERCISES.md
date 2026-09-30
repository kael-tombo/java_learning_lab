# EXERCISES: Database Performance & Connection Sizing
## Lab 05 | Production Engineering Academy

---

## Exercise 1: Simulate and Resolve HikariCP Connection Starvation

### Objective
Trigger connection pool exhaustion under load, diagnose it via HikariCP JMX/Micrometer metrics, and fix it using transaction scope minimization.

### Broken Code
```java
package com.learning.production.lab05;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BrokenCheckoutService {

    private final PaymentGatewayClient gatewayClient;
    private final OrderRepository orderRepository;

    @Transactional // Connection acquired here
    public void checkout(OrderRequest request) {
        Order order = orderRepository.save(new Order(request));
        
        // Simulates 2.5 second network delay to payment processor
        gatewayClient.chargeCard(request.paymentDetails()); 
        
        order.setStatus(OrderStatus.PAID);
        orderRepository.save(order);
    } // Connection released only here!
}
```

### Tasks
1. Configure HikariCP with `maximumPoolSize: 5`, `connectionTimeout: 1000`.
2. Generate 20 concurrent checkout requests using a simple JUnit multi-thread test or Apache JMeter.
3. Observe `ConnectionTimeoutException: Connection is not available, request timed out after 1000ms`.
4. Refactor the code by moving `gatewayClient.chargeCard` outside `@Transactional` using `TransactionTemplate`.
5. Re-run 20 concurrent threads; verify all transactions succeed within milliseconds without connection timeouts.

---

## Exercise 2: Benchmark N+1 Query Resolution

### Objective
Measure SQL statement count and latency differences between:
1. Default lazy loading (N+1 query problem).
2. `@EntityGraph` (SQL JOIN).
3. `hibernate.default_batch_fetch_size: 50`.

### Tasks
1. Populate database with 100 Customers, each having 5 Orders.
2. Query all customers and iterate over their orders. Count SQL statements executed using Hibernate statistics (`hibernate.generate_statistics: true`).
3. Verify that option 1 generates 101 queries.
4. Verify that option 2 generates 1 query.
5. Verify that option 3 generates 3 queries.
6. Record memory and latency benchmarks for each strategy.
