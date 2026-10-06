# Lab 05: LLM Agent Frameworks — Theory

## 1. What Makes Something an Agent

A plain LLM call maps input to output. An **agent** is a loop: the model decides
*what to do next*, an executor performs it, and the result is fed back until a
stop condition fires.

```
goal -> [ plan -> act -> observe -> reflect ]* -> answer
```

Three components:
1. **Policy** — the LLM, given the goal, history, and available tools, emits an action.
2. **Tools** — deterministic side-effecting functions the policy may call.
3. **Loop** — the control flow that alternates policy and tool execution, with
   budgets (steps, tokens, wall-clock, money).

Without the loop you have a function call. Without tools you have a chatbot.

## 2. ReAct

ReAct interleaves **Thought** and **Action** with an **Observation** after each
action:

```
Thought: I need the order status. The order tool takes an order id.
Action:  getOrderStatus(orderId="A-1001")
Observation: {"status": "shipped", "eta": "2026-10-09"}
Thought: Status is known, so I can answer.
Final Answer: Order A-1001 shipped, ETA 2026-10-09.
```

Why it works:
- **Interleaving** keeps the reasoning grounded in fresh observations instead of
  stale parametric memory.
- **Externalized reasoning** in text is inspectable and editable.
- **Observations as evidence** reduce hallucination — the model is quoting tool
  output, not recalling.

Why it costs: each step is a full model call with growing history. Latency and cost
scale with the number of steps, so step budgets are a first-class feature.

## 3. Tool Design

Tools are the agent's API surface. Properties of good tools:

- **Narrow and typed.** `getOrderStatus(orderId: string)` beats `queryDatabase(sql)`.
- **Idempotent where possible** so retries are safe.
- **Errors are informative**: return `{"error": "ORDER_NOT_FOUND"}` instead of
  throwing, so the policy can recover. Never return a stack trace to a model.
- **Cheap and bounded** — a tool that takes 30 s destroys the loop budget.
- **Descriptions include examples** of correct invocation.

Schema shape:

```json
{
  "name": "getOrderStatus",
  "description": "Look up fulfillment status for an order id. Use when the user asks about shipping.",
  "input_schema": {
    "type": "object",
    "properties": { "orderId": { "type": "string", "pattern": "^A-[0-9]{4}$" } },
    "required": ["orderId"],
    "additionalProperties": false
  }
}
```

`additionalProperties: false` and patterns are cheap defense against malformed
arguments. Enforce them in Java *before* dispatch.

## 4. Tool Registry in Java

```java
public final class ToolRegistry {
    private final Map<String, Tool> tools = new LinkedHashMap<>();
    public ToolRegistry register(Tool t) { tools.put(t.name(), t); return this; }
    public Optional<Tool> get(String name) { return Optional.ofNullable(tools.get(name)); }
    public String schemaJson() { /* JSON Schema array of all tools */ }
    public record Tool(String name, String description, Schema schema, Handler handler) {}
    public interface Handler { String apply(Map<String, Object> args) throws Exception; }
}
```

Design points: `handler` receives parsed arguments and returns a **string** (JSON
encoded result) — never an exception that escapes the loop. Tool results must be
serialized deterministically so traces are reproducible.

## 5. Parsing Model Output Robustly

Models emit mixed formats. A production parser layer should handle, in order:

1. Provider-native tool call (structured).
2. Fenced JSON block: ```` ```json {...} ``` ````.
3. Bare JSON object after an `Action:` marker.
4. A single-line `Action: name(arg=value, ...)` mini-language.
5. Fail closed: treat unparseable output as `FINAL` with the raw text.

Always bound the parsed action count to 1 per turn; more than one is a bug signal.

## 6. Planning Strategies

| Strategy | When | Cost |
|----------|------|------|
| Reactive (ReAct only) | Short tasks, tool choice obvious | Low |
| Plan-then-act | Multi-step, known decomposition | Medium: one extra planning call |
| Hierarchical | Large tasks, delegable subgoals | High: coordinator + workers |
| Plan-and-retry | Failure-prone tools | Medium |
| Tree/beam over plans | Long-horizon search | High |

Practical rule: default to ReAct; escalate to explicit planning when the goal has
more than ~3 dependent steps or when the task is deterministic enough to decompose
in code (in which case prefer code — see "workflows vs agents", section 9).

## 7. Memory

- **Working memory**: the loop state — messages, tool results, step counter.
- **Episodic memory**: past trajectories, useful for few-shot and self-improvement.
- **Semantic memory**: a vector store of durable facts (Lab 04 infrastructure).
- **Scratchpad**: free-form notes the agent can read/write between steps.

Practical: prune tool outputs aggressively. A 50-step loop with 2 KB of raw JSON
per observation will blow the context and degrade the policy. Summarize or truncate
to the fields the policy needs.

## 8. Multi-Agent Orchestration

Patterns:
- **Supervisor**: a router model dispatches to specialists, then synthesizes.
- **Sequential pipeline**: fixed stages, typed handoffs (deterministic — prefer this).
- **Parallel fan-out / vote**: run k independent workers, aggregate.
- **Debate**: two agents critique each other's drafts.
- **Hierarchical**: supervisor -> sub-supervisors -> workers.

Costs multiply: supervisor calls + every specialist call. Always measure
`tokens per completed task`, not per call.

## 9. Agents vs Workflows

The most important engineering judgment in this lab:

| | Workflow | Agent |
|---|----------|-------|
| Control flow | Written by you | Chosen by the model |
| Determinism | High | Low |
| Debuggability | Easy | Hard |
| Cost predictability | Good | Poor |
| Best for | Known processes, compliance | Open-ended tasks |

Rule of thumb: if you can write the control flow, write it. Use the model inside
that flow for the fuzzy steps. Reserve model-chosen control flow for genuinely
open-ended work, and wrap it in tight budgets.

## 10. Observability

Log every turn as a span: `{step, thought, tool, args, result, latency_ms,
tokens_in, tokens_out, finish_reason}`. Without this you cannot debug a
non-deterministic system — you can only guess. Emit a trace id, and make the whole
trajectory replayable (seed + recorded tool results).

Guardrails to log: budget exhaustion, tool errors, repeated identical actions
(a classic loop), and steps exceeding a length limit.

## 11. Safety

- Tool allowlist per agent role; no ambient filesystem or shell.
- Path/argument validation against injection (e.g. `orderId` matching `^A-\d{4}$`).
- Treat tool output as untrusted content in the next prompt (Lab 10 covers this).
- Require human approval for irreversible tools (`refund`, `delete`, `sendEmail`).
- Cap side effects per task (`maxWrites`).

## 12. Evaluation

- **Task success rate** — did the goal get accomplished?
- **Step efficiency** — successful steps / total steps.
- **Tool-call accuracy** — precision/recall of correct tool selection.
- **Recovery rate** — success after a tool error.
- **Cost and latency per task**, and p95 across runs.
- **Trajectory tests**: fixed scenarios with asserted tool sequences (regression).

## Key Equations

```
total_cost(task) = sum_steps (in_tokens_i * p_in + out_tokens_i * p_out)
p95_latency = quantile_0.95(step_latencies)
step_efficiency = correct_steps / total_steps
```