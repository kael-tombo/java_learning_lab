# Lab 10: AI Deployment & CI/CD — Vision

## Deploy Is Mechanical, Release Is a Decision

```
  deploy   : move artifact -> staging.        reversible, nobody notices.
  release  : expose to users.                 the only one with a blast radius.

  bad deploys  -> rolled back before traffic.   boring.
  bad releases -> detected in production.       every AI incident I have seen.

  the artifact is not the model.

  ReleaseManifest {
    model@ver, prompt@ver, index@ver, tools@ver, policy@ver,
    genConfig, evaluator@ver
  }

  7 components. each one has shipped an incident. "we only changed the prompt"
  is a sentence I have read in a post-mortem roughly once per release cycle.
```

## The Manifest Hash Converts an Investigation Into a Log Filter

```
  manifestHash = sha256(canonical(manifest))

  with it:      grep by hash, per-version error rate, exact blast radius
  without it:   "are we on the new prompt yet?" -> 40 minutes of archaeology
                across dashboards nobody agrees on
```

## Utilization Near 1 Looks Fine On A Dashboard

```
  queueing delay  W/S = 1 / (1 - rho)

  rho   W/S        replica count for 200 rps, mu=25
  ------------------------------------------------------
  0.50  2.0x       9
  0.70  3.3x       11
  0.85  6.7x       13
  0.95  20x        9      <- "efficient"
  0.99  100x       9

  average latency at rho=0.95 looks fine.
  p95 is on fire. capacity is a latency decision.
```

## Scale on Queue Depth, Not GPU Utilization

```
  GPU utilization  = where the work IS     (lagging by one service time: 3.5 s)
  queue depth      = where the work WILL BE (leading)

  autoscale on util  -> 3.5 s late -> shed load while you scale
  autoscale on queue -> scale while the queue is still filling

  queue depth = lambda * W   (Little)
  so queue depth already encodes arrival rate AND service time. it is the whole signal.
```

## Headroom Is Idle Capacity By Construction

```
  T_recover = ceil( D * T_boot / S )      D lost replicas, S spare, boot 45 s

  S=2   rebuild 10 -> 225 s
  S=4              -> 113 s
  S=6              ->  75 s
  S=0              -> never (a single failure is total)

  "we can scale back to zero when quiet" is a resilience decision,
  not a cost decision. the arithmetic above is the receipt.
```

## The Canary Window Is Longer Than It Looks

```
  5% of 200 rps = 10 rps. detecting a 2-point quality drop at 80% power
  needs ~3,000 samples per arm -> 300 s.

  "let's watch the 5% step for two minutes"   -> decided on 1,200 samples of noise.

  gates need sample counts attached to them. a gate without n is a mood.
```

## Exposure Scales With Radius, Not With Steps

```
  ladder                     mid-ladder failure      T_full
  ---------------------------------------------------------
  1 -> 100                   100% * 5 min            10 min
  1 -> 5 -> 25 -> 100        25% * 5 min             20 min
  1 -> 5 -> 25 -> 50 -> 100  50% * 5 min             30 min

  every extra step costs release time and buys 2-4x less exposure.
  release time is cheap. exposure is not.
```

## Four Gate States, Not Two

```
  INSUFFICIENT   not enough data     -> WAIT     (not a pass)
  BREACH         data says bad        -> ROLLBACK
  PASSED         data says good       -> ADVANCE
  MISSING        no metric            -> BREACH   <- the one everyone gets wrong

  "metric absent" is not "metric good".
  an instrumentation bug otherwise silently deletes your safety gate.
```

## Rollback Must Be a Map Write

```
  rollback time == next request served by the previous manifest

  requires: previous artifact present   (retention)
            previous artifact warm      (warm pool)
            alias, not content         (pointers, not copies)
            repoint effect immediate   (no cache, no drain)
            duration tracked           (a metric with a 5 min objective)

  a rollback that needs a rebuild has an infinite tail.
  P(exposure > 20 min) with median 60 s, sigma 0.6 -> ~8%. with a rebuild -> 100%.
```

## Rollback Cannot Un-Send

```
  release-level rollback:  config flip. fine.
  action-level rollback:   impossible.

  email sent, order placed, refund issued, ticket closed.
  so irreversible actions need:
    idempotency keys, approval gates, dry-run mode, and a compensating-action path
  -- rollback discipline lives in the action layer, not only the alias.
```

## Assign Cohorts By User, Not By Request

```
  request-assigned canary:
    turn 1 -> version A      turn 2 -> version B
    the user sees two products. the eval is uninterpretable.

  user-assigned canary (hash of userId + salt, identical on every replica):
    stable, reproducible, no coordination store, no session leakage.
```

## Risk Lives Where Change Lives

```
  change type        freq/wk   impact   detect   risk = f*I/D
  --------------------------------------------------------------
  tool schema        6         20       3        40
  model swap         0.08      50       5        10
  index rebuild      2          8       4         4
  prompt wording     40         1      10         4
  retrieval top-k    3          6       6         3

  tool schema diffs outrank model swaps and deserve a required review artifact.
  this table tells you where to spend reviewer attention.
```

## Parity: Three Hard Fails

```
  model   1.0  HARD FAIL
  prompt  1.0  HARD FAIL
  index   0.8  HARD FAIL
  data    0.6
  genCfg  0.5
  secrets 0.0   (supposed to differ)

  a weighted average lets a benign gen-config mismatch buy a model mismatch.
  hard-fail the three that have caused every staging-green-prod-red incident.
```

## Shadow Mode Degrades Measurement, Never Users

```
  try  { shadow = candidate.handle(req) }
  catch { count("shadow.error") }        <- cannot fail live
  finally { compare(live, shadow) }
  return live                            <- ALWAYS

  the danger is a shadowed AGENT: a shadow path with side effects sends the same
  email twice. the comparator must be pure. this is a production incident, not a bug.
```

## Cost Per Success, Not Per Token

```
  cost_per_success = spend / successful_requests = cost_per_request / success_rate

  +$0.005/request, success 0.95 -> 0.85 :   cost per success +11.8%

  every per-token dashboard looks fine. budget on the ratio or you will
  optimize the wrong number and wonder why spend went up.
```

## Rollback Drills Compound

```
  5 manual steps at 0.90 each        -> 0.59 chance of a clean rollback
  2 documented automated steps 0.95  -> 0.90

  automating the path you depend on during an incident is the highest-value
  change you can make to rollback design. it is also arithmetic.
```

## Self-Check

- [ ] Manifest covers model, prompt, index, tools, policy, config, evaluator.
- [ ] Hash appears on every response and trace.
- [ ] Target utilization <= 0.6, justified by a tail-latency budget.
- [ ] Autoscaler reads queue depth with a boot-time lookahead.
- [ ] Spare capacity sized against a measured recovery-time objective.
- [ ] Every canary gate carries a minimum sample size.
- [ ] Missing telemetry blocks the release.
- [ ] Rollback is an alias write, measured, under 5 minutes.
- [ ] Cohorts are user-stable across replicas.
- [ ] Irreversible actions have idempotency and approval, not just release rollback.
- [ ] Budgets are cost-per-successful-request.
- [ ] Parity hard-fails on model, prompt, index.
- [ ] Rollback drill run at least once, with numbers.
