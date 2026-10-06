# Observability - Vision

## Why This Lab Exists
In a distributed system, the only way to know what happened is to have recorded
it before you needed it. Teams that treat observability as a dashboard build
discover at 02:00 that they have four dashboards and no way to answer "did this
user see a failure?". This lab exists to reframe observability as *evidence
collection*, not visualisation.

## The Mental Model
Three signals, three questions — do not mix them:

```
  Logs   -> "what happened to THIS request?"   (high cardinality, sampled)
  Metrics-> "is the system unhealthy?"          (aggregated, low cardinality)
  Traces -> "where did the time go?"            (spans, sampled + tail)
```

Metrics tell you *that*. Traces tell you *where*. Logs tell you *what*.
Cardinality is the tax: every unbounded label on a metric can kill the backend.

## What You Should Be Able To Do
- Define a RED or USE method for a service and pick ONE per subsystem.
- Define a golden-signal dashboard and an SLO alert that pages, not one that
  annoys.
- Trace a request across three services and pick a propagation mechanism
  (W3C trace context, not a custom header).
- Compute an error budget burn rate and justify the page threshold.
- Write a query that answers "why did checkout get slow at 14:02?" within
  five minutes of noticing.
- Explain tail sampling and why head sampling loses exactly the requests that
  matter.

## The Anti-Goals
- No metric labelled with user ID, request ID, or raw path.
- No alert without a linked runbook and a stated action.
- Logging everything is not observability; it is cost with no query path.

## Success Criteria
Given a live incident description, you can name the three queries you would run,
in order, and predict roughly how long each takes to return an answer.

## How To Use This Lab
1. `THEORY.md` for the three signals and cardinality discipline.
2. `MATH_FOUNDATION.md` for percentiles, error budget, burn rate, sampling.
3. `CODE_DEEP_DIVE.md` for structured logging, metrics, and tracing in Java.
4. `MINI_PROJECT.md` to instrument a service end to end.
5. `REAL_WORLD_PROJECT.md` to build an SLO and alerting regime.
