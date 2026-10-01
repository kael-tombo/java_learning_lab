# INTERVIEW QUESTIONS: Incident Response, SRE War Rooms & Post-Mortem Engineering
## Lab 14 | Senior / Staff / Principal / Distinguished Level

---

## Senior Level (5–7 Years)

### Q1: What is the foundational operational distinction between incident *mitigation* and incident *resolution*? Why does confusing them inflate MTTR?

**Answer:**
- **Mitigation**: The immediate restoration of service availability, customer SLOs, and business continuity. Examples: rolling back a bad deployment, failing over to a secondary region, tripping a load-shedding circuit breaker, restarting degraded pods.
- **Resolution**: Finding the exact software bug, writing a failing regression test, developing a clean architectural patch, completing code reviews, and deploying the permanent fix.

**Why Confusing Them Inflates MTTR**:
When an engineer with a "debugger mindset" joins an active P1 outage, their natural inclination is to find the exact line of code that broke. They may spend 45 minutes capturing memory dumps or stepping through stack traces while customers are failing transactions at $20,000/minute.
- Conflating resolution with mitigation inflates **Mean Time to Mitigate (MTTR)** by $300\% - 500\%$.
- **The Axiom**: In production emergencies, **always mitigate first** (stop customer bleeding in $< 10\text{ minutes}$ via rollback or failover). Forensic deep-dives and permanent resolution belong in staging during post-incident analysis.

---

### Q2: What is the cardinal rule of an Incident Commander (IC), and why is it disastrous for an IC to touch a terminal or inspect code during a P1 outage?

**Answer:**
**The Cardinal Rule: The Incident Commander (IC) NEVER touches a keyboard, writes code, or debugs during an incident!**

**Why It Is Disastrous**:
1. **Loss of Situational Awareness**: The moment an IC begins reading a stack trace or typing `kubectl` commands, their cognitive bandwidth narrows down to a single micro-hypothesis ("tunnel vision"). They lose the high-level bird's-eye view of the entire system.
2. **Uncoordinated Side-Interventions**: While the IC is buried in logs, other responders on the bridge begin making unvetted changes without approval.
3. **Pacing and Time-Budget Failure**: The IC fails to track the time budget (e.g. noticing that a hypothesis has taken 15 minutes without progress) and forgets to enforce rollback decisions.
4. **Responders Frozen**: When the commander is typing, responders have no one to validate or authorize their proposed actions.

The IC's role is strictly that of an **orchestrator**: approving or rejecting proposed hypotheses, maintaining the timeline, enforcing single-variable modifications, and deciding when to execute rollbacks or regional failovers.

---

## Staff Level (8–12 Years)

### Q3: Explain Sidney Dekker's "Just Culture" philosophy. Why is concluding "human error" considered an architectural and procedural failure in modern SRE post-mortems?

**Answer:**
In Sidney Dekker's *The Field Guide to Understanding Human Error*, **human error is the symptom of deeper systemic vulnerabilities, never the root cause**.

**The Fallacy of Human Error**:
- Blaming an individual ("Engineer Bob forgot to run migrations") assumes that Bob came to work wanting to cause an outage, and that replacing Bob with another engineer would make the system safe.
- In reality, Bob was operating within a system designed by the organization. If the system allows a single engineer to deploy an unvetted SQL migration without schema validation, automated linting, or canary gating, **the system is hazardous by design**.
- Concluding "human error" is lazy: it halts the investigation prematurely and leaves the underlying latent hazards completely intact. The next engineer will inevitably trigger the exact same hazard.

**The Post-Mortem Standard**:
A blameless post-mortem treats the engineer's action as the *starting point* of the investigation:
- *Why did the system allow this action?*
- *What feedback did the UI/CLI provide?*
- *Why was there no automated canary gate to detect the failure on 1% of traffic?*
- *How can we implement an Engineering Control that makes this mistake physically impossible to repeat?*

---

### Q4: How does an Adaptive Concurrency Limiter (e.g., Netflix Vegas / AIMD) prevent queue bloat and cascading service death spirals during database degradation?

**Answer:**
Traditional service architectures rely on fixed-size thread pools (e.g. Tomcat 200 threads) and unbounded request queues.

