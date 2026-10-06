# Infrastructure as Code for ML - Flashcards (60 cards)

**Track:** mlops  |  **Lab:** lab12  |  **Level:** Intermediate

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
| 1 | What is the main value of infrastructure as code? | Changes become reviewable diffs with an author, not console clicks nobody can see. |
| 2 | How should topology and configuration be separated? | Topology (which resources exist) in code; values (names, counts, ARNs) in environment configuration. |
| 3 | Why do stateful resources need special care? | Destroying them means losing data, so recreate requires backups and a documented restore path. |
| 4 | What does drift detection give you? | The difference between what the code says should exist and what actually exists. |
| 5 | Why do GPU pools need quotas and priority? | They convert 'the cluster is full' from an outage into a visible queue. |
| 6 | Why require cost tags? | Chargeback and optimisation are impossible to do later without them. |
| 7 | What is a workspace for? | Per-team isolated state so one team's apply cannot destroy another's resources. |
| 8 | What should a plan contain? | Every create, update and destroy, so the destructive part is impossible to miss. |
| 9 | What is Code, not console? | Console-created resources are invisible to review, untagged by intent and impossible to reproduce. |
| 10 | What is Topology versus configuration? | Which resources exist (a GPU node pool, a bucket, a private subnet) is code. |
| 11 | What is Stateful resources need a different lifecycle? | A GPU pool is disposable; a feature store with production data is not. |
| 12 | What is Quota and priority are policy? | GPU hours are the scarce resource. |
| 13 | What is Drift detection is the missing half? | Code says what should exist; reality says what does. |
| 14 | What is Workspaces and least privilege? | Per-team state and per-team credentials prevent one team's apply from destroying another's resources. |
| 15 | In this lab, what does `plan = f(code, state) -> resource_changes` mean? | Plan semantics: the reviewable artifact |
| 16 | In this lab, what does `drift = actual - desired` mean? | Drift: difference between code and reality |
| 17 | In this lab, what does `cost = sum(gpu_hours x rate + storage_gb x rate)` mean? | Cost model: tagged per resource |
| 18 | In this lab, what does `quota_used = sum(active_requests)` mean? | Quota: the queueing constraint |
| 19 | In this lab, what does `recovery_time = RTO, recovery_point = RPO` mean? | Stateful SLOs: what recreate must preserve |
| 20 | In this lab, what does `apply = state := plan` mean? | Apply: atomic by region, reviewed before running |
| 21 | You see 'Production destroyed by a plan nobody read' in production. What is the cause and the fix? | destructive plan applied without review Fix: require review on plans, and forbid destroy on stateful resources without a restore check |
| 22 | You see 'Two environments diverge because the code was copied' in production. What is the cause and the fix? | topology and configuration in one file Fix: parameterise environment configuration separately |
| 23 | You see 'Cluster full and nobody knows whose job is queued' in production. What is the cause and the fix? | no quota or priority Fix: quotas and priority classes make the queue visible |
| 24 | You see 'GPU spend unattributable' in production. What is the cause and the fix? | resources without cost tags Fix: mandatory tags enforced in the plan stage |
| 25 | You see 'Drift accumulates for months' in production. What is the cause and the fix? | no drift detection Fix: scheduled drift detection with an owner per resource |
| 26 | You see 'One team's apply destroyed another's queue' in production. What is the cause and the fix? | shared state Fix: per-team workspaces with isolated state |
| 27 | Which Java API is the backbone of: keeps topology code environment-agnostic | `HOCON / properties for environment configuration` |
| 28 | Which Java API is the backbone of: the reviewable diff as a typed value | `record Plan(List<ResourceChange> changes, int create, int update, int destroy)` |
| 29 | Which Java API is the backbone of: drift detection as a pure function | `Diff computation on desired vs actual` |
| 30 | Which Java API is the backbone of: so a human or a bot reviews it before apply | `Structured plan output (JSON)` |
| 31 | Which Java API is the backbone of: policy encoded in types, not comments | `Immutable config classes for pools and quotas` |
| 32 | Why does Code, not console matter operationally? | Console-created resources are invisible to review, untagged by intent and impossible to reproduce. |
| 33 | Why does Topology versus configuration matter operationally? | Which resources exist (a GPU node pool, a bucket, a private subnet) is code. |
| 34 | Why does Stateful resources need a different lifecycle matter operationally? | A GPU pool is disposable; a feature store with production data is not. |
| 35 | Why does Quota and priority are policy matter operationally? | GPU hours are the scarce resource. |
| 36 | Why does Drift detection is the missing half matter operationally? | Code says what should exist; reality says what does. |
| 37 | Why does Workspaces and least privilege matter operationally? | Per-team state and per-team credentials prevent one team's apply from destroying another's resources. |
| 38 | In the Infrastructure as Code for ML pipeline, what happens next? Separate topology code from environment configuration and ve... | Separate topology code from environment configuration and version both. |
| 39 | In the Infrastructure as Code for ML pipeline, what happens next? Create a per-team workspace with isolated state and least-pr... | Create a per-team workspace with isolated state and least-privilege credentials. |
| 40 | In the Infrastructure as Code for ML pipeline, what happens next? Define pools with quota, priority and mandatory cost tags.... | Define pools with quota, priority and mandatory cost tags. |
| 41 | In the Infrastructure as Code for ML pipeline, what happens next? Run plan, review the diff, and record the reviewer with the ... | Run plan, review the diff, and record the reviewer with the apply. |
| 42 | In the Infrastructure as Code for ML pipeline, what happens next? Detect drift on a schedule and report divergence rather than... | Detect drift on a schedule and report divergence rather than silently correcting it. |
| 43 | In the Infrastructure as Code for ML pipeline, what happens next? Document the destroy-and-recreate path for stateful resource... | Document the destroy-and-recreate path for stateful resources, including backups. |
| 44 | Exercise focus: Generate and review a plan | The plan is the artifact. |
| 45 | Exercise focus: Topology versus configuration | Stop copying code between environments. |
| 46 | Exercise focus: Drift detection and attribution | Find what the code does not know about. |
| 47 | Exercise focus: Quota and priority | Turn contention into a queue. |
| 48 | Exercise focus: Cost attribution and idle detection | Find the money. |
| 49 | Exercise focus: Stateful recreate drill | Prove the restore path. |
| 50 | State the Plan, drift and the apply contract result for Infrastructure as Code for ML. | Desired: 3 node pools, 2 buckets, 1 private subnet. Actual: those plus a manually created 4th pool. Plan shows zero creates and zero destroys; drift reports the extra pool with no owner, which is a conversation, not an automatic delete. |
| 51 | State the GPU cost attribution result for Infrastructure as Code for ML. | Pool quota 40 A10G-hours per day, average usage 6. Idle for 7 days: the quota costs roughly 34 x 0.55 USD per hour x 24 = about 450 USD per day that nobody is using. |
| 52 | State the Quota and queueing behaviour result for Infrastructure as Code for ML. | Quota 8, demand 12: 8 admitted, 4 queued. With serving at priority 1 and batch at 3, the 4 queued are batch jobs; under heavy batch load serving preempts rather than queueing. |
| 53 | State the Stateful recreate and RPO/RTO result for Infrastructure as Code for ML. | Feature store with 6-hour snapshots: RPO 6 hours, restore 40 minutes. A plan destroying it should require an acknowledgement naming the snapshot and its age, not a bare 'yes'. |
| 54 | What is least privilege in this context? | Per-team credentials that can modify their own resources and nothing else. |
| 55 | How do you review a plan? | Treat the diff as the artifact: read destroys first, confirm applies match the ticket. |
| 56 | What is the difference between drift and desired change? | Desired change is intentional and in code; drift is a divergence nobody intended. |
| 57 | When should you correct drift automatically? | Rarely; report it, let the owner decide, since blind correction can delete manual fixes. |
| 58 | Assumption / invariant to defend: All infrastructure changes go through reviewed code, never a console... | All infrastructure changes go through reviewed code, never a console |
| 59 | Assumption / invariant to defend: Topology and environment configuration are in separate files... | Topology and environment configuration are in separate files |
| 60 | Assumption / invariant to defend: Per-team state and credentials prevent cross-team collisions... | Per-team state and credentials prevent cross-team collisions |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
