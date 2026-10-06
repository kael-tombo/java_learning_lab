# Lab 04: AI Agent Frameworks — Vision

## The Agent Loop

```
   goal
    |
    v
  [ check budgets: steps | tokens | toolCalls | wallClock ]   <-- ALL FOUR, every turn
    |  exhausted -> AgentResult(exhausted, whichBudget)
    v
  [ loop detector tripped? ] -> inject "change approach or answer now"
    |
    v
  [ render memory (pruned) -> prompt with tool schemas ]
    |
    v
  [ LLM call ]  (tokens, latency)
    |
    v
  [ ActionParser: native | fenced | mini-language | bare JSON | fail-closed ]
    |
    +-- FinalAnswer -> done
    |
    +-- BadAction   -> observation "ERROR:UNPARSEABLE"
    |
    +-- ToolCall
          |
          v
      [ gate order matters ]
        1. allowlist / scoped registry      -> ERROR:UNKNOWN_TOOL
        2. argument validation + pattern    -> ERROR:INVALID_ARGUMENT
        3. approval (irreversible only)     -> ERROR:APPROVAL_REQUIRED
        4. circuit breaker                  -> ERROR:CIRCUIT_OPEN
        5. execute (never throws out)       -> ERROR:TOOL_FAILURE
          |
          v
      [ append observation, prune old ones, continue ]
```

## Reliability Math

```
  5-step task, per-step success p:

  p=0.95   0.95^5 = 0.774      "high per-step accuracy"
  p=0.98   0.98^5 = 0.904
  p=0.99   0.99^5 = 0.951

  E[steps] = 5/p  ->  5.26 / 5.10 / 5.05

  maxSteps for 5% truncation = ceil(E/(1-0.05)) = ceil(5.54) = 6

  a "95% accurate" agent is 77% reliable over five steps.
  improving p and recovery beats improving the prompt.
```

## Context Growth Is Quadratic

```
  S steps, context C0 = 1200, observation o = 400, output u = 120

  total_in  = S*C0 + o*S(S-1)/2
  total_out = S*u

  S=5    in =  6,000 + 4,000  = 10,000      out =  600    cost $0.039
  S=10   in = 12,000 + 18,000 = 30,000      out = 1,200   cost $0.108
  S=20   in = 24,000 + 76,000 = 100,000     out = 2,400   cost $0.336
  S=30   in = 36,000 + 174,000= 210,000     out = 3,600   cost $0.702

  S=20 WITH pruning (keep 2 verbatim, P=400):
  S=20   in = 24,000 +    400 = 24,400      cost $0.087

  pruning alone: 3.9x cheaper.
  => context growth is a cost AND a quality problem (attention dilution).
```

## Cost of Multi-Agent

```
  single ReAct trajectory:        5 calls
  supervisor + 4 specialists x2:   1 routing + 8 specialist + 1 synthesis = 10 calls
                                  ~2x cost for the same task

  and the routing call is pure overhead: it is model work whose only
  purpose is to choose between specialists.

  fan-out vote: k=3 workers
     accuracy 0.6 -> k=1: 0.600, k=3: 0.648, k=5: 0.682
     sublinear. 3x the cost buys 5 points.

  WHY IT MAY STILL BE CORRECT: specialists with DIFFERENT tools see
  different evidence, so their errors are less correlated than k samples
  from one agent. measure agreement, not just accuracy.
```

## Multi-Agent Topology

```
SUPERVISOR (routing call)
   |
   +---> Researcher   tools: search, fetch        (read-only)
   +---> Analyst      tools: compute, stats       (read-only)
   +---> Writer       tools: none                 (read-only)
   +---> Verifier     tools: none                 (read-only)
   |                        |
   +--- synthesis call <-----+
        |
        v
   final answer + verifier verdict

  EVERY specialist gets a SCOPED registry. not a filtered dispatch.
  a researcher that can also write is a researcher one injection away
  from writing.

  SEQUENTIAL PIPELINE (usually better):
   extract -> normalize -> enrich -> classify -> respond
   typed records between stages, fully deterministic, 1 model call max
```

## Tool Design: Narrow vs Generic

```
  BAD:  runSql("SELECT * FROM orders WHERE ...")
        - model must know the schema
        - one prompt injection away from DROP TABLE
        - unbounded result size
        - untestable

  GOOD: getOrderStatus(orderId: "^A-[0-9]{4}$")
        - typed, validated, bounded
        - idempotent
        - errors as data: {"error":"ORDER_NOT_FOUND"}
        - pattern blocks "A-1001'; DROP TABLE"

  the schema is a SECURITY boundary, not documentation.
```

## Trajectory Testing

```
  scripted client: [ "getOrderStatus(...)", "FINAL: shipped" ]

  golden trajectory:  [ getOrderStatus ]

  test asserts the TOOL SEQUENCE, not the wording.
  a wording change is not a regression; a different tool order is.

  PROVE THE SUITE HAS TEETH:
    1. corrupt a tool description ("Use when..." -> "")
    2. run the suite
    3. it MUST fail
    if it still passes, the suite is not testing anything.
```

## Termination Guarantees

```
  every loop needs FOUR resource stops:
    maxSteps, maxTokens, maxWallClockMs, maxCostUsd
    (+ maxToolCalls, maxSideEffects)

  and THREE behavioural stops:
    repeated (tool,args) in the window   -> nudge
    identical observation twice          -> nudge
    no tool call for K steps             -> force an answer

  WALL CLOCK catches what the others miss:
    one tool that takes 30 s with maxSteps=10 still burns 30 s
    per-step and per-token budgets are satisfied the whole time.
```

## Failure Map

```
symptom                          | likely cause                  | fix
---------------------------------+-------------------------------+--------------------------
agent loops forever on one tool  | args not normalized in the key| normalize (tool,args)
handler exception kills the run  | tool throws past the loop     | wrap, return ERROR:CODE
"permission granted" changes     | capability read from text     | enforce in code
approvals succeed with nobody    | approval not scoped/timeouted | argument-scoped + deny
specialist writes files          | shared registry               | scoped registry per role
context explodes on long tasks   | no pruning                    | keep last k, summarize rest
run takes minutes                | no wall-clock budget          | add maxWallClockMs
answer states facts no tool saw  | no evidence ledger            | validate claims vs results
suite passes on a broken agent   | suite has no teeth            | break-on-purpose test
```

## Self-Check

- [ ] Workflow default; ReAct only for unknown step counts.
- [ ] Tools narrow, typed, idempotent, errors-as-data.
- [ ] Validation in code with patterns; scoped registries per role.
- [ ] Four resource budgets plus behavioural stops.
- [ ] Approval argument-scoped, timeout denies.
- [ ] Observations pruned; never drop a cited result.
- [ ] Claims validated against an evidence ledger.
- [ ] Trajectory suite proven to have teeth.