**The Queue Bloat Problem (Little's Law)**:
$$L = \lambda \cdot W$$
When a downstream database slows down (e.g., query latency jumps from 10ms to 2,000ms):
- All 200 worker threads become blocked waiting on database I/O.
- Incoming requests queue up in OS and application buffers.
- By the time a queued request reaches a worker thread after waiting 15 seconds in memory, the calling client (or Ingress timeout) has **already timed out and abandoned the request**!
- The server burns 100% of its CPU processing work for clients that have already disconnected, while fresh incoming requests are dropped.

**The Adaptive Concurrency Solution**:
Based on the TCP Vegas congestion control algorithm:
1. The limiter dynamically measures **Round Trip Time (RTT)** of requests.
2. It tracks the minimum observed latency as the baseline.
3. If measured latency rises, it detects queue buildup inside the system:
   $$\text{Queue Size} = \text{Current Limit} \times \left(1.0 - \frac{\text{Baseline RTT}}{\text{Current RTT}}\right)$$
4. The moment queue size exceeds a threshold, the limiter applies **Multiplicative Decrease**: it instantly slashes the maximum allowed concurrent requests (e.g. from 200 down to 40).
5. Any request exceeding the dynamic limit is rejected **immediately at the boundary** with `429 Too Many Requests` in $< 1\text{ms}$.
6. This preserves the remaining worker threads, prevents memory and database saturation, and allows the database to recover without collapsing.

---

### Q5: Contrast the four core ICS roles (Incident Commander, Technical Lead, Communications Lead, Scribe) during a Tier-0 payment outage.

**Answer:**

```
┌─────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Role                    │ Core Responsibilities & Rules of Engagement                            │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Incident Commander (IC) │ • Holds ultimate command authority over the war room.                  │
│                         │ • Does NOT debug, code, or touch terminals.                            │
│                         │ • Approves single-variable hypotheses; enforces rollback deadlines.    │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Technical Operations    │ • Leads technical Subject Matter Experts (DB, K8s, JVM).               │
│ Lead                    │ • Evaluates diagnostic signals and formulates mitigation plans.        │
│                         │ • Directs technical actions ONLY upon receiving verbal approval from IC│
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Communications Lead     │ • Shields technical responders from executive interruptions.           │
│ (Comms)                 │ • Posts internal Slack updates every 15-20 minutes.                   │
│                         │ • Publishes customer-facing updates to public Statuspage.              │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ Incident Scribe         │ • Maintains the chronological timestamped incident log.               │
│                         │ • Records every command run, hypothesis tested, and metric change.     │
│                         │ • Preserves raw evidence for the post-mortem.                          │
└─────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## Principal / Distinguished Level (12+ Years)

### Q6: Design a Disaster Recovery and Multi-Region Traffic Evacuation architecture capable of draining 100,000 requests/sec away from an impaired AWS region in under 5 minutes.

**Answer — Architecture Blueprint**:

```
                                      Route 53 / Cloudflare Anycast DNS
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
         ┌───────────────────────────┐                                 ┌───────────────────────────┐
         │     Region A (Primary)    │                                 │     Region B (Secondary)  │
         │  us-east-1 (Active 80k)   │                                 │  us-west-2 (Active 20k)   │
         ├───────────────────────────┤                                 ├───────────────────────────┤
         │ • ALB / Ingress           │                                 │ • Pre-Warmed Capacity     │
         │ • Active Java Fleet (80%) │                                 │ • Min Headroom = 60%      │
         │ • CockroachDB / DynamoDB  │ ◄────── Active-Active Multi ──► │ • CockroachDB / DynamoDB  │
         │   Global Tables           │         Region Sync (<150ms)    │   Global Tables           │
         └─────────────┬─────────────┘                                 └─────────────▲─────────────┘
                       │                                                             │
                       │ 🚨 Region A Impairment Detected (AWS Network / Power Drop)  │
                       └─────────────────── Region Evacuation ──────────────────────┘
                                            (Target: < 4 Minutes)
```

**Step-by-Step Evacuation Protocol**:
1. **Pre-Warmed Headroom Rule**: Region B must continuously run at least $50\% - 60\%$ of total peak fleet capacity during normal operations. Attempting to cold-scale hundreds of Java pods from zero during an emergency will fail due to cloud instance stockouts and 30-second JVM cold starts.
2. **Global DNS Traffic Shift (T+00 to T+90s)**:
   - Route 53 Application Recovery Controller (ARC) routing control flips Region A weighting to 0%.
   - DNS TTL configured to **$\le 30\text{ seconds}$** with Anycast edge routing.
3. **Edge Ingress Redirect (T+30s)**:
   - Cloudflare / CloudFront edge workers immediately route all requests targeting Region A to Region B via origin shield overrides, bypassing client-side DNS caching delays.
4. **State Layer Isolation (T+90s)**:
   - For multi-region datastores (CockroachDB / Spanner / DynamoDB Global Tables), isolate Region A replicas from the consensus quorum to prevent slow write acknowledgments.
5. **Autoscaling Ramp (T+2m to T+4m)**:
   - Karpenter on Region B initiates pre-emptive scaling to absorb the remaining 80% traffic surge.

---

### Q7: How do you establish an Engineering Hierarchy of Controls to ensure post-mortem action items permanently eliminate failure modes rather than turning into ignored Jira backlog debt?

**Answer — Governance Framework**:

**1. The SRE Hierarchy of Controls**:
Every proposed action item must be categorized according to the industrial safety hierarchy:
- **Level 1: Elimination (Mandatory $\ge 40\%$ of items)**: Completely remove the vulnerable code path, deprecate the brittle service, or eliminate manual data touchpoints.
- **Level 2: Engineering Controls (Mandatory $\ge 30\%$ of items)**: Automated guards that prevent failure even when humans make mistakes. Examples: CI schema linters, automated canary rollback triggers, database proxy query kill-switches, circuit breakers.
- **Level 3: Administrative / Training (Capped at $\le 30\%$)**: Runbooks, alerts, documentation, checklists. Platitudes like "team will be more careful" are rejected by the Review Board.

**2. The Post-Mortem Enforcement SLAs**:
- **P0 Actions (Prevent Direct Recurrence)**: Strict **14-day SLA**. If not deployed in 14 days, the service's feature release pipeline is automatically locked by CI/CD.
- **P1 Actions (Detection & Observability)**: Strict **30-day SLA**.
- **Sprint Tax**: The engineering team must allocate at least **$20\%$ of immediate sprint capacity** to post-mortem action items before resuming standard feature velocity.
- **Executive Review Board**: The VP of Engineering and Staff SREs review overdue post-mortem items weekly. An unresolved P0 action item is treated as an ongoing business risk.
