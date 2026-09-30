# ARCHITECTURE DECISIONS: Kubernetes Java Deployment Standards
## Lab 07 | Production Engineering Academy

---

## ADR-01: Container Resource Sizing and CPU Throttling Policy

### Status: ACCEPTED

### Context
Java services on Kubernetes experienced erratic tail latency spikes during burst traffic. Investigation revealed heavy CFS CPU throttling occurring on services configured with rigid CPU limits.

### Decision
1. **CPU Policy for Latency-Critical Java Services**:
   - Set **CPU Requests** equal to estimated sustained load.
   - Either **omit CPU Limits** or set CPU Limits to $3\times - 4\times$ CPU Requests.
   - Reason: The Linux CFS scheduler throttles containers when CPU limits are reached, even when host node CPU is 80% idle! Removing or relaxing CPU limits prevents artificial latency degradation while CPU requests guarantee node placement capacity.
2. **Memory Policy**:
   - Set **Memory Limits EQUAL to Memory Requests** (Guaranteed QoS Class in Kubernetes).
   - JVM configured with `-XX:MaxRAMPercentage=70.0`.
   - Leaves 30% container headroom for thread stacks, Metaspace, and native OS page cache.
3. **Graceful Termination Policy**:
   - Mandatory `preStop` hook with `sleep 15`.
   - `terminationGracePeriodSeconds` set to minimum 60s.

### Consequences
- Eliminates 502 Bad Gateway errors during rolling updates.
- Eliminates latency spikes caused by kernel CFS throttling.
