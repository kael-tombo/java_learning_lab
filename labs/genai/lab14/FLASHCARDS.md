# Lab 14: LLMOps (LLM Operations) — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | LLM artifact | Model + prompt + index + tools + policy |
| 2 | Most incidents trace to | Prompt, index, tools, or policy (not weights) |
| 3 | Nondeterminism | Same config, different output; logs must include params |
| 4 | Contested correctness | Needs a rubric, not an accuracy number |
| 5 | Iteration asymmetry | Prompt in minutes, model in weeks |
| 6 | Release manifest | All component versions in one object |
| 7 | Manifest fields | model, prompt, index, toolRegistry, policy, generation, evaluator |
| 8 | Release hash | sha256 over canonical manifest serialization |
| 9 | Hash in every response | Enables instant attribution |
| 10 | Canonical serialization | Field order independent of hash |
| 11 | Everything is a release | Prompt and index edits are releases |
| 12 | Shadow deployment | Mirror traffic, do not serve responses |
| 13 | Canary ladder | 1% -> 10% -> 50% -> 100% |
| 14 | Blue-green | 0% or 100%, instant flip |
| 15 | Assign by user | One version per session |
| 16 | Stable bucketing | hash(userId) -> bucket |
| 17 | Gate per step | Automated metrics, not human eyeballing |
| 18 | Min sample per step | Prevent deciding on noise |
| 19 | Auto rollback | On breach, without a human decision |
| 20 | TTFT | Time to first token; prefill dominated |
| 21 | TPOT | Inter-token latency; decode dominated |
| 22 | Throughput | Tokens/s and requests/s |
| 23 | Error classes | Upstream, guardrail fail-closed, OOM, timeout |
| 24 | Cost per request | Per feature, per tenant, per model version |
| 25 | Cost per outcome | Cost / fraction achieving the goal |
| 26 | Input/output split | Tells you which optimization applies |
| 27 | Cache hit rate | Prefix and semantic, separately |
| 28 | Cost spike as signal | Retry loop, cache miss, context growth, runaway agent |
| 29 | Quality metrics | Correctness, faithfulness, citation validity, abstention |
| 30 | Safety metrics | Refusal and over-refusal together |
| 31 | Drift inputs | Intent mix, length, language, retrieval top-score, refusal rate |
| 32 | PSI | Population Stability Index over binned distributions |
| 33 | PSI thresholds | <0.1 stable, >0.25 investigate |
| 34 | 100% coverage signals | Schema validity, refusal, length, PII |
| 35 | Judged sample | Stratified random for an unbiased estimate |
| 36 | Targeted samples | All errors, all escalations, signal disagreements |
| 37 | Never mix samples | Biases the headline metric |
| 38 | Trace spans | request, retrieval, prompt, generation, guardrails, tools, cost, outcome |
| 39 | Hash payloads | Prompts may contain PII |
| 40 | Trace is the repro | Reproduce incidents from traces |
| 41 | Feedback signals | thumbs, regenerate, copy, abandon, escalate, correction |
| 42 | Implicit corrections | Labeled preference pairs at scale |
| 43 | Review queue | Prioritize by user value x severity |
| 44 | Support tickets | Real pain plus gold answers from humans |
| 45 | Freeze during incident | No releases while investigating |
| 46 | One change at a time | Otherwise attribution is impossible |
| 47 | Component version diff | First question for a quality drop |
| 48 | Safe mode | Strict policy, tools off, no retrieval, previous version pinned |
| 49 | Containment menu | Safe mode, disable tool, disable retrieval, roll back, shed load |
| 50 | Time to diagnose | Measured in drills |
| 51 | Load shedding | Shed batch first, then long contexts |
| 52 | Protect interactive | Shedding order matters |
| 53 | Runbook first question | Per alert type, pre-written |
| 54 | Runbook quality | Owner, decision tree, tested action |
| 55 | Toil analysis | Classify operational work by automation level |
| 56 | Eval set drift | Does the eval set still represent traffic? |
| 57 | Blast radius | Bounded slice + kill switches |
| 58 | Feature flags | Independent kill switches |
| 59 | Model deprecation | Traffic shift with quality gates per step |
| 60 | Multi-model scheduling | By cost and quality, respecting headroom |
| 61 | Retry storm | Amplification before the bill arrives |
| 62 | Cache collapse alert | Early indicator of a key or deployment bug |
| 63 | Budget per release | Release notes include cost impact |
| 64 | Owner per alert | Unowned alerts do not get fixed |
| 65 | SLOs | TTFT, TPOT, cost/request, quality floor |
| 66 | Error budget | Burn rate drives release freeze |
| 67 | Deploy vs release | Deploy is mechanical; release is a decision |
| 68 | Game day | Rehearse the runbook before you need it |
| 69 | Post-incident review | The write-up is the prevention |
| 70 | North star | Cost per successful outcome with quality held |

## Self-Check

55+ = solid, 45-54 = redo Exercises 5 and 11, below that reread THEORY 2-7.