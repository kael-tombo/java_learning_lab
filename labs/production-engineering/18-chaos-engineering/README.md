# Lab 18: Chaos Engineering & Fault Injection
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 8 hours | **Level**: Advanced | **Domain**: SRE / Resilience

---

## 🎯 Objectives

- Understand the principles of chaos engineering (from Netflix Chaos Monkey)
- Design safe chaos experiments with blast radius control
- Use Chaos Monkey for Spring Boot (CM4SB)
- Implement fault injection at the code level
- Run GameDays to practice incident response
- Test failure scenarios: network partition, disk full, CPU spike, memory pressure
- Build confidence that your system fails gracefully

---

## 📖 Real-World Context

**"Chaos That Found a Bug"**: Netflix's Chaos Monkey randomly terminated production EC2 instances. During a chaos experiment, they discovered that their auto-scaling group wasn't properly configured — when an instance was terminated, the replacement took 8 minutes (not the expected 2 minutes), causing service degradation. They fixed this in a controlled experiment. If this had happened during a real failure (hardware), it would have been a major incident.

The philosophy: **Break things intentionally before they break unintentionally.**

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Chaos engineering principles, experiment design |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Bugs found through chaos, unexpected resilience gaps |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | CM4SB, Chaos Toolkit, Litmus for K8s |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Chaos experiment design decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Chaos experiment execution runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Chaos and resilience interview questions |
| [EXERCISES.md](./EXERCISES.md) | Design and run your first chaos experiment |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Chaos anti-patterns (no steady state, wrong scope) |
| [CHECKLIST.md](./CHECKLIST.md) | Chaos engineering readiness checklist |

---

## ⚙️ Chaos Monkey for Spring Boot Config

```yaml
chaos:
  monkey:
    enabled: true
    watcher:
      controller: true
      restController: true
      service: true
      repository: false    # Don't kill DB layer (too risky)
    assaults:
      level: 5             # 1 in 5 calls affected
      latencyActive: true
      latencyRangeStart: 500
      latencyRangeEnd: 2000
      exceptionsActive: false  # Start with latency only
      killApplicationActive: false  # Never in prod!
```

---

## 🔗 Related Labs
- Lab 04: [Distributed Resilience](../04-distributed-resilience/)
- Lab 14: [Incident Response](../14-incident-response/)
- Lab 08: [Observability & SRE](../08-observability-sre/)
