# RUNBOOKS: Incident Response, SRE War Rooms & Post-Mortem Operations
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Declaring and Mobilizing a Tier-0 Incident War Room (ICS Protocol)

### 1. Severity Classification Matrix
- **P0 / SEV-0 (Catastrophic)**: Complete platform outage; money-movement or core authentication down fleet-wide. Revenue loss $> \$10,000/\text{minute}$.
- **P1 / SEV-1 (Critical)**: Core user journey impaired for $\ge 5\%$ of users; no workaround available.
- **P2 / SEV-2 (Major)**: Non-critical features degraded (recommendations, analytics); core transactions intact.

### 2. Immediate Mobilization Workflow (First 5 Minutes)

#### Step 1: Declare Incident & Open War Room
Execute in Slack:
```text
/incident declare "P0: Payment Checkout Service Latency Breach & 504 Gateway Timeouts"
```
This triggers automated workflows:
- Generates dedicated war-room channel: `#inc-84920-checkout-outage`.
- Opens dedicated Zoom/Google Meet bridge.
- Pages on-call Primary and Secondary SREs via PagerDuty.

#### Step 2: Establish the Four Core ICS Roles
Within the first 3 minutes of entering the war room, the first responder explicitly assigns roles:
```text
Incident Commander (IC): Sarah Chen (Staff SRE)
Technical Operations Lead: Marcus Vance (Backend Lead)
Communications Lead: Alex Rivera (Product Ops)
Incident Scribe: David Kim (SRE)
```
*Verification*: Post the role assignments in the channel topic.

#### Step 3: Enforce War-Room Rules of Engagement
The IC issues verbal declaration:
1. *"I am Incident Commander. All production changes must receive explicit verbal approval from me before execution."*
2. *"Technical Lead Marcus, assemble diagnostic signals. Do not apply mitigations without approval."*
3. *"Comms Lead Alex, set up the external status page and schedule an internal stakeholder briefing for T+15 minutes."*

---

## Runbook 02: Executing Emergency Load Shedding via Feature Kill-Switches

### 1. Context & Symptoms
- Downstream database connection pools saturated ($100\%$ pool utilization, threads in `TIMED_WAITING`).
- Application response times climbing past Ingress timeout thresholds ($> 5,000\text{ms}$).
- Goal: Shed non-critical database queries instantly to preserve capacity for core money-movement transactions.

### 2. Execution Runbook

#### Step 1: Inspect Available Emergency Circuits
```bash
# Query Spring Boot emergency circuit endpoint
curl -s http://payment-service.production.svc.cluster.local:8080/actuator/emergency-circuit | jq .
```
*Output*:
```json
{
  "RECOMMENDATIONS": false,
  "LOYALTY_POINTS": false,
  "REALTIME_ANALYTICS": false,
  "EXTERNAL_FRAUD_CHECK": false
}
```

#### Step 2: Shed Non-Critical Features
Trip the circuit breakers to shed non-essential database read volume:
```bash
# Disable personalized recommendations
curl -X POST -H "Content-Type: application/json" \
  -d '{"circuitName": "RECOMMENDATIONS", "shedded": true}' \
  http://payment-service.production.svc.cluster.local:8080/actuator/emergency-circuit

# Disable loyalty point calculations
curl -X POST -H "Content-Type: application/json" \
  -d '{"circuitName": "LOYALTY_POINTS", "shedded": true}' \
  http://payment-service.production.svc.cluster.local:8080/actuator/emergency-circuit
```

#### Step 3: Verify Capacity Recovery
Monitor HikariCP database pool metrics:
```bash
kubectl top pods -l app=payment-service
# Verify active connections drop below 70% threshold
```

---

## Runbook 03: The 5-Minute Emergency Canary Rollback Runbook

### 1. Context
If an outage begins within 30 minutes of a recent production deployment, **immediate rollback** is the default mandatory action. Forward-fixing during active customer degradation is strictly prohibited.

### 2. Execution Runbook

