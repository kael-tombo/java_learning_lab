# CODE_DEEP_DIVE — Pool Exhaustion

## 1. Hikari Config That Diagnoses
```properties
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.connection-timeout=10000
spring.datasource.hikari.max-lifetime=1800000
spring.datasource.hikari.leak-detection-threshold=15000
management.metrics.enable.hikaricp=true
```

## 2. Metrics + Logs
```bash
curl -s localhost:8080/actuator/metrics/hikaricp.connections.active
curl -s localhost:8080/actuator/metrics/hikaricp.connections.pending
curl -s localhost:8080/actuator/metrics/hikaricp.connections.timeout.rate
grep -i "not available\|leak detection\|timed out" app.log | tail -30
# leak warning looks like:
# Connection leak detection triggered for connection... stack trace follows
#   at com.shop.OrderDao.findById(OrderDao.java:42)
```

## 3. jstack Proof (pool waiters)
```bash
jstack -l <pid> | grep -B3 -A12 "HikariPool.getConnection\|PoolBase.newConnection" | head -60
# many threads parked here + active≈max = pool saturation confirmed
jcmd <pid> Thread.print | grep -c "getConnection"
```

## 4. Postgres Side
```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
SELECT pid, now()-query_start AS age, state, left(query,160)
 FROM pg_stat_activity WHERE datname='shop' ORDER BY age DESC LIMIT 15;
-- blocker detail
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
-- kill (careful)
SELECT pg_cancel_backend(12345);    -- gentle
SELECT pg_terminate_backend(12345); -- hard
```

## 5. Leaky vs Fixed Java
```java
// LEAKY: close skipped on exception path
Connection c = ds.getConnection();
ResultSet rs = c.createStatement().executeQuery(sql);
if (rs.next()) return map(rs);  // early return leaks c+rs!
// FIXED
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql);
     ResultSet rs = ps.executeQuery()) {
  if (rs.next()) return map(rs); return null;
}
// NEVER hold across remote call
try (Connection c = ds.getConnection()) { Order o = load(c, id); }
callPaymentGateway(o);  // outside conn scope
```

## 6. JFR Connection Events
```bash
jcmd <pid> JFR.start name=pool,settings=profile,filename=/tmp/pool.jfr duration=180s
# correlate jdk.SocketRead (DB wait) with pool-wait stacks in Mission Control
```

## 7. Checklist
Pending>0 confirmed, leak stacks or slow query identified, try-with-resources fix, sizing within DB budget, soak verifies idle recovery.
