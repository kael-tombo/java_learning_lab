# Lab 04: AI Agent Frameworks — Theory

## 1. The Agent Loop

A framework is four things: a **tool registry**, a **policy** (the LLM), a **parser**
(model text -> structured action), and a **runtime** (the loop plus budgets).

```
goal -> [ think -> select tool -> validate args -> execute -> observe ]* -> final
```

The framework's job is to make each of those predictable: typed tools, validated
arguments, bounded iterations, and a structured trace.

## 2. Agent Taxonomy

| Type | Control flow | Determinism | Use when |
|------|-------------|--------------|----------|
| Single-shot call | None | High | One well-specified task |
| Chain | Written | High | Fixed sequence of steps |
| Workflow | Written, with LLM steps | High | Known process, fuzzy sub-steps |
| Router | Written dispatch | High | Classification into a known set |
| ReAct agent | Model-chosen | Low | Open-ended, unknown step count |
| Multi-agent | Model + orchestration | Low | Decomposable specialist work |

**Default to the top of this table.** Use a model-chosen loop only when the step count
is genuinely unknown, and wrap it in hard budgets.

## 3. Tool Design

```json
{
  "name": "getOrderStatus",
  "description": "Look up fulfillment status. Use when the user asks about shipping or delivery.",
  "input_schema": {
    "type": "object",
    "properties": { "orderId": { "type": "string", "pattern": "^A-[0-9]{4}$" } },
    "required": ["orderId"],
    "additionalProperties": false
  }
}
```

Rules that separate a usable tool from a liability:
- **Narrow**. `getOrderStatus(id)` beats `queryDatabase(sql)`.
- **Idempotent** where possible, so retries are safe.
- **Errors as data**: `{"error": "ORDER_NOT_FOUND"}`, never a thrown exception or a
  stack trace. The policy must be able to recover.
- **Fast**. A 30-second tool destroys the loop budget.
- **Described with examples**, including when *not* to use it.
- **Typed and validated in code** before dispatch, not only by the provider.

## 4. Parsing Model Output

Providers offer structured tool calls, but a robust parser must handle, in order:
1. Provider-native structured call.
2. Fenced JSON block.
3. Bare JSON after an `Action:` marker.
4. Mini-language `Action: name(k="v")`.
5. Fail closed: treat unparseable output as a final answer with raw text.

Bound the parsed action count to one per turn; more is a bug signal, not flexibility.

## 5. Budgets and Termination

Every loop needs a stop for each resource:

```
maxSteps, maxTokens, maxToolCalls, maxWallClockMs, maxCostUsd, maxSideEffects
```

Plus behavioural stops: repeated `(tool, args)` detection, identical observations, and
no-progress detection. An agent without termination guarantees will find them
eventually.

## 6. Memory

| Type | Contents | Lifetime |
|------|----------|----------|
| Working | messages, tool results, counters | One task |
| Episodic | past trajectories | Weeks; used for few-shot and self-improvement |
| Semantic | durable facts in a vector store | Persistent |
| Scratchpad | free-form notes between steps | One task |

Prune tool results aggressively. A 50-step loop carrying 2 KB of raw JSON per
observation exhausts the context and degrades decisions. Keep the last few verbatim,
summarize the rest, and never drop a result the final answer cites.

## 7. Planning

| Strategy | Extra cost | Use when |
|----------|-------------|----------|
| Reactive (ReAct only) | None | Short tasks, obvious tool |
| Plan-then-act | 1 call | >3 dependent steps |
| Decomposed | 1 planning + n solving | Independent subtasks |
| Hierarchical | Coordinator + workers | Large decomposable goals |
| Tree/beam over plans | Exponential | Search-like problems with backtracking |

Map plan steps to typed records so stages compose as ordinary Java methods, and require
any deviation from the plan to be logged with a one-line justification.

## 8. Multi-Agent Orchestration

```
SUPERVISOR
   routes to specialists, then synthesizes
   +-- Researcher   tools: search, fetch
   +-- Analyst      tools: compute, stats
   +-- Writer       tools: none
   +-- Verifier     tools: none
```

Other patterns:
- **Sequential pipeline**: fixed stages, typed handoffs. Fully deterministic; prefer it.
- **Parallel fan-out + vote**: k independent workers, aggregate. Self-consistency for
  agents.
- **Debate**: two agents critique each other. Expensive, and correlated errors mean the
  benefit is often overstated.
- **Hierarchical**: supervisor -> sub-supervisors -> workers.

Cost multiplies: supervisor calls plus every specialist call. Measure **tokens per
completed task**, not per call.

## 9. Guardrails Inside the Agent

- Tool allowlist per agent role; no ambient shell, filesystem, or arbitrary HTTP.
- Pattern validation on arguments (blocks `A-1001'; DROP TABLE`).
- Approval gate on irreversible tools, with argument-scoped approvals and a timeout
  that denies.
- Side-effect caps per task.
- Tool output treated as untrusted data in the next prompt.
- Read-only agents get no write tools at all.

## 10. Observability and Evaluation

Trace every turn: `{step, thought, tool, args, result, latency, tokens, finishReason}`.
Without this, a non-deterministic system can only be guessed about.

Metrics:
- **Task success rate**.
- **Step efficiency**: correct steps / total steps.
- **Tool-call precision and recall**.
- **Recovery rate**: success after a tool error.
- **Cost and p95 latency per task**.
- **Trajectory regression tests**: assert tool sequences, ignore wording.

## 11. Framework Anatomy in Java

```
ToolRegistry      register/find/schemas/scoped view
Tool              record(name, description, schema, reversible, handler)
ArgValidator      hand-written schema enforcement
ActionParser      5 strategies, fail closed
AgentConfig       all budgets and flags
Agent             the loop
Memory            working memory + pruning
LoopDetector      normalized (tool,args) repetition
TraceEmitter      JSONL spans
ApprovalGate      CompletableFuture with timeout -> deny
```

## Key Equations

```
P(task success) = prod_i p_i                  (n independent steps)
E[steps]        = n / p                        (p = per-step success)
E[attempts]     = 1/(1-p_retry)
tokens_per_task = sum_i (in_i * p_in + out_i * p_out)
step_efficiency = correct_steps / total_steps
```