# RUNBOOK: API Abuse, Rate Limiting & Contract Incidents
## Lab 10 | Production Engineering Academy

---

## RUNBOOK 01: Mitigating API Scraping / Denial of Service Attack

**Severity**: P1 / P2  
**Symptom**: Database query latency spiking; API gateway traffic surge from specific IP ranges or API keys.

### Step 1: Identify Abusive Client / Token
Inspect Envoy / Kong / Nginx access logs:
```bash
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -n 20
```
Or check API key consumption:
```bash
grep -o 'apiKey=[^& ]*' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -n 10
```

### Step 2: Emergency Gateway Throttling / Block
- **Block by IP Range (Cloudflare / WAF)**:
  Apply IP drop rule to block offending subnet.
- **Throttle by API Key via Redis**:
  Manually set Redis token bucket quota to 0:
  ```bash
  redis-cli HMSET "ratelimit:malicious_client_id" tokens 0 last_updated 9999999999999
  ```
- **Cap Deep Offset Pagination**:
  Enable WAF rule to block requests with query param `page > 100` or `offset > 2000`.

---

## RUNBOOK 02: Rollback of Incompatible API Contract Change
If a mobile app or partner breaks due to a deleted JSON field or modified type:
1. Re-deploy previous API gateway routing or enable legacy response compatibility filter:
   ```yaml
   spring.jackson.deserialization.fail-on-unknown-properties: false
   ```
2. Enable dual-field serialization: emit BOTH the legacy field name and the new field name in JSON payloads until mobile apps have upgraded.
