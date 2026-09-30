# CODE DEEP DIVE: Database Performance & Connection Engineering
## Lab 05 | Production Engineering Academy

---

## Pattern 1: Production-Grade HikariCP Configuration

```java
package com.learning.production.lab05;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import io.micrometer.core.instrument.MeterRegistry;

import javax.sql.DataSource;
import java.time.Duration;

public class ProductionDataSourceFactory {

    public static DataSource createProductionDataSource(MeterRegistry meterRegistry) {
        HikariConfig config = new HikariConfig();

        // 1. Connection coordinates
        config.setJdbcUrl("jdbc:postgresql://db-primary.production.internal:5432/core_banking?sslmode=verify-full");
        config.setUsername("app_banking_user");
        config.setPassword(System.getenv("DB_SECRET_PASSWORD"));
        config.setDriverClassName("org.postgresql.Driver");

        // 2. Pool Sizing: Keep minimumIdle EQUAL to maximumPoolSize to eliminate connection churn
        config.setMaximumPoolSize(15);
        config.setMinimumIdle(15);

        // 3. Timeouts
        config.setConnectionTimeout(Duration.ofSeconds(3).toMillis()); // Fast fail fast if pool exhausted
        config.setIdleTimeout(Duration.ofMinutes(10).toMillis());
        config.setMaxLifetime(Duration.ofMinutes(28).toMillis()); // 2 minutes less than infra firewall/L4 drop
        config.setKeepaliveTime(Duration.ofMinutes(2).toMillis()); // Prevent idle socket termination
        config.setValidationTimeout(Duration.ofSeconds(2).toMillis());

        // 4. Leak Detection: Log warning if a thread holds a connection without closing for > 5 seconds
        config.setLeakDetectionThreshold(Duration.ofSeconds(5).toMillis());

        // 5. Driver Optimizations (PostgreSQL specific)
        config.addDataSourceProperty("reWriteBatchedInserts", "true");
        config.addDataSourceProperty("prepareThreshold", "3");
        config.addDataSourceProperty("preparedStatementCacheQueries", "256");
        config.addDataSourceProperty("preparedStatementCacheSizeMiB", "10");
        config.addDataSourceProperty("tcpKeepAlive", "true");

        // 6. Metrics integration with Micrometer
        config.setMetricRegistry(meterRegistry);
        config.setPoolName("HikariPool-CoreBanking");

        return new HikariDataSource(config);
    }
}
```

---

## Pattern 2: Shortening Transaction Scope & Removing External Calls

```java
package com.learning.production.lab05;

import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;

@Service
public class OrderFulfillmentService {

    private final OrderRepository orderRepository;
    private final FraudDetectionClient fraudClient;
    private final TransactionTemplate transactionTemplate;

    public OrderFulfillmentService(
            OrderRepository orderRepository,
            FraudDetectionClient fraudClient,
            TransactionTemplate transactionTemplate) {
        this.orderRepository = orderRepository;
        this.fraudClient = fraudClient;
        this.transactionTemplate = transactionTemplate;
    }

    /**
     * Correct pattern: External HTTP call is executed OUTSIDE of the DB transaction.
     * The DB connection is held only for microseconds during the actual SQL write.
     */
    public OrderResult processOrder(OrderRequest request) {
        // Step 1: External network call (300ms - 2000ms) - NO DB CONNECTION ACQUIRED
        FraudScore fraudScore = fraudClient.evaluate(request.userId(), request.amount());
        if (fraudScore.isFraudulent()) {
            return OrderResult.rejected("Fraud check failed");
        }

        // Step 2: Minimal DB transaction scope (holds connection for < 5ms)
        return transactionTemplate.execute(status -> {
            Order order = new Order(request);
            order.setFraudScore(fraudScore.value());
            orderRepository.save(order);
            return OrderResult.success(order.getId());
        });
    }
}
```

---

## Pattern 3: Solving Hibernate N+1 with EntityGraphs & Batch Size

```java
package com.learning.production.lab05;

import jakarta.persistence.*;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface CustomerOrderRepository extends JpaRepository<Customer, Long> {

    // ANTI-PATTERN: findAll() generates 1 query for customers + N queries for orders
    // List<Customer> findAll(); 

    // PRODUCTION SOLUTION 1: EntityGraph forces single SQL LEFT OUTER JOIN
    @EntityGraph(attributePaths = {"orders", "orders.items"})
    @Query("SELECT c FROM Customer c WHERE c.active = true")
    List<Customer> findActiveCustomersWithOrders();

    // PRODUCTION SOLUTION 2: Hibernate Batch Fetching
    // In application.yml:
    // spring.jpa.properties.hibernate.default_batch_fetch_size: 50
    // Changes N queries into: WHERE customer_id IN (?, ?, ..., ?) -> 1 + N/50 queries
}
```
