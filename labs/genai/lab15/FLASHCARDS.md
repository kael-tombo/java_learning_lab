# Lab 15: Building a GenAI Platform — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Platform | Capabilities + interfaces + ops + governance + enablement |
| 2 | Not a model server | The model is one component |
| 3 | Failure mode | Governance without usability, or capability without governance |
| 4 | Layer order | Consumption > product > platform > model > data > infra |
| 5 | Dependency rule | Downward only |
| 6 | Why | Upward coupling means every product bug lands in the model layer |
| 7 | Logical model names | `chat-fast`, `chat-quality`, `embed`, `rerank` |
| 8 | Value of logical names | Swap models without touching product code |
| 9 | Registry fields | provider, version, capabilities, SLOs, health, deployment |
| 10 | Routing: capability | Functional requirement (vision, tools) |
| 11 | Routing: quality tier | Cost/quality policy |
| 12 | Routing: latency tier | SLO separation (interactive vs batch) |
| 13 | Routing: region | Data residency |
| 14 | Routing: health | Resilience |
| 15 | Routing: cost ceiling | Finops |
| 16 | Fallback sizing | Full peak capacity |
| 17 | Retry policy | Retry timeouts; never retry 4xx |
| 18 | Circuit breaker | Stop hammering a failing model |
| 19 | Breaker state | closed -> open -> half-open |
| 20 | Utilization target | <= 0.6 |
| 21 | Canary for platform changes | Gate per component |
| 22 | Prompt registry | Versioned, owned, gated |
| 23 | Prompt metadata | owner, intent, risk tier, changelog |
| 24 | Prompt rollout | 0/5/25/100 with rollback |
| 25 | Typed variables | Prevent unfilled placeholders |
| 26 | Guardrails as a service | No per-product reimplementation |
| 27 | Product override | Tighten, never silently disable |
| 28 | Tool registry | schema, owner, auth model, side-effect class |
| 29 | Side-effect classes | read / reversible_write / irreversible_write |
| 30 | Approval by class | Irreversible requires approval |
| 31 | Tool observability | Hooks for latency and errors |
| 32 | Eval as a service | run / regression / compare |
| 33 | Platform suites | generic, safety, cost/latency, multilingual |
| 34 | Product suites | Registered per product |
| 35 | Tenant cache namespacing | Cross-tenant leak prevention |
| 36 | Retrieval isolation | Pre-filter inside the index |
| 37 | Quotas | requests/day, tokens/min, concurrent, cost |
| 38 | Fair queueing | Weighted, so one tenant cannot starve another |
| 39 | Denial-of-wallet | Per-user caps and anomaly alerts |
| 40 | Cost attribution | tenant, team, feature, route, model version |
| 41 | Reconciliation | Meter vs invoice within 2% |
| 42 | Platform SLIs | availability, latency, throughput, quality, cost, freshness |
| 43 | Change failure rate | Rollback rate, canary breach rate |
| 44 | Effectiveness SLI | Time to first success for a new team |
| 45 | Adoption is a product | Build onboarding like a product |
| 46 | Quickstart | One command to a working call |
| 47 | Playground | Teams evaluate for themselves |
| 48 | Templates | RAG, agent, extraction starting points |
| 49 | Path to production | Gate + canary + monitoring documented |
| 50 | Anti-pattern | Raw model endpoints only |
| 51 | Anti-pattern | One giant prompt |
| 52 | Anti-pattern | No evaluation gate |
| 53 | Anti-pattern | Unnamespaced shared cache |
| 54 | Anti-pattern | Platform owns all reliability |
| 55 | Anti-pattern | No cost attribution |
| 56 | Anti-pattern | Silent breaking changes |
| 57 | Anti-pattern | Over-gating |
| 58 | Anti-pattern | Golden path only, no escape hatch |
| 59 | Anti-pattern | Platform as a monolith |
| 60 | Build order | telemetry -> routing -> prompts -> guardrails -> eval |
| 61 | Resist early | Vector database, developer portal |
| 62 | Extension points | Documented, validated custom tools/prompts/scorers |
| 63 | Governance: models | Approved models per region and data class |
| 64 | Governance: data | Residency, retention, lineage |
| 65 | Governance: access | RBAC to models, indexes, tools, dashboards |
| 66 | Governance: change | Who approves, against which gate |
| 67 | Governance: cost | Chargeback with a trusted dashboard |
| 68 | Shadow deployment | Measured with zero user risk |
| 69 | Model deprecation | Ladder off the old version with gates |
| 70 | Chaos testing | Kill replicas; measure isolation |

## Self-Check

55+ = solid, 45-54 = redo Exercises 4 and 12, below that reread THEORY 2-9.