# PRODUCTION SCENARIOS: Chaos Engineering Case Studies
## Lab 18 | Production Engineering Academy

---

## Scenario 1: The Uncontained Chaos Game Day Outage

### Context
An e-commerce engineering team scheduled a monthly "Game Day" chaos experiment in production to test resilience against a Redis cache failure.

### The Disaster
- Chaos tool injected 100% packet loss to the Redis cluster.
- The hypothesis: "Application services will fall back to querying the primary Aurora PostgreSQL database without customer disruption."
- Reality: While the services successfully fell back to the database, the un-cached query traffic was $15\times$ higher than the database could handle!
- PostgreSQL CPU hit 100% within 8 seconds, and connection pools across 40 services exhausted simultaneously.
- To make matters worse, the chaos tool's abort API hung because its own management network was routed through the congested subnet!
- Responders spent 22 minutes manually killing chaos daemon processes via SSH while customer checkout was completely offline.

### Key Lessons
1. **Automated Dead Man's Switch**: Chaos experiments must always use self-terminating timers (e.g. max duration 5 minutes). If the control plane disconnects, the experiment must auto-revert.
2. **Blast Radius Containment**: Test first in Staging, then on internal Canary traffic in Production, never 100% of global production traffic on day one.
3. **Hard SLO Abort Guards**: Link chaos orchestrators directly to Prometheus alerts: if error budget burn rate crosses $2\times$, abort immediately.

---

## Scenario 2: The Hidden Single Point of Failure (SPOF) Discovery

### Context
A banking app had fully redundant, multi-AZ microservices and databases.

### The Game Day Experiment
Engineers injected a simulated total network partition of AWS Availability Zone `us-east-1a`.
- Microservices automatically failed over to `us-east-1b` and `us-east-1c`.
- However, 100% of logins suddenly failed!
- Investigation revealed an undocumented legacy license server required by an optical character recognition (OCR) library. That single VM existed only in `us-east-1a` with no backup!
- Chaos engineering successfully surfaced an existential architectural flaw during controlled business hours rather than an unpredictable 3:00 AM catastrophe.
