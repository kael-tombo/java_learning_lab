# ARCHITECTURE DECISIONS: Enterprise Incident Response & On-Call Standards
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Mandatory Incident Command System (ICS) for Tier-0 Outages

### Status: ACCEPTED

### Context
Major production incidents suffered from uncoordinated swarming, conflicting interventions, and chaotic communication bridges. Engineers and executives spoke over each other, diagnostic signals were ruined by simultaneous unrecorded mutations, and MTTR averaged $> 75\text{ minutes}$.

### Decision
1. **Mandatory ICS Activation**:
   - Any Tier-0 or Tier-1 outage automatically initiates the **Incident Command System (ICS)**.
   - The first on-call engineer declares themselves temporary **Incident Commander (IC)** until explicitly relieved by a designated Staff SRE / Engineering Manager.
2. **Absolute Command Authority**:
   - The IC holds sole operational authority over the incident. No changes may be applied to production without explicit IC verbal or Slack approval.
3. **The Cardinal Rule**:
   - The IC is strictly prohibited from touching terminals, writing code, or performing diagnostics. Their role is situational awareness, hypothesis gating, and pacing.
4. **Dedicated Communications Shield**:
   - A Communications Lead is immediately appointed to manage internal stakeholder briefings and external customer status page communications.

### Consequences
- Uncoordinated simultaneous production changes eliminated.
- Responders protected from executive interruptions.
- MTTR reduced from 75 minutes to $< 18\text{ minutes}$ across Tier-0 services.

---

## ADR-02: Automated Canary Analysis & Immediate Rollback Standard

### Status: ACCEPTED

### Context
Over $70\%$ of production outages were introduced by recent deployments. In multiple cases, engineers spent 45 minutes attempting to "forward-fix" a bug in production rather than executing an immediate rollback.

### Decision
1. **Automated Canary Analysis (ACA)**:
   - All deployments must proceed through a canary phase (e.g. via Argo Rollouts or Flagger) exposing $5\%$ of traffic for 15 minutes.
   - Automated analysis monitors HTTP 5xx error rate and P99 latency. If metrics degrade by $> 15\%$ relative to baseline, the canary automatically aborts and rolls back with zero human intervention.
2. **The 5-Minute Rollback Rule**:
   - If an outage begins within 30 minutes of a deployment, the default mandatory action is **immediate rollback** to the previous known good revision.
   - Attempting to "debug in production" or forward-fix is strictly forbidden during active customer degradation.

### Consequences
- Deployment-related outage durations cut from 45 minutes to $< 4\text{ minutes}$.
- Eliminates risky, unvetted hotfixes created under emergency stress.

---

## ADR-03: Blameless Post-Mortem Policy & Action Item Enforcement SLA

### Status: ACCEPTED

### Context
Post-mortems often devolved into subtle finger-pointing, leading engineers to hesitate to take on-call ownership or report near-miss incidents. Action items documented in post-mortem reviews languished in Jira backlogs, causing identical failure modes to repeat months later.

### Decision
1. **Dekker Just Culture Standard**:
   - Post-mortems are strictly blameless. The term "human error" is forbidden as a root cause; it must be treated as a starting point to investigate tooling, telemetry, and architectural guardrails.
2. **Post-Mortem Review Timeline**:
   - Every P1/P2 incident requires an initial timeline within 24 hours and a completed post-mortem within 5 business days.
3. **Remediation SLA & Engineering Hierarchy of Controls**:
   - At least $70\%$ of action items must be **Engineering Controls** (linters, automation, circuit breakers, schema validations) rather than administrative warnings.
   - P0 action items (preventing direct recurrence) must be deployed within **14 calendar days**.
   - P1 action items (detection and monitoring) must be deployed within **30 calendar days**.
   - The responsible team must allocate $20\%$ of the immediate next sprint capacity to completing post-mortem items.

### Consequences
- Encourages rapid, transparent incident declaration without fear of punishment.
- Ensures systemic architectural defects are permanently remediated.

---

## ADR-04: Emergency Load Shedding & Feature Kill-Switch Architecture

### Status: ACCEPTED

### Context
During upstream provider degradation or database capacity saturation, entire monolithic microservice clusters crashed due to cascading thread pool exhaustion. Applications continued attempting to process low-priority background jobs while critical user checkouts were dropped.

### Decision
1. **Standardized Emergency Circuit Endpoint**:
   - All critical Java services must implement an emergency kill-switch endpoint (via Spring Boot Actuator or dynamic feature flags):
     ```text
     POST /actuator/emergency-circuit?circuit=RECOMMENDATIONS&state=DISABLED
     ```
2. **Graceful Three-Tier Degradation Hierarchy**:
   - **Tier 0 (Protected)**: Core payment, auth, and transaction processing (always executed).
   - **Tier 1 (Degraded)**: Search and product catalog (served from stale L1 caches during overload).
   - **Tier 2 (Sheddable)**: Recommendations, analytics, badge notifications, loyalty point calculations (instantly disabled during high-load incidents to preserve database capacity).

### Consequences
- Services maintain core business availability during severe dependency failures.
- Provides immediate non-invasive mitigation option during active war rooms.

---

## ADR-05: Automated Incident Forensic Bundle Generation

### Status: ACCEPTED

### Context
When services degraded, engineers frequently restarted pods to restore availability before capturing diagnostic state. When the post-mortem was held 2 days later, zero thread dumps, heap histograms, or cgroup stats were available, making root cause determination impossible.

### Decision
1. **Automated Forensic Capture Prior to Drain**:
   - Node termination hooks and on-call runbook scripts must execute an automated forensic snapshot script capturing:
     - JVM thread dump (`jcmd Thread.print`)
     - Class histogram (`jcmd GC.class_histogram`)
     - Linux cgroup stats (`/sys/fs/cgroup/cpu.stat`, `memory.stat`)
     - OS socket summaries (`ss -s`)
   - The entire bundle is compressed and uploaded to an S3/GCS forensic bucket within 45 seconds before the pod is restarted or drained.

### Consequences
- Guarantees forensic telemetry is preserved without delaying incident mitigation.
- Provides complete forensic artifacts for offline blameless post-mortem investigations.
