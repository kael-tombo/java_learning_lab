# THEORY: Incident Response, SRE War Rooms & Post-Mortem Engineering
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Incident Command System (ICS) for Technology Outages

When a critical Tier-0 outage strikes, standard engineering hierarchy (VP $\rightarrow$ Director $\rightarrow$ Manager $\rightarrow$ Tech Lead) completely collapses. In emergency operations, standard decision-making latency is catastrophic. Modern Site Reliability Engineering adapts the **Incident Command System (ICS)** (originally codified by FEMA and firefighting services) for technology operations.

```
                           ┌──────────────────────────────────────────────┐
                           │            Incident Commander (IC)           │
                           │  • Holds absolute operational authority     │
                           │  • DOES NOT CODE OR DEBUG!                   │
                           │  • Directs timeline, mitigations, delegations│
                           └──────────────────────┬───────────────────────┘
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     Technical Operations Lead   │      │       Communications Lead       │      │         Incident Scribe         │
├─────────────────────────────────┤      ├─────────────────────────────────┤      ├─────────────────────────────────┤
│ • Leads Subject Matter Experts  │      │ • Shields responders from execs │      │ • Records real-time timeline    │
│ • Validates hypotheses          │      │ • Posts internal Slack updates  │      │ • Logs commands, flags, diffs   │
│ • Directs technical mitigations │      │ • Manages customer Statuspage   │      │ • Records metric changes & plots│
└────────────────┬────────────────┘      └─────────────────────────────────┘      └─────────────────────────────────┘
                 │
         ┌───────┴───────┬───────────────┐
         ▼               ▼               ▼
┌────────────────┐ ┌───────────┐ ┌───────────────┐
│ DB SME (Pg/Ora)│ │ Network/K8s│ │ JVM/App Lead  │
└────────────────┘ └───────────┘ └───────────────┘
```

### 1.1 The Cardinal Rule of the Incident Commander
**The Incident Commander (IC) NEVER touches a keyboard to debug or write code!**
The moment an IC begins inspecting logs, typing commands, or analyzing a thread dump:
- They develop **tunnel vision** on a single hypothesis.
- They lose high-level situational awareness.
- Uncoordinated side-actions from other engineers go unnoticed.
- Responders begin acting in silos without approval.

The IC's sole job is **orchestration**: approving or rejecting proposed hypotheses, maintaining the time budget, deciding on rollbacks or regional traffic evacuation, and ensuring responders remain calm and methodical.

### 1.2 Clear Role Separation

| Role | Primary Responsibility | Anti-Behavior to Avoid |
|:---|:---|:---|
| **Incident Commander (IC)** | Command authority, mitigation approvals, timeline pacing | Diving into terminal, speculating on code bugs |
| **Technical Lead** | Coordinates SMEs, forms and disproves diagnostic hypotheses | Making unapproved production changes unilaterally |
| **Comms Lead** | Internal updates (every 15–20m), external public status page updates | Asking technical responders for status every 2 minutes |
| **Scribe** | Accurate chronological logging of actions, timestamps, and metric shifts | Forgetting to record commands or hypotheses that failed |
| **Responders (SMEs)** | Deep-dive forensics on specific domains (DB, K8s, JVM) | Acting without explicit IC approval |

---

## 2. Forensic Latency Vector: MTTD, MTTA, MTTR & MTBF

```
Timeline of an Incident:
───────────────────────────────────────────────────────────────────────────────────────────► Time
│               │                  │                                            │
▲               ▲                  ▲                                            ▲
Outage Begins   Alert Fires        Engineer Acknowledges /                      Service Mitigated
(Latent Defect) (SLO Breach)       War Room Assembled                           (Health Restored)
│◄─── MTTD ────►│◄───── MTTA ─────►│◄────────────────── MTTR ──────────────────►│
```

### 2.1 The Critical Distinction Between Resolution and Mitigation
- **Mitigation ($\text{MTTR}$)**: Restoring service availability and customer SLOs (e.g. rolling back a release, draining traffic away from an affected AZ, flipping a feature flag, shedding non-critical load).
- **Resolution**: Finding the permanent software defect, writing a unit test, issuing a code patch, reviewing, and deploying the fix days later.
$$\text{Production Rule: Always MITIGATE first, INVESTIGATE root cause later!}$$

### 2.2 Forensic Operational Metrics

$$\text{MTTD (Mean Time to Detect)} = T_{\text{alert}} - T_{\text{incident\_start}}$$
- Driven by monitoring resolution, anomaly detection, and synthetic canary probes.
- **Target**: $< 3\text{ minutes}$ for Tier-0 services.

$$\text{MTTA (Mean Time to Acknowledge)} = T_{\text{response}} - T_{\text{alert}}$$
- Driven by PagerDuty / Opsgenie escalation policies, secondary on-call schedules, and on-call handoff hygiene.
- **Target**: $< 5\text{ minutes}$.

$$\text{MTTR (Mean Time to Mitigate / Restore)} = T_{\text{service\_restored}} - T_{\text{response}}$$
- Driven by automated rollbacks, clear runbooks, chaos-tested failovers, and feature kill-switches.
- **Target**: $< 15\text{ minutes}$ for critical user journeys.

