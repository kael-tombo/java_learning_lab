# Lab 05: LLM Agent Frameworks — Vision

## The ReAct Loop

```
                    +---------------------------+
   goal  ---------> |  build prompt:            |
                    |  system + tools + history  |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |  LLM call (tokens, latency)|
                    +-------------+-------------+
                                  |
                    +-------------+-------------+
                    |  ActionParser (5 strats)   |
                    +--+------------+---------+--+
                       |            |         |
              +--------+     +------+-----+   +----------+
              |              |            |               |
              v              v            v               v
        +----------+   +-------------+  +--------+   +-------------+
        | FINAL    |   | ToolCall    |  | Bad    |   | approval    |
        | answer   |   | dispatch    |  | action |   | required    |
        +----+-----+   +------+------+  +---+----+   +------+------+
             |               |              |               |
             |        +------v-------+      |        +------v------+
             |        | validate args|      |        | COMPLETION  |
             |        | allowlist?   |      |        | STAGE       |
             |        +------+-------+      |        +-------------+
             |               |              |
             |        +------v-------+      |
             |        | handler    |      |
             |        | (idempotent|      |
             |        |  where pos) |     |
             |        +------+-----+      |
             |               |             |
             |        +------v-------------v--+
             |        |  append Observation    |
             |        |  (truncate/summarize)  |
             |        +----------+-------------+
             |                   |
             +---------+---------+
                       |  loop while budgets remain
                       v
        steps < max  ?  no -> AgentResult(exhausted, budgetKind)
                    |
                    +-- budget checks: steps, tokens, wall clock,
                        loop detection, observed tool-error count
```

## Agent Anatomy

```
+-----------------------------------------------------------------------+
|  AGENT                                                                |
|                                                                       |
|  +-----------------+     +--------------------------------------+    |
|  |  POLICY (LLM)   |<--->|  MEMORY                               |    |
|  |  - decides next  |     |  - system prompt                     |    |
|  |    action       |     |  - goal                              |    |
|  |  - sees tools   |     |  - assistant turns                  |    |
|  |    + history    |     |  - observations (pruned)            |    |
|  +--------+--------+     |  - budget counters                  |    |
|           |              +--------------------------------------+    |
|           | action                                                  |
|           v                                                         |
|  +-----------------+     +--------------------------------------+    |
|  |  TOOL REGISTRY  |     |  BUDGETS                            |    |
|  |  name/sdesc/    |     |  maxSteps | maxTokens | maxWall   |    |
|  |  schema/handler |     |  maxCost  | loopWindow| maxWrites |    |
|  |  reversible?    |     +--------------------------------------+    |
|  |  scoped per role|                                                  |
|  +--------+--------+                                                  |
|           | result                                                       |
|           +--------------------> back into MEMORY                      |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |  TRACE: step, thought, tool, argsHash, resultHash, latency, tok  |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

## Prompt Assembly Order

```
+---------------------------------------------------+
| SYSTEM: role, rules, budget reminder              |  stable -> cached
| TOOLS: JSON schemas (20 tools = 1200 tokens)      |  stable -> cached
+------------------- PREFIX BOUNDARY ----------------+
| ASSISTANT: Thought: I need the order status...    |  volatile
| OBSERVATION: {"status":"shipped","eta":"..."}     |  volatile, pruned when old
| ASSISTANT: Action: getOrderStatus(orderId="A-1")  |  volatile
| OBSERVATION: ...                                  |  volatile
+------------------- PREFIX BOUNDARY ----------------+
| USER GOAL repeated as a reminder                  |  last = highest attention
+---------------------------------------------------+

everything above the FIRST boundary is cacheable across steps of one run
and across runs with the same tool set
```

## Parse Strategies Priority

```
raw model output
   |
   +-- 1. native structured tool call  (provider format)   -> ToolCall
   +-- 2. ```json fenced block                             -> ToolCall
   +-- 3. "Action: name(k=v, k2="v2")" mini-language       -> ToolCall   <-- check BEFORE 4
   +-- 4. "Action: {json}" bare JSON after marker           -> ToolCall
   +-- 5. natural language, no action markers              -> FinalAnswer
   |
   +-- anything else / parse error                          -> BadAction (fail closed)
```

