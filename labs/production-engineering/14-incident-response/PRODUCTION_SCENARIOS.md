# PRODUCTION SCENARIOS: Incident Response & Post-Mortem War Stories
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The $2,400,000 Uncoordinated War Room Chaos Outage

### 1. Incident Context & Architecture
- **Event**: Cyber Monday high-velocity checkout window.
- **Service**: `checkout-orchestration-service` (Spring Boot 3.x, PostgreSQL, Redis, Kafka).
- **Incident Severity**: P0 / SEV-0 ($80,000/minute revenue at risk).

### 2. The Disaster & Swarming Chaos
At 18:02 UTC, checkout success rate plummeted from $99.8\%$ to $14\%$:
- An emergency Zoom bridge was created without declaring an Incident Commander.
- Within 10 minutes, **over 45 engineers, directors, and executives joined the bridge**, speaking over one another.
- Responders began making uncoordinated changes simultaneously:
  - Engineer Alice suspected a Redis cache stall and restarted the Redis primary cluster.
  - Engineer Bob suspected a network partition and started restarting Kubernetes ingress pods.
  - Engineer Charlie deployed a manual hotfix adjusting JVM heap from 4GB to 8GB.
- **The Compounded Collapse**:
  - Alice's Redis restart dumped 25,000 cache-miss queries per second directly onto PostgreSQL.
  - PostgreSQL was overwhelmed by the unexpected cache-stampede queries.
  - Bob's Ingress restart dropped all active TCP sessions, triggering client auto-retries that multiplied traffic volume by $3\times$.
  - Total outage duration dragged out to **1 hour and 48 minutes**, costing the company over **$2,400,000 in unrecoverable sales**!

### 3. Forensic Autopsy & The ICS Turning Point
Post-incident review revealed that the original failure was merely a **minor database connection pool saturation** caused by a slow fraud-detection query:
- A simple 3-minute rollback of the fraud service would have mitigated the entire incident at T+05 minutes!
- Instead, 103 minutes of outage were created purely by **uncoordinated responder swarming and conflicting emergency mutations**.

### 4. Systemic Remediation
1. Formal adoption of the **Incident Command System (ICS)**:
   - Absolute command authority granted to the Incident Commander.
   - Responders strictly prohibited from executing commands without explicit verbal authorization.
2. Implemented automated forensic snapshot tooling and dedicated private responder channels.
3. *Outcome*: During the subsequent year's peak event, MTTR dropped from 108 minutes down to **8.4 minutes**.

---

## Scenario 2: The Database Connection Starvation & Emergency Load Shedding Save

### 1. Incident Context
- **Service**: `catalog-browsing-service` (Java 21, Spring Boot, MySQL).
- **Workload**: 60,000 HTTP requests/sec during a viral product launch.

### 2. The Collapse
At 12:15 UTC, MySQL primary CPU reached $100\%$:
- Query latency skyrocketed from 8ms to 4,200ms.
- All 150 pods in the microservice fleet exhausted their HikariCP connection pools (`activeConnections = 30`, `idleConnections = 0`, `threadsAwaitingConnection = 480`).
- Thread pools locked up; Ingress controllers began dropping requests with `504 Gateway Timeout`.

