# Lab 08: AI Observability — Theory

## 1. The Observability Stack

```
  TRACES      one request, end to end, with every decision recorded
  METRICS     aggregated numbers over time, cheap enough to alert on
  LOGS        structured events, retained, searchable
  EVALS       quality judgements, sampled, the slowest but most valuable signal
  COST        the same trace carrying a dollar figure
```

Traces explain a single request. Metrics tell you something is wrong. Evals tell you
whether it is wrong in a way users notice. **All four are needed**, and they are not
substitutes: a latency alert tells you nothing about quality, and a quality score tells
you nothing about which endpoint degraded.

## 2. What Must Be in a Trace

```
trace_id, user/tenant, feature
  intent classification (confidence)
  retrieval: index version, chunk ids, scores, rerank margins
  prompt: template id + version, rendered hash, token count
  generation: model version, sampling params, TTFT, TPOT, tokens
  guardrails: input findings, output verdict, stage attribution
  tools: calls, arg hashes, result hashes, approvals
  cost: per-line breakdown
  outcome: citations valid, abstained, user signal
```

Rules:
- **Hash long payloads**, never inline them. Logs are a liability (PII).
- **Record versions**, so a regression is attributable.
- **Record scores**, so you can see *how close* retrieval was to failing.
- Every line carries `trace_id` and tenant for cost attribution.

## 3. Metrics Taxonomy

**Serving**: TTFT, TPOT, throughput, error rate by class, queue depth, batch size
distribution, cache hit rate, preemption rate.

**Cost**: input/output token split, $/request, $/feature, $/tenant, $/successful
outcome, cache savings, retry amplification.

**Quality** (sampled): task correctness, faithfulness, citation validity, abstention,
refusal and over-refusal, win rate vs baseline.

**Drift**: intent mix, query length, language, retrieval top-score distribution,
refusal rate, tool-error rate.

**Business**: task completion rate, time-to-resolution, deflection rate, revenue per
request, escalation rate.

The business layer is what makes the others actionable. "Accuracy 0.82" is a fact;
"accuracy 0.82 correlates with a 3% support cost increase" is a decision.

## 4. Sampling Strategy for Online Scoring

You cannot afford to judge 100% of traffic:

```
100% of responses:  cheap signals (schema, refusal, length, PII, citation present)
sampled:            judge-based quality
  - stratified random  -> the unbiased headline metric
  - all errors         -> the fix queue
  - all escalations    -> high-severity items
  - signal disagreement-> silent failures
```

**Never average the strata together.** The mix would describe nothing. Report the random
sample as quality and the targeted samples as "problems found".

## 5. Cost Attribution

```
cost_per_request = in_tokens*p_in + out_tokens*p_out + embed_calls*p_emb
                 + rerank_calls*p_rr + gpu_ms*p_gpu
```

Attribute by: tenant, feature, route/tier, model version, prompt version, cache status,
agent vs direct. Reconcile monthly against the provider invoice; a discrepancy above 2%
means the meter is wrong and every optimization number derived from it is suspect.

The most useful derived metric:

```
cost_per_successful_outcome = cost_per_request / success_rate
```

A 5-point quality drop doubles the bill per outcome. Cost and quality are the same
conversation, and observability is what connects them.

## 6. Drift Detection

```
PSI = sum_i (p_i - q_i) * ln(p_i / q_i)
PSI < 0.10 stable | 0.10-0.25 investigate | > 0.25 major shift
```

Watch: intent mix, query length, language, retrieval top-score, refusal rate. Drift
alerts trigger **investigation**, not automatic rollback. Quality regression triggers
rollback. Conflating them produces alert fatigue.

## 7. Alert Design

| Alert | Signal | Action |
|-------|--------|--------|
| TTFT p95 breach | Latency | Check traffic, context length, cache |
| Quality drop | Sampled eval | **First: diff the release manifest** |
| Refusal spike | Refusal rate | Policy or guardrail change? |
| Cost spike | $/request | Retry loop, cache miss, context growth |
| Cache hit collapse | Hit rate | Deploy bug: volatile content in the prefix |
| Injection attempt | Guardrail findings | Which channel? which tenant? |
| Drift | PSI | Investigate; review the eval set |
| Error rate | By class | Upstream, guardrail fail-closed, OOM |

Every alert needs: an owner, a first question, a runbook link, and a tested
containment action. An unowned alert does not get fixed.

## 8. Retention and Privacy

- Traces: sampled retention with a long tail; never full retention for 100% of traffic.
- Logs: PII scrubbed at write; retention per data classification.
- Prompts and completions: hash by default, store content only for flagged or sampled
  cases with a documented purpose.
- Audit logs (policy decisions, guardrail verdicts): longer retention, tamper-evident,
  externally stored.
- Tenant-deletable on request; retention enforced by a job with a metric.

## 9. Cost of Observability

```
obs_cost = traces * price_per_span + metrics * cardinality + eval * judge_calls
```

Cardinality is the usual blowup: **never label a metric with a request id or a full
query string.** Use bounded label sets (intent, route, model version, cache status).
High-cardinality detail belongs in traces, not metrics.

## 10. Failure Modes

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Metric with request id | Metrics backend explodes | Cardinality mistake | Bounded labels; detail in traces |
| PII in logs | Compliance incident | No scrub at write | Scrub before persist |
| Cost unexplained | Bill 3x | Untagged calls | Mandatory attribution fields |
| Alert fatigue | Alerts ignored | Noisy thresholds, no owners | SLOs, owners, runbooks |
| Quality drop undiagnosed | Weeks lost | No manifest diff | Version everything; diff first |
| Retries invisible | Load spike unexplained | No attempt counter | Trace attempt count |
| Cost blind to quality | Team ships bad cheap | Separate dashboards | Cost per outcome metric |
| Drift ignored | Suite goes stale | Drift alert has no action | Link drift to eval refresh |
| Trace missing a stage | Incomplete picture | Instrumentation gaps | Stage span as a launch requirement |

## Key Equations

```
cost_per_request = in_tok*p_in + out_tok*p_out + emb*p_emb + rr*p_rr + gpu_ms*p_gpu
cost_per_outcome = cost_per_request / success_rate
sample_rate_for_quality = eval_budget / (judge_cost_per_item * n_strata)
PSI = sum (p_i - q_i) ln(p_i/q_i)
attribution(i) = failures_first_detected_at_layer_i / total_failures
```