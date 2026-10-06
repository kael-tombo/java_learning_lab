# Lab 10: AI Deployment & CI/CD — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Deploy | Mechanical artifact movement |
| 2 | Release | A decision with an owner |
| 3 | Release artifact | Model + prompt + index + tools + policy + config |
| 4 | Manifest hash | sha256 over canonical bundle |
| 5 | Hash in responses | Instant attribution |
| 6 | Immutable artifacts | Never overwrite a published version |
| 7 | Aliases | Stable pointers: production, canary |
| 8 | Warm pool | Previous version hot for instant rollback |
| 9 | Rollback = config flip | Not a rebuild |
| 10 | Rollback target | < 5 minutes |
| 11 | Expand/contract | Old artifact reads the new schema |
| 12 | Backward compatibility | A rollback requirement, not a nicety |
| 13 | Side effects | Not undone by release rollback |
| 14 | Action-level gates | Approvals and idempotency |
| 15 | Shadow | Mirror traffic, do not serve |
| 16 | Canary ladder | 1 / 5 / 25 / 100 |
| 17 | Blue-green | 0 or 100, instant flip |
| 18 | A/B | 50/50 by user, for a decision |
| 19 | Assign by user | Session consistency |
| 20 | Salt per experiment | Cross-experiment randomization |
| 21 | Missing metric | Counts as a breach |
| 22 | Automatic rollback | No human decision under pressure |
| 23 | Min sample per step | Do not decide on 40 requests |
| 24 | CI commit | Lint, unit, fast eval (~2 min) |
| 25 | CI merge | Full eval, safety, budgets (~30 min) |
| 26 | Build | Immutable artifact + provenance + model card |
| 27 | Stage | Deploy and shadow production traffic |
| 28 | Canary | Gated steps |
| 29 | Release | Alias flip, monitor, rollback ready |
| 30 | Post | Continuous eval, drift, drills |
| 31 | Content-addressed artifacts | Cacheable, verifiable |
| 32 | Provenance | Base SHA, adapter checksum, dataset hash |
| 33 | Model card | Capabilities, SLOs, cost, eval summary |
| 34 | Env parity | Model, prompt, index, config, instrumentation |
| 35 | Shadow catches parity bugs | Real distributions |
| 36 | Feature flags | Independent kill switches |
| 37 | Blast radius | Bounded by flag scope |
| 38 | Flag expiry | Stale flags are debt |
| 39 | Flag audit | Guardrail disabling requires approval |
| 40 | Replicas formula | `peak_rps / (service_rate * utilization)` |
| 41 | Utilization target | <= 0.6 |
| 42 | Scale on queue depth | Leading indicator |
| 43 | Cold-start guard | GPU start time in minutes |
| 44 | Admission control | 429 over unbounded queueing |
| 45 | Logical model names | Products decoupled from models |
| 46 | Health-aware routing | Breakers and fallback |
| 47 | Never retry 4xx | Malformed requests fail identically |
| 48 | Deprecation ladder | Gates per step |
| 49 | Auto-pin | Safety net for un-migrated callers |
| 50 | Drain before decommission | Finish in-flight work |
| 51 | Served batch quality | Numerics differ from offline batch 1 |
| 52 | Build-invariance test | Offline eval at the served batch |
| 53 | Safety gate | Zero tolerance |
| 54 | Quality gate | Per category, with a tolerance |
| 55 | Latency gate | p95 budget |
| 56 | Cost gate | Per request or per correct outcome |
| 57 | Instrumentation gate | Missing spans block |
| 58 | Canary of a stage | Isolate a component change |
| 59 | Game day | Rehearse the rollback |
| 60 | Post-mortem | The write-up is the prevention |

## Self-Check

55+ = solid, 45-54 = redo Exercises 5 and 16, below that reread THEORY 1-8.