---

## 3. Degradation Strategy: Graceful Degradation & Load Shedding

When capacity collapses or downstream dependencies fail, services must degrade predictably rather than crashing completely:

```
                                  Incoming Request Volume
                                            │
                                            ▼
                             ┌──────────────────────────────┐
                             │       Request Priority       │
                             └──────────────┬───────────────┘
                                            │
         ┌──────────────────────────────────┼──────────────────────────────────┐
         ▼                                  ▼                                  ▼
┌─────────────────┐                ┌─────────────────┐                ┌─────────────────┐
│ Tier 0: Core Tx │                │ Tier 1: User UX │                │ Tier 2: Non-Crit│
│ (Money Movement)│                │ (Catalog/Search)│                │ (Recs, Badges)  │
├─────────────────┤                ├─────────────────┤                ├─────────────────┤
│ Process ALWAYS  │                │ Degrade to L1   │                │ SHED LOAD:      │
│ (Protected)     │                │ Stale Cache     │                │ Return Empty    │
│                 │                │                 │                │ Response 200    │
└─────────────────┘                └─────────────────┘                └─────────────────┘
```

### 3.1 Load Shedding via CoDel & Adaptive Concurrency Limits
Traditional fixed thread pools and request queues fail under overload because requests spend seconds waiting in queues before being processed, consuming resources only to deliver timeouts.
- **Netflix Concurrency Limits (Vegas / AIMD Algorithm)**: Dynamically adjusts maximum concurrent requests based on measured round-trip latency. If latency climbs, concurrency limit shrinks, rejecting excess requests with `429 Too Many Requests` at the boundary before they overload worker threads.
- **Emergency Feature Kill-Switches**: Spring Boot Actuator endpoints or dynamic feature flags (LaunchDarkly) designed to disable expensive database queries (e.g., personalized recommendations, real-time inventory counts) with a single atomic toggle.

---

## 4. The Philosophy of Blameless Post-Mortems (Just Culture)

Human error is the **symptom** of deeper architectural and systemic vulnerabilities, never the root cause.

```
Punitive / Blame Culture:
  "Engineer X ran a DELETE without a WHERE clause."
  └──► Punishment: Reprimand Engineer X.
  └──► Result: Engineers hide mistakes; fear-driven culture; incident recurrences inevitable!

Blameless / Just Culture (Sidney Dekker):
  "Why was a junior engineer able to execute an unrestricted destructive SQL query directly
   against production without peer approval, automated linters, or a read-only proxy?"
  └──► Remediation: Implement dual-custody database proxies, ephemeral credentials, and query linters.
  └──► Result: System becomes resilient to human error.
```

### 4.1 The "Five Whys" Root Cause Drill-Down
A formal methodology to peel back surface-level proximate actions to identify foundational system design flaws:
1. **Why did the checkout service fail?** $\rightarrow$ It ran out of database connections.
2. **Why did it run out of connections?** $\rightarrow$ Queries to the `orders` table were taking 14 seconds instead of 10ms.
3. **Why were queries taking 14 seconds?** $\rightarrow$ A missing index on `customer_id` caused full sequential table scans across 50 million rows.
4. **Why was the index missing in production?** $\rightarrow$ The migration script was executed manually and failed midway due to a lock acquisition timeout.
5. **Why was the script executed manually without failure alerts?** $\rightarrow$ Database migrations lacked automated CI/CD gating and automated rollback checks.
**Root Cause**: Lack of automated migration pipelines with dry-run locks and rollback verification — NOT "engineer forgot to verify the index."

---

## 5. Post-Mortem Action Item Hierarchy of Controls

Post-mortem remediation items must not be vague platitudes ("remind team to be careful"). They must follow the **Engineering Hierarchy of Controls**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. ELIMINATION (Most Effective): Remove the hazard entirely            │
│    Example: Deprecate and delete the legacy unindexed table.           │
├────────────────────────────────────────────────────────────────────────┤
│ 2. SUBSTITUTION: Replace hazard with safer alternative                 │
│    Example: Replace direct SQL migrations with automated Flyway/Liquibase│
├────────────────────────────────────────────────────────────────────────┤
│ 3. ENGINEERING CONTROLS: Isolate people from hazard                    │
│    Example: Database proxy rejects any query lacking WHERE on index.   │
├────────────────────────────────────────────────────────────────────────┤
│ 4. ADMINISTRATIVE CONTROLS: Change the way people work                 │
│    Example: Mandatory runbook checklist for manual releases.           │
├────────────────────────────────────────────────────────────────────────┤
│ 5. WARNINGS / TRAINING (Least Effective): Rely on human vigilance     │
│    Example: "Retrain engineers on writing good SQL queries."           │
└────────────────────────────────────────────────────────────────────────┘
```
**FinOps & SRE Standard**: At least $70\%$ of post-mortem action items must fall into **Level 1, 2, or 3** (Automated Engineering Controls).
