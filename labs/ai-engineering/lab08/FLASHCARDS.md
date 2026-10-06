# Lab 08: AI Observability — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Observability stack | Traces, metrics, logs, evals, cost |
| 2 | Traces | One request, reconstructed |
| 3 | Metrics | Aggregates; cheap enough to alert on |
| 4 | Logs | Structured events, retained |
| 5 | Evals | Quality judgements; sampled, most valuable |
| 6 | Not substitutes | Latency says nothing about quality |
| 7 | Trace contents | intent, retrieval, prompt, generation, guardrails, tools, cost, outcome |
| 8 | Hash payloads | Never inline prompts or completions |
| 9 | Record versions | Attribution for regressions |
| 10 | Record scores | See how close retrieval was to failing |
| 11 | trace_id everywhere | Correlation and cost attribution |
| 12 | Cardinality | Bounded label sets only |
| 13 | Forbidden labels | request id, raw query, user id |
| 14 | High-cardinality in traces | Traces are built for it |
| 15 | TTFT | Prefill-dominated; perceived latency |
| 16 | TPOT | Decode-dominated; reading speed |
| 17 | Throughput | tokens/s, requests/s |
| 18 | Error classes | Upstream, guardrail fail-closed, OOM, timeout |
| 19 | Batch size distribution | Not just the average |
| 20 | Cache hit rate | Prefix and semantic, separately |
| 21 | Preemption rate | Overload indicator |
| 22 | Cost per request | By tenant, feature, route, version |
| 23 | Cost per outcome | cost / success_rate |
| 24 | Token split | Input vs output tells you which lever |
| 25 | Reconciliation | Meter vs invoice within 2% |
| 26 | 100% cheap signals | Schema, refusal, length, PII, citation |
| 27 | Sampled judging | Quality, with a budget |
| 28 | Random stratum | The unbiased metric |
| 29 | Error stratum | The fix queue |
| 30 | Escalation stratum | High-severity items |
| 31 | Disagreement stratum | Silent failures |
| 32 | Never mix strata | The average describes nothing |
| 33 | PSI | Distribution shift over bins |
| 34 | PSI thresholds | 0.10 / 0.25 |
| 35 | Quantile bins | Better for skewed inputs |
| 36 | Drift triggers | Investigation, not rollback |
| 37 | Quality triggers | Rollback |
| 38 | Retry ratio | attempts / requests |
| 39 | Retry storm | > 1.2 sustained |
| 40 | Alert: TTFT | Traffic, context, cache |
| 41 | Alert: quality | Manifest diff first |
| 42 | Alert: refusal | Policy or guardrail change |
| 43 | Alert: cost | Retry, cache miss, context growth |
| 44 | Alert: cache | Deploy bug signal |
| 45 | Alert: injection | Channel and tenant |
| 46 | Alert ownership | Named team |
| 47 | First question | Per alert type, pre-written |
| 48 | Runbook | Tested containment |
| 49 | Guardrail attribution | Which layer caught it |
| 50 | Exemplar traces | Worst, fastest, most common failure |
| 51 | PII scrub at write | Before persistence |
| 52 | Retention by class | Traces, logs, audit, prompts |
| 53 | Audit immutability | Hash chain or external sink |
| 54 | Tenant deletion | Enforced, with a metric |
| 55 | Observability cost | Spans + metrics + evals |
| 56 | Sampling plan | Budget-fit with CI width preserved |
| 57 | Hierarchical baselines | Per-tenant without masking |
| 58 | Seasonal baselines | Residual scoring |
| 59 | Offline/online gap | Compare judged vs proxy |
| 60 | Business metrics | The layer that makes others actionable |

## Self-Check

55+ = solid, 45-54 = redo Exercises 2 and 9, below that reread THEORY 2-8.