# Lab 05: LLM Agent Frameworks — Math Foundation

## 1. Expected Step Count

If each step succeeds independently with probability `p`, the expected number of
steps to complete a task is `1/p`. For a 5-step task with per-step success 0.9:

```
E[steps] = 5 / 0.9 = 5.56
```

and the probability of completing without any failure is `0.9^5 = 0.590` — so a
"reliable" 90%-per-step agent is only 59% reliable over five steps. This is why
per-step reliability and recovery matter more than raw per-step accuracy.

## 2. Reliability of an n-Step Agent

```
P(success | n steps, per-step p) = p^n
```

Doubling reliability per step (0.95 -> 0.99) over 10 steps moves end-to-end success
from 0.599 to 0.904. Engineering effort belongs there, not in the prompt.

## 3. Cost Model

```
cost(task) = sum_{i=1..S} [ in_tokens_i * p_in + out_tokens_i * p_out ]
```

With context growth: `in_tokens_i = C0 + sum_{j<i} obs_tokens_j`. For constant
observation size `o`, `in_tokens_i ~ O(i)`, so total input tokens are `O(S^2)`:

```
total_in_tokens = sum_i (C0 + i*o) = S*C0 + o*S(S-1)/2
```

An S=20-step loop at o=300 tokens ingests ~57,000 tokens of history. This is the
quantitative reason observation pruning (Exercise 7) matters.

## 4. Latency

```
T_task = sum_i ( T_model_i + T_tool_i )  +  T_plan
```

With sequential tools and no overlap, latency is the *sum*. Parallel fan-out turns
`max_i` into the bound instead of `sum_i`, at the cost of `sum` tokens:

```
T_fanout = max_i T_tool_i   vs   T_seq = sum_i T_tool_i
cost_fanout = sum_i cost_i  (unchanged)
```

A vote of k agents costs kx and saves (k-1) x the slowest tool time.

## 5. Step Efficiency

```
step_efficiency = correct_steps / total_steps
```

A useful acceptance bar: > 0.7 for a 5-8 step task. Below 0.5 means the tool set or
descriptions are wrong, not that the model is weak.

## 6. Tool Selection Accuracy

Treat tool choice as classification over the registry:

```
tool_precision = correct_tool_calls / all_tool_calls
tool_recall    = correct_tool_calls / tool_calls_required_by_task
```

Recall is the informative one — precision can look perfect while the agent never
calls the tool it needs.

## 7. Recovery Rate

```
recovery = successful_tasks_containing_an_error / tasks_containing_an_error
```

Recovery is the single most informative agent metric: it separates "the model
cannot plan" from "the plumbing gives it no way to recover".

## 8. Multi-Agent Fan-Out Variance

With k independent workers of accuracy `a` and independent errors, majority vote
correctness for odd k (binary task) follows the binomial tail:

```
P(vote correct) = sum_{j=(k+1)/2}^{k} C(k,j) a^j (1-a)^{k-j}
```

For `a = 0.6`, k = 3: `3*0.36*0.4 + 0.216 = 0.648`. k = 5: `0.682`. Gains flatten
past k=5 — the classic diminishing return of self-consistency (Lab 03).

If errors are *correlated* (same prompt, same model), the binomial assumption
overstates the benefit: agreement rate is the honest diagnostic.

## 9. Majority Vote with Agreement

```
agreement = max_class_count / k
```

High agreement + wrong answer usually means **systematic** error (bad tool schema,
missing data, wrong prompt). Low agreement + right answer means luck. Track both.

## 10. Utility with Cost and Risk

Score a trajectory:

```
U(task) = value_correct * 1 - lambda_cost * cost_normalized - mu_risk * irreversible_actions
```

Risk weight `mu_risk` must be large enough that one unapproved refund outweighs a
100% success bonus. Make it a hard gate instead: `refund` without approval -> reject.

## 11. Context Budget Allocation

For S steps, allocate the budget `B`:

```
reserve_for_latest = c * o          (last c steps verbatim)
summarize_older    = s_1..s_{S-c} summarized to <= s_max tokens each
B >= C0 + (S-c)*s_max + c*o
```

If that fails, reduce `S` (the budget on steps) rather than dropping summaries —
losing history breaks reasoning; losing steps just makes the agent less thorough.

## 12. Decision Threshold vs Budget

Doubling `maxSteps` roughly doubles worst-case cost. Set `maxSteps` from the task's
*known* decomposition depth plus slack, e.g. `3 * expectedSteps`, and rely on loop
detection rather than a huge ceiling.

## Worked Numbers

Task: refund eligibility, 4 tool calls typical, p = 0.92 per step.

- `P(success) = 0.92^4 = 0.716`.
- Expected steps to success at `E = 4/0.92 = 4.35`.
- `o = 400` observation tokens, `C0 = 1200` (system + 6 tool schemas), S = 5:
  `total_in = 5*1200 + 400*(5*4/2) = 6000 + 4000 = 10,000` tokens.
- At $3/M in, $15/M out with ~120 out tokens per step (600 out total):
  cost `= 0.03 + 0.009 = $0.039` per task.
- With k=3 fan-out for the ambiguous cases only (~30% of traffic): `+9%` cost.

## Self-Check Questions

1. Compute `P(success)` for a 7-step task at per-step 0.95.
2. Show `total_in_tokens` is `O(S^2)` under constant observation size.
3. Why does correlated error make voting less useful than the binomial predicts?
4. Choose `maxSteps` for an expected 4-step task with a hard requirement of < 20
   steps. Justify with cost, not vibes.