# Lab 04: AI Agent Frameworks — Math Foundation

## 1. Task Success as a Product

With `n` steps of per-step success probability `p` (independent):

```
P(task success) = p^n
```

For a 5-step task: `p=0.95 -> 0.774`, `p=0.98 -> 0.904`, `p=0.99 -> 0.951`. **A
"reliable" 95%-per-step agent is only 77% reliable over five steps.** This is why
per-step reliability and recovery engineering matter more than a better prompt.

## 2. Expected Steps

```
E[steps to success] = n / p
```

At `n = 5, p = 0.9`: `5.56` steps, and 56% of runs exceed the plan. Any budget set at
exactly `n` will truncate a large fraction of runs.

## 3. Expected Cost

```
cost(task) = sum_{i=1..S} [ in_tokens_i * p_in + out_tokens_i * p_out ]
```

With growing context (`in_i ≈ C0 + i*o`) and constant output `u`:

```
total_in  = S*C0 + o*S(S-1)/2        ~ O(S^2)
total_out = S*u                       ~ O(S)
```

For `S = 20, C0 = 1200, o = 300`: `total_in = 24,000 + 57,000 = 81,000` tokens. Context
growth dominates agent cost quadratically — the quantitative reason pruning is not
optional.

## 4. Latency

```
T_task = sum_i ( T_model_i + T_tool_i )
```

Sequential tools sum. Parallel fan-out changes the bound to `max_i` at unchanged token
cost:

```
T_fanout = max_i T_tool_i   vs   T_seq = sum_i T_tool_i
cost_fanout = sum_i cost_i   (unchanged)
```

For three 2-second tools: sequential 6 s, fan-out 2 s, same tokens. Fan-out is free
latency when tools are independent — which is exactly when it is safe.

## 5. Step Efficiency

```
step_efficiency = correct_steps / total_steps
```

A useful acceptance bar is `> 0.7` for a 5-8 step task. Below 0.5 the problem is the tool
set or the descriptions, not the model's reasoning: the model cannot select correctly
from tools it does not understand.

## 6. Tool Selection as Classification

```
tool_precision = correct_tool_calls / all_tool_calls
tool_recall    = correct_tool_calls / required_tool_calls
```

Recall is the informative one. Precision can look perfect while the agent never calls
the tool it needed — the failure mode where it hallucinates an answer instead of
retrieving.

## 7. Recovery Rate

```
recovery = successful_tasks_with_errors / tasks_with_errors
```

Recovery separates two very different failures: "the model cannot plan" versus "the
plumbing gave it no way to recover". A low recovery rate with a high precision points
at error surfacing (tools returning opaque failures), which is a code fix, not a prompt
fix.

## 8. Retry Amplification

```
E[attempts] = 1 / (1 - p_retry)
```

`p = 0.2 -> 1.25x`, `p = 0.5 -> 2x`. Under saturation, timeouts raise `p_retry`,
creating a feedback loop. Cap retries, add jitter, and stop retrying a tool whose
circuit breaker is open.

## 9. Multi-Agent Cost

For a supervisor with `m` specialists each called `k` times:

```
calls = 1 (routing) + m*k (specialists) + 1 (synthesis)
tokens_total = sum of all calls' tokens
```

With `m = 4, k = 2`: `10` calls versus a single-agent `6`-call trajectory. Multi-agent
roughly doubles cost for the same task, which is only justified when specialists measurably
outperform one generalist.

## 10. Fan-Out Vote Accuracy

With `k` workers of accuracy `a` and independent errors (odd `k`, binary task):

```
P(vote correct) = sum_{j=(k+1)/2}^{k} C(k,j) a^j (1-a)^{k-1...}
```

`a=0.6`: `k=3 -> 0.648`, `k=5 -> 0.682`, `k=9 -> 0.710`. Sublinear gains.

If errors are correlated with correlation coefficient `rho`, the effective independent
sample size falls toward `k * (1-rho^2) / (1 + rho^2)`, and the benefit shrinks
proportionally. **Agreement rate is the honest diagnostic**: high agreement plus a wrong
answer means a shared blind spot.

