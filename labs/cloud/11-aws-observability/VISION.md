# AWS Observability - Vision

## The Big Picture
CloudWatch is a metrics, log, and alarm API that everything in AWS already emits to whether you
intend it or not. The skill is not reading dashboards — it is designing instrumentation that
answers questions and keeps cardinality survivable.

## Why This Matters
Uninstrumented services are un-debuggable at scale, and badly instrumented ones are worse:
they cost more than the compute, break the metrics backend, and produce dashboards nobody
opens. This lab is about signal discipline.

## The Vision for This Lab
This lab builds the observability stack for a distributed application: metrics that reflect
the four golden signals, logs that correlate with traces, and X-Ray traces that survive
service boundaries. Then it makes it survivable at scale with an explicit dimensionality budget.

## Learning Philosophy
1. Instrument the outcome, not the internals — users feel latency, not thread counts
2. Dimensionality is a budget; new labels are a purchase
3. Every dashboard panel must inform a decision
4. A metric nobody alerts on is a cost with no return

## Future Path
- 20-distributed-monitoring — the theory behind this tooling
- 08-observability-sre — SLOs and error budgets
- 14-incident-response — what the signals are for

## Success Metrics
You have mastered AWS observability when you can:
- [ ] Emit custom metrics with a deliberate dimensionality budget
- [ ] Trace a request across three services with X-Ray and verify continuity
- [ ] Build a RED dashboard where every panel maps to a decision
- [ ] Write an alarm that fires on symptom and has a documented first action

## The Observability Mindset
> Instrumentation is a product for the engineers who will be woken up at 3am. Give them the
fewest signals that reliably identify the problem, and make each one cheap enough to keep
forever.