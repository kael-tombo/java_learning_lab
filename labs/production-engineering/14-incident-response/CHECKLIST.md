# CHECKLIST: Incident Response, SRE War Rooms & Post-Mortem Readiness
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Incident Mobilization & ICS Command Structure

- [ ] **Incident Declaration & Severity Classification**:
  - [ ] P0/P1 declared immediately upon breaching customer SLOs or encountering active data loss.
  - [ ] Dedicated incident Slack channel (`#inc-<id>-<description>`) and Zoom/Meet war room opened automatically.
- [ ] **Core ICS Role Assignment (Within First 3 Minutes)**:
  - [ ] **Incident Commander (IC)** explicitly named; possesses sole operational authority over the war room.
  - [ ] IC strictly obeys the Cardinal Rule: **Zero coding, zero debugging, zero terminal execution**.
  - [ ] **Technical Operations Lead** appointed to direct subject matter experts (DB, K8s, JVM).
  - [ ] **Communications Lead** appointed to handle stakeholder updates and public status pages.
  - [ ] **Scribe** appointed to maintain real-time chronological action log.

---

## 2. Pacing, Hypothesis Testing & Diagnostic Hygiene

- [ ] **Mitigation Priority Rule**:
  - [ ] Responders prioritize **immediate mitigation** (stopping customer impact) over root-cause investigation.
  - [ ] The 5-Minute Rollback Rule enforced: if an outage began within 30 minutes of a release, rollback is executed immediately.
- [ ] **Single-Variable Mutation Protocol**:
  - [ ] Multiple simultaneous uncoordinated production changes strictly forbidden.
  - [ ] Every proposed mitigation stated as a discrete hypothesis, approved by the IC, and executed by a single assigned owner.
  - [ ] Metrics observed for 3 to 5 minutes after each change before testing subsequent hypotheses.
- [ ] **Forensic Snapshot Preservation**:
  - [ ] Automated forensic script executed before restarting or draining degraded pods:
    - Thread dump (`jcmd Thread.print`)
    - Class histogram (`jcmd GC.class_histogram`)
    - Linux cgroup stats (`cpu.stat`, `memory.stat`)
    - Socket states (`ss -s`)

---

## 3. Emergency Load Shedding & Traffic Draining

- [ ] **Feature Kill-Switches**:
  - [ ] Emergency circuit breakers available via `/actuator/emergency-circuit` or feature flag toggle.
  - [ ] Non-critical read queries (recommendations, analytics, badges) sheddable within 10 seconds to preserve core database capacity.
- [ ] **Adaptive Concurrency Protection**:
  - [ ] Edge ingress and microservice entrypoints enforce adaptive concurrency limits (Vegas/AIMD) to reject excess load with HTTP 429 during database degradation.
- [ ] **Regional Evacuation Readiness**:
  - [ ] Global DNS (Route 53 ARC / Cloudflare) configured with $\le 30\text{s}$ TTL to enable complete regional traffic evacuation in $< 4\text{ minutes}$.

---

## 4. Communications Shield & Stakeholder Hygiene

- [ ] **Technical Responder Isolation**:
  - [ ] Technical war room kept quiet; executives, product managers, and customer success redirected to Comms Lead.
- [ ] **Cadence of Executive Briefings**:
  - [ ] Standardized incident status updates posted to `#incident-exec-updates` every 15 to 20 minutes.
  - [ ] Public customer status page (Statuspage.io) updated with clear, factual, non-technical impact statements.

---

## 5. Blameless Post-Mortem & Action Item Governance

- [ ] **Dekker's Just Culture Adherence**:
  - [ ] Post-mortem review conducted within 5 business days of incident resolution.
  - [ ] Language audited: "human error" is strictly forbidden as a root cause; treated as a symptom of inadequate system design.
  - [ ] "Five Whys" analysis conducted to uncover latent organizational and architectural vulnerabilities.
- [ ] **Action Item Hierarchy of Controls**:
  - [ ] At least $70\%$ of action items categorized as **Level 1 (Elimination)** or **Level 2 (Engineering Controls)**.
  - [ ] P0 action items (preventing direct recurrence) assigned clear engineer owners with a strict **14-day deployment SLA**.
  - [ ] Engineering team commits at least $20\%$ of immediate next sprint capacity to post-mortem remediation tickets.