## Observation Pruning Visual

```
steps 1..12, observation = 400 tokens each, cap = 3000 tokens

keep verbatim: last 3
summarize: steps 1..9  ->  "tool=getOrder status=ok keys=status,eta"  (~15 tok)

before prune:  12 * 400            = 4,800 tokens  (over cap)
after prune:   3*400 + 9*15        = 1,335 tokens  (fits)

drop order when still over cap:
  1. oldest SUMMARY first  (keeps recent evidence intact)
  2. then oldest observation
  3. NEVER drop the system prompt or the goal reminder
```

## Budget Exhaustion Ladder

```
step 1  ok
step 2  ok
step 3  ERROR:TOOL_FAILURE:TimeoutException
step 4  recovery -> ok
step 5  same tool + same args as step 3  -> loop detector fires
        observation: "change approach or answer now"
step 6  Final Answer

failure modes, in order of frequency:
  maxSteps exhausted        (agent never terminates)
  maxTokens exhausted       (observations too verbose)
  wall clock exhausted      (one slow tool)
  maxCost exhausted         (fan-out too wide)
  loop detector fired 5x    (stuck, no progress)
```

## Agent vs Workflow Decision

```
task: "refund eligibility decision"
  |
  +-- steps known?  policy rules known?
  |      |
  |     YES -> WORKFLOW:  Java code decides, LLM extracts fields
  |            deterministic | testable | cost-capped
  |
  |     NO  -> AGENT:      model chooses tools
  |            flexible | expensive | non-deterministic
  |
  +-- default: workflow. escalate to agent only with a budget + trace.

failure mode to avoid: an agent wrapping a deterministic process,
adding cost, variance and debug surface for zero capability gain
```

## Multi-Agent Supervisor Pattern

```
        +----------------------+
        |  SUPERVISOR          |  routes, then synthesizes
        +----------+-----------+
                   |
     +-------------+-------------+-------------+
     |             |             |             |
  +--v-----+   +---v-----+   +---v-----+   +---v------+
  |Research|   | Analyst |   | Writer  |   | Verifier |
  | tools: |   | tools:  |   | tools:  |   | tools:   |
  | search,|   | calc,   |   | (none)  |   | (none)   |
  | fetch  |   | stats   |   |         |   |         |
  +---+----+   +---+----+   +---+----+   +---+------+
      |             |             |             |
      +---- note ----+---- note ---+---- note ----+
                   |
        +----------v-----------+
        |  SYNTHESIZED ANSWER  |
        |  + verifier verdict  |
        +----------------------+

cost = supervisor(1..n routing + 1 synthesis) + sum(specialists)
NOTE: each specialist MUST get a scoped registry, not the full one
```

## Safety Boundaries

```
input (untrusted: user text, retrieved docs, tool output)
   |
   v
+--------------------------+
| SANITIZE / VALIDATE      |  length caps, encoding normalization,
| delimit, label as DATA   |  injection heuristics
+-----------+--------------+
            |
            v
+--------------------------+
| POLICY (system message)  |  never built by concatenating input
| TOOL SCHEMAS             |  allowlist only
+-----------+--------------+
            |
            v
   model action
            |
   +--------+---------+-------------------+
   |                  |                   |
   v                  v                   v
 validate         allowlist?         irreversible?
 args               |                   |
   |            no -> UNKNOWN      no approval -> APPROVAL_REQUIRED
   v                  |                   |
 handler ---------->+-------yes-----------+
   |
   | error -> ERROR:CODE observation (recoverable, never throws)
   v
 sanitize OUTPUT (PII scrub, length cap) -> return

NOTE: no shell tool. no ambient filesystem. no unbounded loop.
```

## Self-Check

- [ ] Tool errors return data, never throw.
- [ ] Every tool call passes schema validation before dispatch.
- [ ] Budgets cover steps, tokens, wall clock, and cost.
- [ ] Observations pruned oldest-summary-first.
- [ ] Irreversible tools gated on approval with timeout -> deny.
- [ ] Trajectory regression suite asserted on every change.