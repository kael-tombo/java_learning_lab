# Lab 05: LLM Agent Frameworks — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Agent | Policy + tools + loop with budgets |
| 2 | Function call vs agent | A single tool invocation has no loop; an agent iterates |
| 3 | ReAct | Thought -> Action -> Observation, repeated |
| 4 | ReAct benefit | Reasoning stays grounded in fresh evidence |
| 5 | ReAct cost | One model call per step; latency grows with steps |
| 6 | Observation | The tool's returned data fed back into the context |
| 7 | Trajectory | The full record of thoughts, actions, observations |
| 8 | Final answer signal | An explicit `FINAL`/`Final Answer:` action |
| 9 | Tool | Typed, bounded, idempotent-where-possible side-effecting function |
| 10 | Tool description | Includes when-to-use and an example invocation |
| 11 | Narrow tools | `getOrderStatus(id)` beats `runSql(String)` |
| 12 | Generic tools danger | Model must guess schema/arguments; high injection surface |
| 13 | Tool errors as data | Return `{"error": "CODE"}` so the policy can recover |
| 14 | Never return stack traces | Leaks internals and derails the model |
| 15 | Schema strictness | `additionalProperties: false`, enums, patterns, `required` |
| 16 | Validate before dispatch | Java-side check, not only provider-side |
| 17 | ToolRegistry | `Map<String, Tool>` plus JSON Schema emission |
| 18 | Tool handler contract | Parsed args in, serialized string out |
| 19 | Deterministic serialization | Sort keys so traces are reproducible |
| 20 | Parser strategies | Native call, fenced JSON, bare JSON, mini-language, fail-closed |
| 21 | Fenced block | ```` ```json {...} ``` ```` is common in real output |
| 22 | One action per turn | More than one is a bug signal |
| 23 | Unknown tool | Resolve to `UNKNOWN_TOOL` observation, not an exception |
| 24 | Budgets | maxSteps, maxTokens, maxWallClockMs, maxCost |
| 25 | Budget exhaustion | Report it explicitly; never fail silently |
| 26 | Loop detection | Repeated `(tool, args)` in recent history |
| 27 | Loop-breaking nudge | Inject an observation telling the model to change approach |
| 28 | Reactive agent | ReAct only; best for short tasks |
| 29 | Plan-then-act | Planner emits steps first; loop executes with justification |
| 30 | Hierarchical | Supervisor dispatches to sub-agents |
| 31 | Sequential pipeline | Fixed stages with typed handoffs; fully deterministic |
| 32 | Fan-out and vote | k workers, majority aggregate |
| 33 | Debate | Two agents critique each other |
| 34 | Agent vs workflow | Written control flow is the default; agents are the exception |
| 35 | Why workflows win | Determinism, debuggability, cost predictability |
| 36 | When to use an agent | Genuinely open-ended goals, unknown step count |
| 37 | Working memory | Loop state: messages, results, counters |
| 38 | Episodic memory | Past trajectories for few-shot or self-improvement |
| 39 | Semantic memory | Vector store of durable facts |
| 40 | Scratchpad | Free-form notes readable between steps |
| 41 | Observation pruning | Summarize old results, keep recent steps verbatim |
| 42 | Pruning rule | Never drop a result the final answer cites |
| 43 | Context growth | O(steps x observation size) without pruning |
| 44 | Multi-agent cost | Supervisor + all specialists per task |
| 45 | Cost metric | Tokens per completed task, not per call |
| 46 | Step efficiency | Correct steps / total steps |
| 47 | Recovery rate | Success after a tool error |
| 48 | Tool-call accuracy | Precision/recall of tool selection |
| 49 | Approval gate | `CompletableFuture<Approval>` with timeout -> deny |
| 50 | Irreversible tools | refund, delete, send, purchase — require approval |
| 51 | Side-effect caps | `maxWrites` per task |
| 52 | Tool allowlist | Per-role registry; no ambient shell or filesystem |
| 53 | Argument injection | Validate `orderId` against `^A-[0-9]{4}$` |
| 54 | Untrusted tool output | Delimit and label as data in the next prompt |
| 55 | Observability span | step, thought, tool, args, result, latency, tokens |
| 56 | Replayability | Seed + recorded tool results |
| 57 | Trace ids | Propagated through every span |
| 58 | Stub model in tests | Scripted responses make agent tests deterministic |
| 59 | Fixture-based parser tests | One fixture per branch plus adversarial inputs |
| 60 | Trajectory test | Assert tool-call sequence, ignore wording |
| 61 | Break-on-purpose test | Corrupt a tool description and confirm the suite fails |
| 62 | Confidence from observations | Every claim traceable to a tool result |
| 63 | Self-correction pass | Critic flags unsupported claims, then repair steps |
| 64 | Escalation | Agent hands off with a summary when stuck |
| 65 | State machine agents | Explicit states + transitions + budget per cycle |
| 66 | Reflexion | Verbal self-feedback added to the context for the next attempt |
| 67 | Retry semantics | Retry only idempotent tools; else verify state first |
| 68 | Idempotency keys | Dedupe retried side effects |
| 69 | Prompt caching in agents | Stable tool schemas first, volatile history last |
| 70 | Prompt bloat risk | 20 tools in the schema on every step is a real cost line |

## Self-Check

55+ = solid, 45-54 = redo Exercises 3 and 7, below that reread THEORY 1-9.