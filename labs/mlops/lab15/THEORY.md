# Production ML Architecture

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Problem This Solves

You now have every component: pipeline, tracking, registry, feature store, serving, monitoring, governance. The remaining work is arranging them so the system degrades predictably.

Architecture is where component quality becomes system behaviour. The failure modes of ML systems are mostly integration failures, not algorithm failures.

## 2. Learning Objectives

- Design an end-to-end architecture with explicit data, control and feedback paths
- Separate the training path from the serving path deliberately
- Design for degradation: what each component does when its dependencies fail
- Choose consistency levels per interaction and justify them
- Plan the rollout from shadow to canary to full, with guardrails
- Produce an architecture with named owners, SLOs and failure playbooks

## 3. Core Concepts

### 3.1 Three paths, not one pipeline

Training (batch, reproducible, slow), serving (online, fast, stateless) and feedback (delayed labels and outcomes) are different systems with different constraints. Architecture diagrams that draw one pipeline are usually hiding the places things break.

### 3.2 Serving is a read path with a cache

The serving path is a feature read plus a model inference plus a decision, with strict latency. Everything else about the model lifecycle is batch. Designing the read path first, with a bounded fallback, is what makes the system survive dependency outages.

### 3.3 Degradation is a design decision

Each dependency can fail: feature store, model registry, upstream event stream. For each you decide what the service does. Silent fallback to a weaker model is often better than an error, provided it is logged and monitored as degraded.

### 3.4 Feedback loops have latency and bias

Outcomes arrive late and are biased toward what the current system did. Exploration is needed or the model converges to reinforcing its own decisions. This is why shadow tests and deliberate exploration exist.

### 3.5 Consistency choices per interaction

A read-your-writes guarantee matters when a user updates a profile and immediately expects a changed recommendation; it does not matter for a batch dashboard. Choosing per interaction, with a reason, is what makes latency budgets achievable.

### 3.6 The architecture is the failure playbook

Every arrow in the diagram is a dependency that can fail. If the diagram does not say what happens when that arrow breaks, the architecture is incomplete, regardless of how clean it looks.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `p99_end_to_end = p99_features + p99_inference + p99_queue` | Latency budget | every term needs a number |
| `availability = prod(availability_i) over the required path` | Availability | the weakest link dominates |
| `error_budget_burn = observed / allowed` | Burn rate | drives the alerting threshold |
| `degradation_ladder = (full, reduced, baseline, reject)` | Fallback order | explicit, not accidental |
| `feedback_delay = now - decision_time` | Label lag | bounds how fast drift can be seen |
| `cost_per_1k_decisions = infra + compute_amortised` | Unit economics | the number leadership cares about |

## 5. How the Pieces Fit Together

1. Draw three paths: batch training, online serving, and delayed feedback.

2. Give the serving path a latency budget and a degradation ladder with named fallbacks.

3. Choose consistency per interaction and write the reason next to it.

4. Instrument every arrow with a metric, an SLO and an owner.

5. Plan the rollout: shadow, canary, ramp, with guardrails and rollback at each step.

6. Write the failure playbooks first, then the happy-path description.

## 6. Assumptions and Invariants

- Training and serving are separate systems with separate failure domains
- The serving path has a bounded fallback that is logged as degraded
- Every dependency in the read path has an owner and an SLO
- Consistency choices are explicit and justified per interaction
- Feedback latency is documented and bounded in the monitoring design
- Rollout stages have guardrails and a rehearsed rollback

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| A feature store outage takes scoring down entirely | no fallback in the read path | degradation ladder ending at a baseline or rules engine |
| Rollback requires a 40-minute meeting | no pre-authorisation | pre-authorised rollback with recorded reasons |
| Users see stale recommendations after editing their profile | inconsistency assumed rather than chosen | per-interaction consistency choice with a reason |
| The model never learns from a new behaviour class | feedback loop with no exploration | deliberate exploration or shadow scoring of alternatives |
| Cost per decision doubles and nobody knows | no unit economics | cost per 1k decisions on the dashboard |
| Everything is one big service | training and serving share a failure domain | separate deployments, separate scaling, separate rollback |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Resilience patterns: circuit breaker, bulkhead, timeout` | the three that matter for a read path |
| `Semaphore-bounded thread pools per dependency` | bulkhead so a slow feature store cannot starve inference |
| `record Decision(String id, double score, String modelVersion, String[] fallbacksUsed)` | the decision log that makes degradation visible |
| `Micrometer for per-dependency latency` | every arrow in the diagram gets a metric |
| `Immutable config for latency budgets` | budgets in config, not scattered as literals |

## 9. Where This Sits in the Larger System

- **Every lab in this track** contributes a component; this lab is where they meet.
- **mlops/lab06** is the runtime substrate for the serving path.
- **mlops/lab08** is the monitoring that makes degradation visible.
- **mlops/lab11** is the governance that makes the audit trail complete.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Design an end-to-end architecture with explicit data, control and feedback paths
- [ ] 0 — cannot yet — Separate the training path from the serving path deliberately
- [ ] 0 — cannot yet — Design for degradation: what each component does when its dependencies fail
- [ ] 0 — cannot yet — Choose consistency levels per interaction and justify them
- [ ] 0 — cannot yet — Plan the rollout from shadow to canary to full, with guardrails
- [ ] 0 — cannot yet — Produce an architecture with named owners, SLOs and failure playbooks

## 11. Summary Checklist

- [ ] Training, serving and feedback are drawn as separate paths.
- [ ] The serving path has an explicit degradation ladder.
- [ ] Every dependency has an owner, an SLO and a metric.
- [ ] Consistency choices are documented per interaction.
- [ ] Rollout stages have guardrails and a rehearsed rollback.
- [ ] Unit economics are on the dashboard.
