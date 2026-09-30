# ARCHITECTURE DECISIONS: Chaos Engineering & Fault Injection Policy
## Lab 18 | Production Engineering Academy

---

## ADR-01: Enterprise Chaos Engineering Standards & Blast Radius Controls

### Status: ACCEPTED

### Context
Outages caused by cascading microservice failures revealed that untested failure scenarios repeatedly caused major incidents during peak customer traffic.

### Decisions
1. **Mandatory Monthly Chaos Game Days**:
   - Every tier-1 service team must conduct a monthly Game Day simulating one major failure scenario (AZ partition, database primary crash, third-party timeout).
2. **Blast Radius Constraints**:
   - Production experiments must be scoped to Canary pods or max 5% of traffic.
   - Experiments must run during high-staffing business hours (10:00 AM – 2:00 PM local time), never on Friday or weekends.
3. **Automated Stop-Loss Guard**:
   - Experiments must have a self-terminating hard timeout ($\le 10\text{ minutes}$).
   - Automated Prometheus monitor must terminate experiment if error budget burn rate exceeds $2\times$.

### Consequences
- Eliminates surprise outages during peak events.
- Forces all new services to prove circuit breaker resilience prior to production launch.
