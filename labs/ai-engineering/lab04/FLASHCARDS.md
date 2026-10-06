# Lab 04: AI Agent Frameworks — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Framework | Registry + policy + parser + runtime |
| 2 | Agent | Policy + tools + loop with budgets |
| 3 | Function call vs agent | No loop versus iteration |
| 4 | Taxonomy | Call, chain, workflow, router, ReAct, multi-agent |
| 5 | Default | Workflow (written control flow) |
| 6 | Use ReAct when | Step count genuinely unknown |
| 7 | Tool description | Says when to use it, with an example |
| 8 | Narrow tools | `getOrderStatus(id)` over `runSql(sql)` |
| 9 | Generic tools | Model must guess schema; injection surface |
| 10 | Idempotent tools | Safe retries |
| 11 | Errors as data | Policy can recover |
| 12 | Never stack traces | Leaks internals, derails the model |
| 13 | Strict schemas | `required`, enums, patterns, `additionalProperties:false` |
| 14 | Validate in code | Not only provider-side |
| 15 | Parse strategies | Native, fenced, mini-language, bare JSON, fail closed |
| 16 | One action per turn | More is a bug signal |
| 17 | Unknown tool | `UNKNOWN_TOOL` observation, not an exception |
| 18 | Budgets | Steps, tokens, tool calls, wall clock, cost, side effects |
| 19 | Wall clock | Catches a single slow tool |
| 20 | Behavioural stops | Loop detection, no-progress |
| 21 | Loop detection key | Normalized `(tool, args)` |
| 22 | Loop nudge | "Change approach or answer now" |
| 23 | Working memory | Loop state for one task |
| 24 | Episodic memory | Past trajectories |
| 25 | Semantic memory | Durable facts in a store |
| 26 | Pruning rule | Keep recent; never drop a cited result |
| 27 | Planning styles | Reactive, plan-then-act, decomposed, hierarchical, tree |
| 28 | Plan-then-act | One extra planning call |
| 29 | Deviation logging | Every skip or reorder justified |
| 30 | Router | Classify then dispatch |
| 31 | Sequential pipeline | Deterministic typed handoffs |
| 32 | Fan-out + vote | Self-consistency for agents |
| 33 | Debate | Two agents critique; often correlated errors |
| 34 | Hierarchical | Supervisor -> sub-supervisors -> workers |
| 35 | Scoped registries | Specialists cannot reach other tools |
| 36 | Cost metric | Tokens/dollars per completed task |
| 37 | Step efficiency | Correct steps / total steps |
| 38 | Healthy value | > 0.7 for a 5-8 step task |
| 39 | Recovery rate | Success after a tool error |
| 40 | Tool precision/recall | Selection correctness |
| 41 | Trace fields | step, thought, tool, args, result, latency, tokens |
| 42 | Trajectory test | Assert tool sequences |
| 43 | Break-on-purpose test | Corrupt a description; suite must fail |
| 44 | Approval gate | Argument-scoped, timeout -> deny |
| 45 | Side-effect caps | Writes per task |
| 46 | Untrusted tool output | Delimit and label as data |
| 47 | Idempotency key | `(taskId, tool, normalizedArgs)` |
| 48 | Circuit breaker | Stop hammering a broken tool |
| 49 | Escalation | Hand off with partial context |
| 50 | Inject into tool output | Agents read attacker-controlled text |
| 51 | Scripted client | Deterministic agent tests |
| 52 | Script exhaustion | Signals the loop did not converge |
| 53 | Streaming | Perceived latency for plan and results |
| 54 | Checkpoint/resume | Survive crashes in long runs |
| 55 | Critic pass | Flags unsupported claims |
| 56 | Reflexion | Verbal self-feedback into the next attempt |
| 57 | No-progress detect | Identical observations twice |
| 58 | Timeout per tool | Prevents one call from eating the budget |
| 59 | Parallel safety | Read-only tools parallel; writes serialized |
| 60 | Compaction | Summarize old observations, never the goal |
| 61 | Prompt bloat | 20 tool schemas per step is a real cost line |
| 62 | Schema caching | Tools change rarely; put them early |
| 63 | Role definitions | Each agent states its goal and constraints |
| 64 | Single responsibility | Narrow agent goals beat one omnipotent agent |
| 65 | Framework portability | Keep domain logic out of the runtime |
| 66 | Eval harness | Scenario suite + golden trajectories |
| 67 | Production eval | Sample traces, score offline |
| 68 | Regression on traces | Any golden change needs review |
| 69 | Variance measurement | Agents vary; measure spread, not one run |
| 70 | Kill switch | Disable a tool or agent without a deploy |

## Self-Check

55+ = solid, 45-54 = redo Exercises 3 and 13, below that reread THEORY 2-8.