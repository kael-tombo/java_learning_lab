# Lab 14: LLMOps (LLM Operations) — Vision

## The Release Bundle

```
  a response is produced by FIVE versioned artifacts:

  modelId@modelVersion        Llama-3.1-8B@sha256:abc123
  promptTemplateId@version    support_system@v17
  indexVersion                corpus-2026-10-05@embed-v3@chunks-881432
  toolRegistryVersion         tools@v9   (schemas + permissions + approvals)
  policyVersion               policy@v4   (safety policy + constitution)
  generationConfig            t=0.2,p=0.95,max=800,stop=[],seed=fixed
  evaluatorVersion            judge-v5@metrics-v3

  manifestHash = sha256(canonical(manifest))

  EVERY response carries manifestHash in a header and in the trace.

  => "was this the old prompt?" becomes:
       SELECT * FROM traces WHERE prompt_version != 'v17'
     in one query, instead of an afternoon of guessing.

  MOST QUALITY INCIDENTS ARE ONE OF THESE FIVE CHANGING.
  A prompt tweak is a release. An index rebuild is a release.
  A guardrail threshold change is a release.
```

## Deployment Ladder

```
   production
   |  100%   v16 (current)
   |   |
   |   +---- 1%  ---> v17   gates: quality -2pts | safety 0 | p95 +5% | cost +5%
   |                    |     n >= 400 samples
   |                    |
   |   +---- 10% ---> v17   same gates, n >= 400
   |                    |
   |   +---- 50% ---> v17   same gates
   |                    |
   +---- 100% ------> v17
                         |
                    any breach -> AUTOMATIC rollback, no human decision

  assignment: hash(userId, salt) -> bucket
     a user sees ONE version per session (and across restarts)
     salt per experiment avoids correlated bias across experiments

  request math:
     total requests to finish = n * (1/0.01 + 1/0.10 + 1/0.50 + 1)
                             = n * 113
     n = 400  ->  45,200 requests to promote
     at 50k req/day -> 21 hours.  at 2k req/day -> 22 DAYS.
     => low-volume products MUST use shadow eval to build sample size
```

## Metrics Stack

```
  INFRASTRUCTURE (100% coverage)
    TTFT p50/p95/p99 | TPOT | throughput | queue depth
    error rate by class | timeout | retry ratio | preemption | batch size dist
                    |
                    v
  COST (100% coverage)
    $/request  $/feature  $/tenant  $/model version
    input/output token split | prefix + semantic cache hit
    $/SUCCESSFUL OUTCOME   <-- the number finance cares about
                    |
                    v
  QUALITY (100% cheap signals + sampled judging)
    cheap on every response: schema valid | refused | length | PII | cited
    judged on a sample:     correctness | faithfulness | abstention | win rate
                    |
                    v
  DRIFT (100% coverage)
    intent mix | prompt length | language | retrieval top-score | refusal rate
```

## Sampling Strategy

```
  100% of responses     -> cheap signals only (no model call, ~free)
                              |
        +---------------------+---------------------+
        |                     |                     |
   RANDOM STRATIFIED     ALL ERRORS          SIGNAL DISAGREEMENT
   (unbiased quality)     ALL ESCALATIONS     (schema valid but
                                              user disliked it)
        |                     |                     |
        v                     v                     v
   HEADLINE METRIC       FIX QUEUE             FIX QUEUE
   "how good is it"      "what is broken"     "what looks fine and isn't"

  *** NEVER AVERAGE THESE TOGETHER ***
  mixing them produces a number that describes nothing
```

## Incident Triage Decision Tree

```
  QUALITY DROP
  +-- step 1: diff the release manifests
  |     index changed?      -> corpus freshness? embedding model changed?
  |                          chunker changed? re-ingest incomplete?
  |     prompt changed?     -> pull the eval diff from CI for that version
  |     policy changed?     -> refusal thresholds moved?
  |     tools changed?      -> schema tightened? permission narrowed?
  |     model changed?      -> FULL eval, not a spot check
  |     nothing changed?    -> data drift? upstream provider change?
  |
  +-- step 2: freeze releases  (before investigating, not after)
  |
  +-- step 3: pin the previous manifest  (config flip, seconds)
  |
  +-- step 4: sample traces from the affected window; compare to a good window
  |
  +-- step 5: identify the failing COMPONENT, not just the symptom
  |
  +-- step 6: add the case to the eval suite before closing
```

