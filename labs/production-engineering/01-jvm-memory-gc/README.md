# Lab 01: JVM Memory Architecture & GC Mastery
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 12 hours | **Level**: Expert | **Domain**: JVM Internals

---

## 🎯 Objectives

By the end of this lab you will:
- Understand every region of JVM memory and how objects move through it
- Choose the right GC algorithm for your workload (G1, ZGC, Shenandoah, Parallel)
- Read and interpret GC logs like a surgeon
- Size heap regions for production workloads
- Diagnose and fix OOMEs, memory leaks, GC pressure in live systems
- Know when GC is NOT the problem

---

## 📖 Real-World Context

**The Scenario**: Your e-commerce platform serves 50,000 concurrent users. Every Black Friday, your JVM pauses for 8-12 seconds during Full GC, causing cascading timeouts. Orders are lost. Your CEO is furious. Your on-call engineer is exhausted.

This isn't a textbook problem. This is Tuesday at Amazon, Netflix, LinkedIn, Booking.com.

---

## 🔖 Contents

1. [THEORY.md](./THEORY.md) — JVM memory model, GC algorithms, heap internals
2. [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) — Real incidents with memory
3. [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) — Java code patterns, JVM flags, GC analysis
4. [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) — GC selection guide
5. [RUNBOOKS.md](./RUNBOOKS.md) — On-call runbook for OOM/GC incidents
6. [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) — Staff/Principal level questions
7. [EXERCISES.md](./EXERCISES.md) — Hands-on heap analysis exercises
8. [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) — Memory anti-patterns with war stories
9. [CHECKLIST.md](./CHECKLIST.md) — Production JVM configuration checklist

---

## 🚀 Quick Start

```bash
# Run heap analysis exercise
java -Xmx512m -Xms512m \
  -XX:+UseG1GC \
  -Xlog:gc*:file=gc.log:time,uptime,level,tags \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/heapdump.hprof \
  -jar your-app.jar
```

---

## 🔗 Related Labs
- Lab 03: [Production Debugging & Profiling](../03-production-debugging/)
- Lab 15: [Performance Engineering](../15-performance-engineering/)
- Lab 20: [Production Readiness Checklist](../20-production-readiness/)
