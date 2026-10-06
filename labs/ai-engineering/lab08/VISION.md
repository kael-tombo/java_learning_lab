# Lab 08: AI Observability — Vision

## The Stack

```
   traces         one request, reconstructed end to end
   metrics        aggregates; cheap enough to alert on
   logs           structured, retained, searchable
   evals          quality judgements; sampled, slowest, most valuable
   cost           the same trace carrying a dollar figure

   a latency alert tells you NOTHING about correctness.
   a quality score tells you NOTHING about which endpoint degraded.
   they answer different questions and both are required.
```

## What a Trace Must Contain

```
trace_id  tenant  feature  manifest_hash
  intent: refund (0.94)
  retrieval: index=corpus-10-05@embed-v3  hits=[c17(0.71), c3(0.68), ...]
  prompt: support.reply@v17  rendered=sha256:9f2c  tokens=1180
  generation: model=gpt-x@2026-09  t=0.2 p=0.95  TTFT=380ms TPOT=32ms  out=184
  guardrails: input=[none]  output=PASS(schema ok, pii none)
  tools: refundLookup(orderId=A-1001) 3ms  approval=none
  cost: in 0.00354  out 0.00276  rerank 0.00040  TOTAL 0.00670
  outcome: citations_valid=true  abstained=false  user_signal=positive

  WHY EACH LINE:
    manifest_hash    -> "was this the old prompt?"
    retrieval scores -> not just the hits, but how CLOSE the miss was
    rendered hash    -> reproducibility without storing PII
    approval         -> the audit trail for irreversible actions
    outcome          -> joins quality back to cost
```

## Cardinality: The Way Metrics Systems Die

```
  10 labels x 4 bounded values each  =  4^10 = 1,048,576 series   (budget blown)
   1 label  x request_id (10^6/day) =  1,000,000 series            (same damage)

  FORBIDDEN metric labels:  request_id, user_id, raw query, trace_id, chunk_id
  ALLOWED metric labels:    intent, route, model_version, cache_status, outcome

  detail belongs in TRACES, which are designed for high cardinality.
  metrics are designed for aggregation and cost scales with SERIES COUNT,
  not with sample count.
```

## Sampling: What to Score on Whom

```
  100% of responses   cheap signals, no model call
                     schema valid | refused | length | PII | citation | tool errors
  ~0.1% of responses  judged quality, stratified:
       RANDOM              -> the unbiased headline number
       ALL ERRORS          -> the fix queue
       ALL ESCALATIONS     -> high severity
       SIGNAL DISAGREEMENT -> cheap said fine, user said no

  *** averaging these produces a number that describes nothing ***
  StrataSampler.blended() throws for exactly this reason.
```

## Cost: Measure Before You Optimize

```
  one RAG request ($3/M in, $15/M out, $1/M rerank, $0.02/M embed)

  line            tokens     cost       share
  -----------------------------------------------
  input          4,200      $0.0126    ============================  50%
  output           180      $0.0027    =====                          11%
  rerank         10,000      $0.0100    ==============================  40%
  embed           1,500      $0.00003   =                              0.1%
                             ---------
                             $0.0253

  the intuitive fix ("shorter answers") is 11%.
  the non-obvious fix (rerank 50 -> 20) is 40% of the bill.
```

## Cost per Outcome Connects Cost and Quality

```
  cost_per_outcome = cost_per_request / success_rate

  success    cost/outcome   vs baseline
  --------------------------------------
  1.00       $0.0253        --
  0.95       $0.0266        +5.3%
  0.90       $0.0281       +11%
  0.82       $0.0309       +22%
  0.75       $0.0337       +33%

  a 5-point quality drop at constant cost raises the bill per outcome by 6%.
  at a constant BUDGET it also means serving fewer requests per day.

  => cost and quality alerts should share a dashboard.
     a cost spike is usually a quality or safety regression
     (retry loop, cache miss, context growth, runaway steps).
```

## Drift: Investigate, Do Not Roll Back

```
  PSI = sum (p - q) ln(p/q)

  PSI < 0.10   stable
  0.10-0.25    moderate -> investigate
  > 0.25       major    -> freeze releases, sample, re-evaluate the suite

  calibration: 10 bins shifted 10% relatively -> PSI ~ 0.10 (at the boundary)
               one rare category appearing -> PSI > 0.5 immediately

  ACTION MAPPING
    drift            -> investigate, review the eval set
    quality drop     -> ROLL BACK
    latency spike    -> rollback if correlated with a release
    cost spike       -> break down by line, check retry ratio
```

## Guardrail Attribution

```
  attacks failing at each layer (first layer to catch)

  L1 input   L2 system  L3 tools   L4 output   L5 monitor
  |____|     |____|     |____|     |____|      |____|

  caught at L1        15
  caught at L2        22
  caught at L3        48    <-- load-bearing
  caught at L4        73    <-- most of the work
  caught at L5        22
  UNCAUGHT            20    <-- the attack surface with NO defence

  the two numbers that matter most:
    detection_rate = 1 - uncaught/total
    which layer carries the system -> where to invest next
```

## Alert Design

```
  alert          owner         first question                     action
  ---------------------------------------------------------------------------------
  QUALITY_DROP   ml-quality    "Did any versioned component change?"  DIFF MANIFEST, freeze
  TTFT_P95       serving       "Did traffic or context length change?" CACHE, roll back
  COST_SPIKE     finops        "Which cost line?"                     BREAKDOWN, retry ratio
  REFUSAL_SPIKE  safety        "Was a policy change deployed?"         DIFF POLICY, roll back
  CACHE_COLLAPSE serving       "Was a template edited this week?"     inspect prefix
  RETRY_STORM    serving       "attempts/request?"                    shed load
  INJECTION      security      "which channel, which tenant?"         page, scope
  DRIFT          data          "which input dimension?"               INVESTIGATE, not rollback

  every alert: owner + first question + runbook + tested containment.
  AlertRouter throws on an unregistered type -> no unactionable alerts.
```

## Privacy and Retention

```
  span type            content stored?      TTL
  --------------------------------------------------
  trace (success)      hashes only          7 days
  trace (error)        hashes + excerpts    90 days
  logs                 scrubbed at write    30 days
  prompts/completions  on request, sampled  30 days
  audit (policy, gate) full, tamper-evident 7 years
  rendered prompt      hash only            with the trace

  scrub the SERIALIZED LINE, not individual fields:
  a field added later is then scrubbed automatically.
  retention is a job with a metric, not a policy document.
```

## Self-Check

- [ ] Traces, metrics, logs, evals, cost — all four present.
- [ ] Version info in every trace; manifest diff first in triage.
- [ ] Scores recorded, not just hits (how close the miss was).
- [ ] Bounded metric labels; high cardinality in traces only.
- [ ] Scrub on the serialized line.
- [ ] Cost breakdown sorted by share; cost per outcome tracked.
- [ ] Random and targeted strata never averaged.
- [ ] Drift investigates; quality rolls back.
- [ ] Retry ratio and cache hit rate monitored as leading signals.
- [ ] Every alert has an owner, a first question, and a tested action.