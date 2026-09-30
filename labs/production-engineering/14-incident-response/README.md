# Lab 14: Production Incident Response & RCA
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: SRE

---

## 🎯 Objectives

- Run an effective incident response from detection to resolution
- Communicate clearly during incidents (internal and external)
- Write blameless post-mortems that actually improve systems
- Build action items that prevent recurrence
- Design on-call rotations and escalation policies
- Measure MTTR, MTTD, and incident frequency
- Practice incident simulation with GameDays

---

## 📖 Real-World Context

**The Anatomy of a Great Incident Response**: Google's Site Reliability Engineering book defines how world-class teams handle incidents. The difference between a 10-minute resolution and a 3-hour resolution is almost always:
1. One person takes incident commander role
2. Clear communication channel
3. Systematic hypothesis testing (not random changes)
4. Decision to escalate vs continue debugging

This lab teaches the human and process side of production incidents.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Incident classification, ICS, post-mortem methodology |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Annotated real incident timelines with learnings |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Alerting code, runbook automation, status pages |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | On-call design, escalation policy design |
| [RUNBOOKS.md](./RUNBOOKS.md) | Universal incident command runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | "Tell me about a production incident" questions |
| [EXERCISES.md](./EXERCISES.md) | Incident simulation GameDay exercises |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Blame culture, unclear ownership, hero culture |
| [CHECKLIST.md](./CHECKLIST.md) | Incident response readiness checklist |

---

## 📋 Blameless Post-Mortem Template

```markdown
# Post-Mortem: [Service] [Date]

## Impact
- Duration: 45 minutes
- Users affected: ~12,000 (15% of traffic)
- Revenue impact: ~$45,000
- SLO impact: 2.3% of monthly error budget consumed

## Timeline (all times UTC)
- 14:23 — Alert fires: payment_success_rate < 95%
- 14:25 — On-call acknowledges, opens incident channel
- 14:31 — Root cause identified: connection pool exhausted
- 14:38 — Mitigation applied: increased pool size, restarted service
- 14:48 — Error rate returns to normal, incident resolved

## Root Cause
Upstream fraud service latency increased from 30ms to 800ms due to
unrelated database issue. Our connection pool exhausted as threads
waited for slow fraud checks, causing request queuing.

## Contributing Factors
1. No timeout on fraud service calls (calls could block indefinitely)
2. Connection pool size not sized for worst-case upstream latency
3. No circuit breaker on fraud service

## Action Items
| Action | Owner | Due |
|--------|-------|-----|
| Add 500ms timeout to fraud service client | @alice | Oct 7 |
| Add circuit breaker to fraud service | @bob | Oct 7 |
| Add connection pool wait timeout alert | @carol | Oct 10 |
| Load test with slow upstream | @dave | Oct 14 |
```

---

## 🔗 Related Labs
- Lab 08: [Observability & SRE](../08-observability-sre/)
- Lab 04: [Distributed Resilience](../04-distributed-resilience/)
- Lab 20: [Production Readiness](../20-production-readiness/)