## 11. Budget Sizing

Given an expected step count `E = n/p` and a hard truncation fraction target `alpha`:

```
maxSteps = ceil( E / (1 - alpha) )
```

For `n = 5, p = 0.9` (`E = 5.56`) and `alpha = 0.05`: `maxSteps = ceil(5.85) = 6`. Note
that 6 steps truncates ~10% of runs; if truncation is unacceptable, either raise `p`
(recovery engineering) or accept the tail and log it.

## 12. Token Budget Allocation

```
in_tokens_i = C0 + sum_{j<i} o_j     with pruning keeping sum_{j<i} o_j <= P
```

Choose `P` (history budget) from the marginal value: past observations matter most
recently, so a budget that keeps the last `k` steps verbatim and summarizes the rest
beats one that keeps everything up to a cap. Empirically `k = 3-5`.

## 13. Approval Economics

Irreversible actions cost `C_wrong` when they should not have happened:

```
expected_cost(action) = C_wrong * (1 - approval_catch_rate)
```

If `C_wrong = $500` (a bad refund) and the approval process catches 95%: `$25`
expected. Halving the approval rate to 50% raises it to `$250`. **The approval gate is
cheap insurance whose value scales with the cost of the mistake**, which is why the
gate matters for `refund` and barely for `lookup`.

## 14. Side-Effect Caps

With `n_writes` writes per task and a per-write risk `r`:

```
E[blast radius] = n_writes * r
```

Capping writes at 3 with `r = 0.2` bounds expected damage at 0.6 units regardless of how
the agent loops. Caps are the cheapest containment available.

## 15. Variance Across Runs

With `R` runs of the same task, per-run quality `q_i`:

```
mean = (1/R) sum q_i
sd   = sqrt( (1/(R-1)) sum (q_i - mean)^2 )
sem  = sd / sqrt(R)
```

An agent framework decision requires the **sem to be small relative to the effect being
claimed**. With `sd = 0.15` (typical for agents), distinguishing a 5-point improvement
needs `R >= (1.96*0.15/0.05)^2 = 35` runs. Reporting a single run proves nothing.

## Worked Numbers

Support triage task, 5 tool calls typical, `p = 0.92`.

- `P(success) = 0.92^5 = 0.659`. Less than two-thirds.
- `E[steps] = 5/0.92 = 5.43`.
- `maxSteps` for `alpha = 0.05`: `ceil(5.43/0.95) = 6`.
- Tokens: `C0 = 1200` (system + 6 tool schemas), `o = 400`, `u = 120`, `S = 5`:
  `total_in = 5*1200 + 400*10 = 20,000`; `total_out = 600`.
- At `$3/M` in, `$15/M` out: cost `$0.060 + $0.009 = $0.069` per task.
- With pruning keeping 2 steps verbatim (`P = 400`): `total_in = 6,000 + 400 = 6,400`;
  cost `$0.0282` — a **59% reduction from pruning alone**.
- Fan-out k=3 on the ambiguous 30%: `+3` specialist calls worst case, `+9%` cost,
  latency for those cases cut from `3*T` to `T`.
- Supervisor with 4 specialists, 2 calls each: 10 calls versus 5 — roughly 2x cost for a
  measured quality gain, if any.

Conclusion: prune history first, set `maxSteps` from `E/(1-alpha)`, and only reach for
multi-agent when a measurement shows the generalist is the bottleneck.

## Self-Check Questions

1. Compute `P(success)` for a 7-step task at `p = 0.97`.
2. Derive `maxSteps` for `n = 6, p = 0.85, alpha = 0.02`.
3. Compute expected agent cost at `S = 30`, `C0 = 2000`, `o = 200`, `u = 100`.
4. Show how `rho = 0.8` error correlation changes the effective fan-out sample size.
5. Compute `E[blast radius]` for `n_writes = 8` with a cap of 3 and `r = 0.25`.