#### Step 1: Identify Last Known Good Revision
```bash
kubectl rollout history deployment/payment-orchestrator -n production
```
*Inspect Revisions*:
```text
REVISION  CHANGE-CAUSE
47        Release v3.1.8 (Stable baseline)
48        Release v3.2.0 (Target of suspected regression)
```

#### Step 2: Execute Immediate Rollback
```bash
kubectl rollout undo deployment/payment-orchestrator -n production --to-revision=47
```

#### Step 3: Monitor Rollout Progress
```bash
kubectl rollout status deployment/payment-orchestrator -n production --timeout=120s
```

#### Step 4: Verify Metric Recovery
Check Grafana / Prometheus for HTTP error rate collapse:
```promql
sum(rate(http_requests_total{status=~"5.*", app="payment-orchestrator"}[1m])) 
/ 
sum(rate(http_requests_total{app="payment-orchestrator"}[1m])) * 100
```
Verify error rate drops to $< 0.1\%$.

---

## Runbook 04: Rapid Forensic Snapshot Bundle Generation Prior to Pod Restart

### 1. Context
Before restarting a degraded pod, responders must capture JVM diagnostic state so root cause analysis can be performed post-incident.

### 2. Execution Runbook

#### Step 1: Run Snapshot Script Inside Pod
```bash
# Execute remote diagnostic capture on the offending pod
kubectl exec -it <POD_NAME> -n production -- /bin/bash -c "
  mkdir -p /tmp/dump
  jcmd 1 Thread.print > /tmp/dump/threads.txt
  jcmd 1 GC.class_histogram | head -n 60 > /tmp/dump/histogram.txt
  cat /sys/fs/cgroup/cpu.stat > /tmp/dump/cgroup_cpu.txt
  tar -czf /tmp/forensic-snapshot.tar.gz -C /tmp/dump .
"
```

#### Step 2: Copy Bundle to Local Terminal / Forensic S3 Bucket
```bash
kubectl cp production/<POD_NAME>:/tmp/forensic-snapshot.tar.gz ./forensic-snapshot.tar.gz
aws s3 cp ./forensic-snapshot.tar.gz s3://corp-incident-forensics/inc-84920/
```

#### Step 3: Authorize Pod Restart
Only once the tarball is safely written to S3, the Incident Commander authorizes:
```bash
kubectl delete pod <POD_NAME> -n production
```

---

## Runbook 05: Facilitating a Blameless Post-Mortem and Root Cause 5-Whys Session

### 1. Post-Mortem Meeting Schedule & Preparation
- **Timeline**: Schedule within 48 to 72 hours of incident resolution.
- **Duration**: 50 minutes.
- **Attendees**: Incident Commander, Responders, Service Owner, Lead Architect, Scribe.

### 2. Meeting Facilitation Agenda

#### Phase 1: Establishing Dekker's Just Culture (5 Minutes)
The Facilitator opens with the mandatory preamble:
> *"We hold post-mortems to learn how our systems can be made more resilient, not to assign blame. Every responder acted with good intentions based on the information they had. The term 'human error' is not accepted as a root cause."*

#### Phase 2: Chronological Timeline Walkthrough (15 Minutes)
Review the scribe's timestamped log:
- When was the defect introduced?
- When did customer impact begin (MTTD)?
- When did the alert trigger (MTTA)?
- What hypotheses were tested?
- What action successfully mitigated the outage (MTTR)?

#### Phase 3: The 5-Whys Root Cause Drill-Down (15 Minutes)
Iterate through 5 levels of causation to peel back proximate symptoms to latent architectural defects.

#### Phase 4: Action Item Formulation & SLA Commitment (15 Minutes)
Every agreed action item must meet the SRE Hierarchy of Controls:
- **P0 (14-Day SLA)**: Automated engineering controls (linters, circuit breakers, canary gates) to eliminate recurrence.
- **P1 (30-Day SLA)**: Monitoring and observability improvements.
Assign each item a specific engineer owner and create corresponding Jira tickets before adjourning.
