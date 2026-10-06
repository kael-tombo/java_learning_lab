# Lab 09: AI Security — Flashcards

| # | Front | Back |
|-------|-------|------|
| 1 | Jailbreak | User persuasion to bypass policy |
| 2 | Prompt injection | Instructions smuggled through untrusted content |
| 3 | Injection is worse | The app supplies the channel |
| 4 | Real boundaries | Capability control, data isolation, verified computation |
| 5 | Defence in depth | Layers that raise attacker cost |
| 6 | Prompt is not a boundary | Bypassable; treat as a layer |
| 7 | Classifier is not a boundary | Probabilistic; a layer |
| 8 | Regex is not a boundary | Cheap pre-filter only |
| 9 | NFKC | Unicode normalization against lookalikes |
| 10 | Zero-width chars | Hide text from human reviewers |
| 11 | Bidi controls | Direction spoofing during review |
| 12 | Decode-and-classify | Classify base64/hex/ROT13/URL decodings too |
| 13 | Depth limit | Bound recursive decoding |
| 14 | Quote, do not delete | Preserve evidence; avoid a side channel |
| 15 | Length caps | Cost and attack surface |
| 16 | Rate limits | Abuse and enumeration |
| 17 | Token bucket | Smooth bursts |
| 18 | Privilege separation | Capability from code |
| 19 | Model cannot self-authorize | Narration is data |
| 20 | Read-only roles | No write tools registered |
| 21 | Tool allowlist | No shell, no generic SQL, no arbitrary HTTP |
| 22 | Strict schemas | `additionalProperties:false`, enums, patterns |
| 23 | Validate in code | Not only provider-side |
| 24 | Approval scope | Bound to normalized arguments |
| 25 | Approval expiry | Stale approvals are vulnerabilities |
| 26 | Timeout denies | Fail closed on absent approval |
| 27 | Side-effect caps | Writes per task |
| 28 | Idempotency key | Retries cannot duplicate writes |
| 29 | Circuit breaker | Protect fragile tools |
| 30 | Result sanitization | Tools return references, not secrets |
| 31 | Output guardrails | Schema, refusal, grounding, PII, policy |
| 32 | Fail closed | Exception or uncertainty blocks |
| 33 | PII scrub at write | Logs are a compliance surface |
| 34 | Retention by class | Minimise exposure window |
| 35 | Canary | Detect system-prompt leakage |
| 36 | Canary at volume | Probabilities compound |
| 37 | Tenant-scoped cache | Tenant + authz in the key |
| 38 | Pre-filter isolation | Unauthorized content never ranks |
| 39 | Cross-tenant test | Randomized, in CI |
| 40 | Data classification | Governs models and retention |
| 41 | Encryption | Transit and at rest |
| 42 | DLP | Exports and logs |
| 43 | Supply chain | Models, datasets, adapters as dependencies |
| 44 | Pin by SHA | A floating tag can change silently |
| 45 | Adapter checksums | Verify before serving |
| 46 | Dataset scanning | Poisoning and PII at ingest |
| 47 | Prompt review | Third-party prompts are code |
| 48 | Refusal rate | On disallowed prompts; want high |
| 49 | Over-refusal rate | On benign lookalikes; want low |
| 50 | Category thresholds | Security research differs from self-harm |
| 51 | Harmed-party priority | Self-harm needs urgency and referral |
| 52 | Red team | Adversarial testing by people trying to break it |
| 53 | Threat model first | Know what you protect |
| 54 | Attack families | Encoding, framing, collision, exfil, multi-turn, multimodal |
| 55 | Mutation operators | Systematic attack generation |
| 56 | Finding to test | Every bypass becomes permanent coverage |
| 57 | Safe mode | Strict policy, tools off, previous version pinned |
| 58 | Containment | Disable tool, revoke creds, scope tenant |
| 59 | Time to detect | Measured in drills |
| 60 | Time to contain | Measured in drills |
| 61 | Blast radius | Feature flags and scoped capability |
| 62 | New-surface review | New data source or tool re-threat-models |
| 63 | Authorship matters | Insider leakage is real |
| 64 | Export controls | DLP on data export |
| 65 | Retention deletion | Job with a metric |
| 66 | Index freshness as risk | Stale content is still served |
| 67 | Cached poison | Ingest-time scanning and dedupe |
| 68 | Adversarial examples | Train on found attacks |
| 69 | Over-correction check | Adversarial fine-tuning hurts benign accuracy |
| 70 | Security as process | A finding without a test is not a fix |

## Self-Check

55+ = solid, 45-54 = redo Exercises 5 and 7, below that reread THEORY 1-8.