### 3. War Room Action & Mitigation via Kill-Switch
- **T+00:03**: Staff SRE Sarah Chen assumed Incident Command.
- **T+00:05**: Technical Lead diagnosed that MySQL was stalled executing complex nested queries for **personalized recommendations** and **real-time viewer badges**.
- **T+00:07**: Rather than restarting the database or pods (which would worsen the thundering herd), the IC authorized executing the **Emergency Load Shedding Kill-Switch**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"circuitName": "RECOMMENDATIONS", "shedded": true}' \
    http://catalog-service/actuator/emergency-circuit
  ```
- **T+00:08**: The application immediately stopped querying MySQL for recommendations, returning empty fallback recommendation lists (HTTP 200) directly from memory in $0.1\text{ms}$.
- **T+00:10**: MySQL query volume collapsed by **65%**. Active connections in HikariCP dropped from 30 down to 8.
- **T+00:12**: Core catalog browsing response times returned to **12ms** baseline. Core revenue transactions remained completely operational.

---

## Scenario 3: The Missing Index Sequential Scan Meltdown (The 5-Whys Post-Mortem)

### 1. Incident Summary
- **Incident ID**: INC-48201
- **Duration**: 24 minutes
- **Impact**: 45,000 checkout attempts failed with HTTP 500.

### 2. The Five-Whys Investigation Record

1. **Why did the checkout service throw HTTP 500 errors?**
   $\rightarrow$ HikariCP threw `ConnectionTimeoutException: Connection is not available, request timed out after 30000ms`.
2. **Why were database connections unavailable for 30 seconds?**
   $\rightarrow$ All 50 connections in the pool were held by worker threads executing `SELECT * FROM orders WHERE customer_id = ?`.
3. **Why did this query take 18 seconds to execute instead of 5ms?**
   $\rightarrow$ The database executed a full sequential table scan across 48 million rows because the index on `customer_id` was missing.
4. **Why was the index missing in production when it was present in staging?**
   $\rightarrow$ The DBA running the production migration aborted the `CREATE INDEX` command when it timed out due to an exclusive lock conflict with an ETL batch job, intending to run it manually later.
5. **Why was a critical database migration executed manually without automated validation?**
   $\rightarrow$ Database migrations lacked an automated CI/CD deployment pipeline with lock timeout pre-checks and post-migration index verification gates.

### 3. Action Items Hierarchy of Controls
- **Level 1 (Elimination)**: Deprecate manual SSH DBA database migrations entirely.
- **Level 2 (Engineering Control - P0, 14-Day SLA)**: Implement automated Liquibase/Flyway CI/CD pipeline with pre-deployment lock conflict detection and automated index presence verification before traffic shifting.
- **Level 3 (Engineering Control - P1, 30-Day SLA)**: Configure pg_stat_statements anomaly alerts flagging any query with `calls > 100` and `mean_exec_time > 500ms`.

---

## Scenario 4: The DNS Failover Black Hole (Stale JVM DNS Cache Outage)

### 1. Incident Context & Disaster Recovery
- **Architecture**: Multi-Region Active-Passive deployment across AWS `us-east-1` (Primary) and `us-west-2` (Standby).
- **Incident**: AWS `us-east-1` experienced a major availability zone power loss and network degradation.

### 2. The Failed Failover
The SRE team initiated automated Disaster Recovery:
- Route 53 Application Recovery Controller flipped DNS records to point all traffic to `us-west-2`.
- Public DNS propagation completed within 60 seconds (Route 53 TTL was 30s).
- External curl requests from outside verified traffic was hitting `us-west-2` successfully.
- **The Catastrophe**: Internal Java microservices calling each other were **still failing at a 100% rate**! Microservices in `us-west-2` were still firing internal gRPC requests across the WAN back into the dead `us-east-1` region!

### 3. Root Cause: JVM Infinite DNS Caching
Forensic analysis of the Java startup flags revealed:
```bash
# Default JVM behavior in older configs:
# networkaddress.cache.ttl was unset!
```
Because the application had been started with a SecurityManager in its legacy base image, the HotSpot JVM's default DNS cache TTL was set to **`-1` (Cache Forever)**!
- The JVM resolved internal service endpoints once at pod boot time.
- When Route 53 flipped the DNS IP addresses to the backup region, **the JVM completely ignored the new DNS records**.
- All internal microservices continued hammering the unreachable IP addresses in `us-east-1` until every pod in the fleet was forcefully restarted.

### 4. Production Remediation
1. Enforced JVM DNS TTL standards across all base container images:
   ```bash
   -Dnetworkaddress.cache.ttl=5
   -Dnetworkaddress.cache.negative.ttl=2
   ```
2. Implemented automated Chaos Engineering tests simulating region failover to continuously verify that internal gRPC channels pick up DNS shifts within 10 seconds.
