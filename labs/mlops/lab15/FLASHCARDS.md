# Production ML Architecture - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why draw three paths instead of one pipeline? | Training, serving and feedback have different constraints and failure domains; one diagram hides the breaks. |
| 2 | What belongs in a degradation ladder? | An ordered list of fallbacks, ending in a baseline or a rules engine, each logged as degraded. |
| 3 | What is the serving latency budget made of? | Feature reads plus inference plus queueing, each needing its own number and its own p99. |
| 4 | Why does availability multiply along the path? | The system is only as available as the required components in series, so the weakest dominates. |
| 5 | What is the feedback delay problem? | Outcomes arrive late and are biased toward current behaviour, so drift is invisible for weeks. |
| 6 | Why explore deliberately? | Without exploration the model converges to reinforcing its own decisions and cannot learn a new behaviour class. |
| 7 | What is a bulkhead? | Separate bounded resource pools per dependency so one slow dependency cannot exhaust everything. |
| 8 | Why does rollback need pre-authorisation? | Because rollback time is dominated by finding an approver, not by the technical step. |
| 9 | What is Three paths, not one pipeline? | Training (batch, reproducible, slow), serving (online, fast, stateless) and feedback (delayed labels and outcomes) are different systems with different constraints. |
| 10 | What is Serving is a read path with a cache? | The serving path is a feature read plus a model inference plus a decision, with strict latency. |
| 11 | What is Degradation is a design decision? | Each dependency can fail: feature store, model registry, upstream event stream. |
| 12 | What is Feedback loops have latency and bias? | Outcomes arrive late and are biased toward what the current system did. |
| 13 | What is Consistency choices per interaction? | A read-your-writes guarantee matters when a user updates a profile and immediately expects a changed recommendation; it does not matter for a batch dashboard. |
| 14 | What is The architecture is the failure playbook? | Every arrow in the diagram is a dependency that can fail. |
| 15 | In this lab, what does `p99_end_to_end = p99_features + p99_inference + p99_queue` mean? | Latency budget: every term needs a number |
| 16 | In this lab, what does `availability = prod(availability_i) over the required path` mean? | Availability: the weakest link dominates |
| 17 | In this lab, what does `error_budget_burn = observed / allowed` mean? | Burn rate: drives the alerting threshold |
| 18 | In this lab, what does `degradation_ladder = (full, reduced, baseline, reject)` mean? | Fallback order: explicit, not accidental |
| 19 | In this lab, what does `feedback_delay = now - decision_time` mean? | Label lag: bounds how fast drift can be seen |
| 20 | In this lab, what does `cost_per_1k_decisions = infra + compute_amortised` mean? | Unit economics: the number leadership cares about |
| 21 | You see 'A feature store outage takes scoring down entirely' in production. What is the cause and the fix? | no fallback in the read path Fix: degradation ladder ending at a baseline or rules engine |
| 22 | You see 'Rollback requires a 40-minute meeting' in production. What is the cause and the fix? | no pre-authorisation Fix: pre-authorised rollback with recorded reasons |
| 23 | You see 'Users see stale recommendations after editing their profile' in production. What is the cause and the fix? | inconsistency assumed rather than chosen Fix: per-interaction consistency choice with a reason |
| 24 | You see 'The model never learns from a new behaviour class' in production. What is the cause and the fix? | feedback loop with no exploration Fix: deliberate exploration or shadow scoring of alternatives |
| 25 | You see 'Cost per decision doubles and nobody knows' in production. What is the cause and the fix? | no unit economics Fix: cost per 1k decisions on the dashboard |
| 26 | You see 'Everything is one big service' in production. What is the cause and the fix? | training and serving share a failure domain Fix: separate deployments, separate scaling, separate rollback |
| 27 | Which Java API is the backbone of: the three that matter for a read path | `Resilience patterns: circuit breaker, bulkhead, timeout` |
| 28 | Which Java API is the backbone of: bulkhead so a slow feature store cannot starve inference | `Semaphore-bounded thread pools per dependency` |
| 29 | Which Java API is the backbone of: the decision log that makes degradation visible | `record Decision(String id, double score, String modelVersion, String[] fallbacksUsed)` |
| 30 | Which Java API is the backbone of: every arrow in the diagram gets a metric | `Micrometer for per-dependency latency` |
| 31 | Which Java API is the backbone of: budgets in config, not scattered as literals | `Immutable config for latency budgets` |
| 32 | Why does Three paths, not one pipeline matter operationally? | Training (batch, reproducible, slow), serving (online, fast, stateless) and feedback (delayed labels and outcomes) are different systems with different constraints. |
| 33 | Why does Serving is a read path with a cache matter operationally? | The serving path is a feature read plus a model inference plus a decision, with strict latency. |
| 34 | Why does Degradation is a design decision matter operationally? | Each dependency can fail: feature store, model registry, upstream event stream. |
| 35 | Why does Feedback loops have latency and bias matter operationally? | Outcomes arrive late and are biased toward what the current system did. |
| 36 | Why does Consistency choices per interaction matter operationally? | A read-your-writes guarantee matters when a user updates a profile and immediately expects a changed recommendation; it does not matter for a batch dashboard. |
| 37 | Why does The architecture is the failure playbook matter operationally? | Every arrow in the diagram is a dependency that can fail. |
| 38 | In the Production ML Architecture pipeline, what happens next? Draw three paths: batch training, online serving, and delaye... | Draw three paths: batch training, online serving, and delayed feedback. |
| 39 | In the Production ML Architecture pipeline, what happens next? Give the serving path a latency budget and a degradation lad... | Give the serving path a latency budget and a degradation ladder with named fallbacks. |
| 40 | In the Production ML Architecture pipeline, what happens next? Choose consistency per interaction and write the reason next... | Choose consistency per interaction and write the reason next to it. |
| 41 | In the Production ML Architecture pipeline, what happens next? Instrument every arrow with a metric, an SLO and an owner.... | Instrument every arrow with a metric, an SLO and an owner. |
| 42 | In the Production ML Architecture pipeline, what happens next? Plan the rollout: shadow, canary, ramp, with guardrails and ... | Plan the rollout: shadow, canary, ramp, with guardrails and rollback at each step. |
| 43 | In the Production ML Architecture pipeline, what happens next? Write the failure playbooks first, then the happy-path descr... | Write the failure playbooks first, then the happy-path description. |
| 44 | Exercise focus: Draw and validate the architecture | Three paths, every edge owned. |
| 45 | Exercise focus: Latency budget allocation | Make the budget real. |
| 46 | Exercise focus: Degradation ladder design | Order the fallbacks by quality cost. |
| 47 | Exercise focus: Consistency choices per interaction | Choose deliberately and write the reason. |
| 48 | Exercise focus: Availability arithmetic | Find the weakest link. |
| 49 | Exercise focus: Rollout and rollback design | Shadow, canary, ramp, and back. |
| 50 | State the End-to-end latency budget result for Production ML Architecture. | Budget 60 ms: features 20, inference 25, queue 10, overhead 5. If features p99 slips to 45 without a timeout, the total becomes 85 and the SLO is missed while every component's dashboard looks individually acceptable. |
| 51 | State the Availability along the read path result for Production ML Architecture. | Registry 0.999, feature store 0.999, compute 0.9995, network 0.9999: product is about 0.9974, or 26 minutes of downtime a month. Removing the registry from the hot path by caching the model locally lifts it to 0.9985. |
| 52 | State the Degradation ladder and blast radius result for Production ML Architecture. | Detection 4 minutes: cached model in 200 ms, baseline in 50 ms, rules in 20 ms. All three rungs are reachable inside detection, so the ladder is useful; a 10-minute 'warm standby' rung would not be. |
| 53 | State the Feedback delay and detection bound result for Production ML Architecture. | 30-day churn labels: quality monitoring has a floor of 30 days. Feature PSI can alert same-day, so the architecture needs both, with the understanding that PSI is the early warning and quality is the truth. |
| 54 | What does 'consistent enough' mean here? | Choosing a consistency level per interaction and writing the reason, rather than assuming one global guarantee. |
| 55 | What is unit economics for an ML system? | Cost per 1,000 decisions, including amortised training, which is the number leadership cares about. |
| 56 | When is a rules engine the right fallback? | When a model outage would be worse than a weaker but predictable decision path. |
| 57 | What does shadow scoring buy at the architecture level? | It is the only way to compare a challenger on live traffic without affecting users. |
| 58 | Assumption / invariant to defend: Training and serving are separate systems with separate failure domain... | Training and serving are separate systems with separate failure domains |
| 59 | Assumption / invariant to defend: The serving path has a bounded fallback that is logged as degraded... | The serving path has a bounded fallback that is logged as degraded |
| 60 | Assumption / invariant to defend: Every dependency in the read path has an owner and an SLO... | Every dependency in the read path has an owner and an SLO |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
