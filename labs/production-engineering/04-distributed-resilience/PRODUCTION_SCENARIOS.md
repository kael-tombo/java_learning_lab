# PRODUCTION SCENARIOS: Distributed Systems Failures & Cascading Collapse
## Lab 04 | Production Engineering Academy

---

## Scenario 1: The Cascading Timeout Storm (The Thundering Herd)

### Context
A fintech payments gateway processing 12,000 requests/second across 40 container pods. The architecture consists of an API Gateway -> Order Service -> Inventory Service -> Payment Service -> External Payment Gateway (Visa/Mastercard processor).

### Incident Timeline (All times UTC)
- **14:02:10**: The external payment processor experiences an internal database migration locking a subset of tables. Their response time jumps from 150ms to 4,800ms.
- **14:02:30**: Payment Service HTTP client connections take 4.8 seconds instead of 150ms. Since the payment service had a default connection pool size of 200 and an HTTP client read timeout of 10,000ms (10s), all 200 HTTP client connections quickly become saturated.
- **14:03:00**: Inbound Tomcat/Netty request worker threads in Payment Service block waiting for an available outbound connection from the pool. Within 30 seconds, all 500 Tomcat worker threads in each of the 40 Payment Service pods are completely exhausted in `WAITING` state.
- **14:03:20**: Order Service calls to Payment Service begin timing out. Order Service had a retry policy configured: **3 immediate retries on timeout**.
- **14:03:40**: The retry storm triples inbound traffic to Payment Service from 12k req/s to 36k req/s.
- **14:04:00**: Order Service thread pools exhaust. Kubernetes liveness probes to `/actuator/health` in Payment Service and Order Service time out (probe timeout was 1s, but Tomcat cannot dispatch the probe request).
- **14:04:30**: Kubernetes marks all 40 pods as Unhealthy and initiates simultaneous container restarts.
- **14:05:00**: New pods start up, attempt to warm up JIT caches and open database connections, and are immediately hit with the queued 36k req/s backlog. Startup CPU hits 100%, health checks fail again. Total fleet death spiral.

### Forensic Metrics & Root Cause
1. **Unbounded Timeout**: 10s read timeout allowed latency to inflate 30x before failing.
2. **Aggressive Retry Storm**: 3 immediate retries without exponential backoff and without jitter multiplied downstream load by 4x during an active degradation.
3. **No Circuit Breaker**: No mechanism to short-circuit fast when downstream failure rate crossed 50%.
4. **Co-mingled Health Check Thread Pool**: Liveness probes shared the same saturated HTTP thread pool as business traffic.

### Corrective Production Remediation
1. Implemented **Resilience4j Circuit Breaker** with 50% failure rate threshold and 5-second open state duration.
2. Configured **Exponential Backoff with Full Jitter** on idempotent GET/query calls, completely removed retries from non-idempotent POST payments.
3. Configured separate management server port on different thread pool (`management.server.port=8081`) so Kubernetes health probes are immune to business thread exhaustion.

---

## Scenario 2: The Distributed Split-Brain State in Dual-Region Failover

### Context
A multi-region active-active database and distributed lock cluster across `us-east-1` (Primary) and `us-west-2` (Secondary). A transit fiber cut between AWS regions caused a 4-minute network partition.

### The Failure Mode
- Both regions had 3 nodes of a 5-node distributed consensus cluster. Wait—5 nodes across 2 regions means 3 in Region A and 2 in Region B.
- Region B lost connectivity to Region A.
- A custom failover script in Region B concluded Region A was completely offline and force-promoted Region B's database to Read-Write without verifying quorum.
- For 4 minutes, both regions accepted writes independently, creating irreconcilable data divergency in account balances and order IDs.

### Key Lesson & Architectural Rule
Never attempt manual or heuristic failover across partitioned networks without verifiable mathematical quorum ($N/2 + 1$).
