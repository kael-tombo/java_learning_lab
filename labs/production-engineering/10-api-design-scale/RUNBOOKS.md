# RUNBOOK: Production API Incidents, Rate Limiting & Contract Triage
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## RUNBOOK 01: Mitigating API Scraping & Deep Pagination DoS

**Severity**: P1 / High  
**Trigger**: Alert `DatabaseReadIOPSHigh` or `APIGatewayLatencyP99 > 2000ms`.

### Phase 1: Rapid Telemetry Assessment (< 3 minutes)
1. **Identify High-Volume Query Patterns in Gateway Logs**:
   ```bash
   # Extract top 20 client IPs generating traffic
   awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -n 20

   # Check for scraping patterns using deep pagination (e.g. page > 100 or offset > 5000)
   grep -E '(\?|&)(offset=[0-9]{4,}|page=[0-9]{3,})' /var/log/nginx/access.log | awk '{print $1, $7}' | head -n 20
   ```
2. **Inspect Slow Queries in PostgreSQL**:
   ```sql
   SELECT pid, now() - query_start AS duration, query 
   FROM pg_stat_activity 
   WHERE state = 'active' AND query ILIKE '%OFFSET%'
   ORDER BY duration DESC LIMIT 10;
   ```

---

### Phase 2: Immediate Containment Actions
1. **Edge WAF Block Rule (Cloudflare / AWS WAF)**:
   Deploy an instant WAF rule matching request URI queries to block deep offsets:
   ```
   Rule: (http.request.uri.query contains "offset=" and int(http.request.uri.query.offset) > 1000) -> Action: BLOCK (403)
   ```
2. **Targeted Redis Rate Limiter Lockout**:
   Zero out the token bucket for the offending client API key or IP:
   ```bash
   redis-cli HMSET "ratelimit:client:bad_actor_api_key" tokens 0 last_updated 9999999999999
   redis-cli EXPIRE "ratelimit:client:bad_actor_api_key" 86400
   ```
3. **Terminate Hanging Backend Queries in PostgreSQL**:
   ```sql
   SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE query ILIKE '%OFFSET%' AND state = 'active';
   ```

---

## RUNBOOK 02: Emergency Mitigation of Breaking API Contract Changes

**Severity**: P1  
**Trigger**: Sudden surge in mobile app crash rates (`JSONParseError`, `UnrecognizedPropertyException`) following a new backend microservice deployment.

### Phase 1: Verify the Breaking Schema Delta
Inspect git deployment diff or diff current OpenAPI spec against the previous release:
```bash
git diff HEAD~1 -- src/main/resources/openapi.yaml
```
Look for:
- Renamed JSON fields (e.g. `user_id` $\to$ `userId`).
- Modified data types (e.g. `int` $\to$ `string` or `enum` changes).
- Newly added required fields with no defaults.

---

### Phase 2: Gateway Response Transformation Hotfix
Before triggering a full backend rollback, mitigate mobile crashes at the API Gateway layer:
1. **Envoy Lua Response Filter / Spring Cloud Gateway Filter**:
   Inject an inline response transformer to alias the new field back to the legacy field name:
   ```lua
   -- Envoy inline response body re-mapper
   function envoy_on_response(response_handle)
       local body = response_handle:body()
       if body then
           local json = cjson.decode(body)
           if json.userId and not json.user_id then
               json.user_id = json.userId -- Duplicate field for backward compatibility
               response_handle:body():setBytes(cjson.encode(json))
           end
       end
   end
   ```
2. **If Transformation Is Not Possible: Trigger Instant Canary Rollback**:
   ```bash
   kubectl rollout undo deployment/order-service-api -n production
   ```

---

## RUNBOOK 03: Redis Rate Limiter Outage & Fail-Open Emergency Protocol

**Severity**: P1 / High  
**Trigger**: Alert `APIGateway500Spike` or `RedisConnectionPoolTimeout` on the rate-limiting filter.

### Phase 1: Diagnose Rate Limiter Dependency
If the centralized Redis cluster hosting token buckets becomes unreachable, poorly designed gateways block all legitimate user traffic with 500 or 503 errors.

Check Gateway logs:
```bash
grep -i "RedisCommandTimeoutException" /var/log/gateway/gateway.log | head -n 10
```

### Phase 2: Force Fail-Open Mode
Execute dynamic actuator configuration update to bypass rate limiter checks:
```bash
# Push dynamic property to Spring Cloud Gateway / Consul:
curl -X POST http://gateway-internal:8081/actuator/env \
  -H 'Content-Type: application/json' \
  -d '{"name":"ratelimiter.fail-open","value":"true"}'

curl -X POST http://gateway-internal:8081/actuator/refresh
```
*Expected Behavior*: Incoming requests bypass Redis checks and route directly to backend services, restoring 100% user availability while SREs recover the Redis cluster.

---

## RUNBOOK 04: Resolving Idempotency Key Lock Starvation & 409 Storms

**Severity**: P2  
**Trigger**: Elevated rate of `HTTP 409 Conflict` errors on payment and checkout endpoints.

### Phase 1: Root Cause Diagnosis
When a backend service crashes or experiences a network freeze *while* processing a payment, the distributed lock `lock:idempotency:<key>` remains in the `IN_PROGRESS` state. Subsequent client retries receive `HTTP 409 Conflict` indefinitely until the lock TTL expires.

Inspect locked keys in Redis:
```bash
redis-cli KEYS "lock:idempotency:*"
# Inspect TTL of stuck lock
redis-cli TTL "lock:idempotency:9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
```

### Phase 2: Releasing Orphaned Locks
1. **Identify Associated Database Record**:
   Query the PostgreSQL database to determine if the transaction actually succeeded or failed:
   ```sql
   SELECT id, status, idempotency_key FROM charges WHERE idempotency_key = '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d';
   ```
2. **If DB Record is Missing (Transaction Never Committed)**:
   Safely release the orphaned lock so the client can retry:
   ```bash
   redis-cli UNLINK "lock:idempotency:9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
   ```
3. **If DB Record Exists as `SUCCESS`**:
   Manually backfill the completed response into Redis to allow client replay:
   ```bash
   redis-cli SET "idempotency:9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d" '{"statusCode":200,"payloadJson":"{\"status\":\"SUCCESS\"}"}' EX 86400
   redis-cli UNLINK "lock:idempotency:9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
   ```
