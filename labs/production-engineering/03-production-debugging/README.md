# Lab 03: Production Debugging & Profiling
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 12 hours | **Level**: Expert | **Domain**: Observability & Diagnostics

---

## 🎯 Objectives

- Profile JVM CPU usage with async-profiler (flame graphs)
- Analyze heap dumps with Eclipse MAT to find memory leaks
- Capture and analyze thread dumps to diagnose deadlocks
- Debug production issues without disrupting live traffic
- Use `jcmd`, `jstack`, `jstat`, `jmap` effectively
- Instrument code with OpenTelemetry for distributed tracing
- Set up structured logging for root-cause analysis

---

## 📖 Real-World Context

**"The Monday Slowdown"**: Every Monday morning, your order processing service degrades from p99=50ms to p99=3000ms by 11 AM. By 2 PM it's timing out. By 5 PM it's back to normal. No errors in logs. No exceptions. What do you do?

This lab teaches the systematic investigation skills to answer that question — in production, under pressure, with minimal impact to users.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Profiling techniques, JVM diagnostic tools, tracing |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Real debugging war stories with solutions |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | async-profiler, JFR, OpenTelemetry code |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Observability architecture decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Performance degradation investigation runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | "Debug this production problem" interview questions |
| [EXERCISES.md](./EXERCISES.md) | Analyze real heap dump and flame graph exercises |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Debugging anti-patterns (log.debug in hot paths, etc.) |
| [CHECKLIST.md](./CHECKLIST.md) | Production observability readiness checklist |

---

## 🛠️ Key Tools

```bash
# async-profiler (CPU/alloc/wall profiling)
./profiler.sh -e cpu -d 30 -f cpu.html $(pgrep java)

# jcmd (universal diagnostic tool)
jcmd $(pgrep java) GC.class_histogram | head -30
jcmd $(pgrep java) Thread.print
jcmd $(pgrep java) VM.native_memory summary

# jfr (Java Flight Recorder — low-overhead continuous profiling)
jcmd $(pgrep java) JFR.start name=prod-recording duration=60s filename=recording.jfr

# Eclipse MAT for heap analysis
# JDK Mission Control for JFR analysis
```

---

## 🔗 Related Labs
- Lab 08: [Observability & SRE](../08-observability-sre/)
- Lab 14: [Incident Response](../14-incident-response/)
- Lab 15: [Performance Engineering](../15-performance-engineering/)
