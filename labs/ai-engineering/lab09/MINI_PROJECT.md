# Lab 09: AI Security — Mini Project

## Project: Security Harness with Layered Guardrails and a Red-Team Suite

Build a security harness in Java 21 — sanitization, recursive decoding, injection
detection, privilege separation, a tool gate, a fail-closed output pipeline, PII
scrubbing, tenant isolation, audit logging — plus a red-team suite with per-layer
attribution.

## Goal

A harness where 100+ attack cases across 8 families are executed against 5 defense
layers, every failure is attributed to the layer that missed it, and every finding
becomes a permanent test.

## Requirements

### Phase 1: Input Layer
- [ ] NFKC normalization, invisible and bidi character stripping, length caps.
- [ ] Recursive decode (base64, hex, ROT13, URL) with a depth bound and cycle guard.
- [ ] Token-bucket rate limiter per tenant.
- [ ] 12 attack signatures; 100+ fixtures; measured detection per family.

### Phase 2: Mutation Engine
- [ ] 8 mutation operators (encoding, framing, collision, many-shot, role spoof,
      code comment, split, hypothetical).
- [ ] Apply to 20 base prompts; measure compliance per operator per defense layer.

### Phase 3: Boundary
- [ ] `TrustedRenderer` with markers and data labels.
- [ ] Measure compliance with and without markers; report both numbers.
- [ ] Indirect injection set: 40 documents with embedded instructions.

### Phase 4: Tool Layer
- [ ] Scoped registries (read-only, support, admin).
- [ ] `ToolGate` with the seven ordered checks.
- [ ] Arg-scoped approvals with expiry and timeout-denies.
- [ ] Side-effect caps; idempotency keys.
- [ ] 100 injected documents/args: zero unauthorized calls.

### Phase 5: Output Layer
- [ ] Eight stages, each PASS/BLOCK/FAIL_CLOSED; exceptions block.
- [ ] PII scrub with re-scan verification; zero residual.
- [ ] Grounding verification; citation validation.
- [ ] A stage made deliberately to throw, proving fail-closed.

### Phase 6: Isolation
- [ ] Tenant-scoped caches; leak test fails without scoping.
- [ ] Retrieval namespaces with pre-filtering; unauthorized query returns zero.
- [ ] 1,000 randomized cross-tenant tests.

### Phase 7: Audit and Supply Chain
- [ ] Hash-chained audit log with external anchors; tamper detection verified.
- [ ] Provenance verification: pinned base SHA, adapter checksum, dataset hash.

### Phase 8: Abuse Detection
- [ ] Burst, repeated-input, argument-probing, denial-of-wallet detectors.
- [ ] Throttle-not-block policy; escalation for exfiltration attempts.

### Phase 9: Metrics and Suite
- [ ] Refusal and over-refusal per category with thresholds.
- [ ] Canaries over 1,000 requests.
- [ ] Per-layer attribution histogram with the uncaught count.
- [ ] Every finding converted into a permanent regression test.
- [ ] Suite runner exits non-zero on any violation.

### Phase 10: Safe Mode
- [ ] Strict policy, tools off, no retrieval, previous version pinned.
- [ ] Verified graceful degradation (still answers).

## Directory Layout

```
lab09/
  src/com/aiengineering/lab09/{input,context,tools,output,safety,audit,supply,abuse,mode,suite}/
  attacks/direct.jsonl
  attacks/indirect.jsonl
  attacks/multiturn.jsonl
  out/attack_matrix.txt
  out/attribution.json
  out/audit.log
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — sanitizer and decode detector; all encoding variants caught.
2. **M2** — injection detector; 100% on the internal suite.
3. **M3** — mutation engine; compliance measured per operator.
4. **M4** — boundary layer; marker effectiveness quantified.
5. **M5** — tool gate; 100 injections, zero unauthorized calls.
6. **M6** — output pipeline; deliberate exception blocks.
7. **M7** — PII scrub; zero residual on re-scan.
8. **M8** — isolation tests; 1,000 randomized cross-tenant tests green.
9. **M9** — audit chain tamper-detected; provenance verified.
10. **M10** — canary over 1,000 requests; zero leakage.
11. **M11** — attribution histogram; weakest layer identified.
12. **M12** — safe-mode drill; full suite green.

## Acceptance Criteria

- [ ] 100% detection on the internal attack suite.
- [ ] Indirect injection caught in 40/40 documents.
- [ ] Zero unauthorized tool calls across injected documents and args.
- [ ] Stage exception blocks (fail closed verified).
- [ ] PII scrub leaves zero residual matches.
- [ ] Cross-tenant leak test fails when scoping is removed.
- [ ] Canary never appears in 1,000 outputs.
- [ ] Audit chain tamper detected; anchor catches a full rewrite.
- [ ] Refusal and over-refusal reported as a pair with a chosen operating point.
- [ ] Attribution sums correctly with the uncaught count published.
- [ ] Every finding is a permanent regression test.
- [ ] Reverting a fix causes a suite failure.

## Stretch Goals

- [ ] Adversarial fine-tuning reducing attack success rate.
- [ ] Constitutional critic (5 principles) vs single classifier.
- [ ] Representation probe separating compliant from refusing responses.
- [ ] Multi-turn stateful accumulation detector.
- [ ] Rate-limit enumeration detection.
- [ ] Secret rotation drill measuring propagation time.
- [ ] Poisoned-corpus detection at ingest.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Attack succeeds despite guardrails | Relying on prompts rather than code |
| Handler invoked with invalid args | Validation after dispatch, or missing patterns |
| Legit questions refused after tuning | Over-refusal not measured |
| Stage exception returns content | try/catch that logs and continues |
| Cross-tenant hit | Cache key missing tenant/authz |
| Canary found in one run | Spot check instead of a volume test |
| Audit passes after edit | Chain not recomputed, or no external anchor |
| Attribution blames the model | No per-layer instrumentation |
| Benign user blocked | Hard block instead of throttle |
| Suite passes on a broken agent | No break-on-purpose test |

## Definition of Done

`REPORT.md` contains: the threat model grid, the layer architecture, the mutation matrix
(operator x layer), the marker effectiveness numbers, the tool gate order with results,
the output pipeline with the fail-closed proof, the PII results, the isolation test
counts, the audit tamper and anchor results, the canary results over 1,000 requests, the
refusal/over-refusal frontier with the chosen operating point, the per-layer attribution
with the uncaught list, the safe-mode drill, and a list of residual risks accepted with
reasons.