## Cost Spike Triage

```
  $/request up 3x
  +-- which line?
  |     INPUT  up -> context growth (check compaction) | cache hit collapsed
  |                 | index returning more chunks | retry feeding the meter
  |     OUTPUT up -> max_tokens raised | runaway agent steps | repetition loop
  |     GPU   up -> batching regressed | precision reverted | replicas scaled down
  |
  +-- retry ratio = attempts / requests
  |     > 1.2 sustained = RETRY STORM
  |       saturation -> timeouts -> retries -> more load -> more saturation
  |       (positive feedback; catch it here, not in the invoice)
  |
  +-- cache hit rate
        collapsed after a deploy = a key or template change put volatile content
        into the cached prefix. hit rate is a DEPLOYMENT BUG DETECTOR.
```

## Drift: PSI

```
  PSI = sum (p_i - q_i) * ln(p_i/q_i)      over quantile bins

  PSI < 0.10   stable
  0.10-0.25    moderate -> investigate
  > 0.25       major shift -> freeze releases, sample, re-evaluate the eval set

  calibration (10 equal bins, 10% relative shift in one bin):
     PSI ~ delta^2/q = (0.1)^2 = 0.01
     across 10 bins uniformly shifted: ~ 10 * 0.01 = 0.1   <- at the boundary

  so a 10% uniform shift across every bucket IS a real signal.

  IMPORTANT: drift alerts trigger INVESTIGATION, not automatic rollback.
  quality regression triggers rollback. conflating them causes alarm fatigue.
```

## Rollout Sample Size

```
  to resolve a d-point change on a rate near 0.5:
     n ~ 960 / d^2

     d = 2 pts  ->  n = 240
     d = 5 pts  ->  n = 384
     d = 10 pts ->  n = 96

  "we looked at 40 responses" resolves nothing.
  a canary step with n=400 is a ~5-point gate. below that, do not promote.

  ladder total = n * 113
  low-volume products -> shadow eval to build sample size without user risk
```

## Safe Mode

```
  NORMAL                          SAFE MODE (engaged on anomaly)
  ------------------------------  ------------------------------------------
  standard policy                 strictest policy
  role-scoped tool allowlist      tools DISABLED entirely
  retrieval on                    retrieval OFF
  guardrail pipeline              block on any uncertainty
  current manifest                PINNED previous manifest
  normal latency                  degraded but ANSWERED

  sequence matters:
     1. PIN the previous manifest        <-- BEFORE changing anything
     2. flip the config
     3. audit-log the reason
     pin-first is what makes rollback a config flip instead of a rebuild
```

## Load Shedding Order

```
  traffic mix:  interactive 10% | standard 40% | batch 50%

  30% overload -> shed BATCH first (15k)

    interactive  10k   PROTECTED
    standard     40k   PROTECTED
    batch        20k ->  5k   (15k shed)
    -----------------------------
    protected: 50k of 75k = 67% of good traffic intact

  shed order:  batch -> long_context -> standard -> interactive LAST

  fixed order = predictable, testable, documented behavior
  a batch tier with no SLO is the correct shock absorber
```

## Operational Hygiene

```
  DO
  ---
  freeze releases during an incident
  reproduce from the trace
  one change at a time
  keep rollback a config flip (seconds, not minutes)
  version everything that can change a response
  bound blast radius with independent kill switches
  run the drill (untested runbooks are fiction)
  alert on cost per request with the same urgency as latency

  DON'T
  -----
  roll back blind (it hides the cause and sometimes worsens it)
  make two changes in one release
  let "just a prompt tweak" ship unversioned
  run a 20-minute rollback under pressure
  alert on drift and quality with the same action
  mix targeted and random samples into one number
  write a runbook and never execute its containment action
```

## Self-Check

- [ ] Manifest hash in every response and trace.
- [ ] Canary assigned by user, gated automatically, rolled back automatically.
- [ ] Missing metrics count as breaches.
- [ ] Cost per request alerted with latency urgency.
- [ ] Retry ratio monitored before the bill.
- [ ] Manifest diff is step 1 of quality triage.
- [ ] Releases frozen before investigation.
- [ ] Runbooks executed in drills.