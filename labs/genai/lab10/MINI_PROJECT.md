# Lab 10: LLM Safety & Alignment — Mini Project

## Project: Layered Safety Harness for an LLM Application

Build a complete guardrail stack in Java 21 around a stub LLM: input sanitization,
system-boundary rendering, tool gate with approvals, an eight-stage output pipeline,
attack generation and mutation, and a suite runner with per-layer attribution.

## Goal

A harness where 100+ attack cases across 12 families are executed against 5 defense
layers, every failure attributed to the layer that missed it, every finding turned
into a permanent test, and refusal and over-refusal reported as a pair.

## Requirements

### Phase 1: Input Layer
- [ ] NFKC normalization, zero-width and bidi stripping, control-character removal.
- [ ] Length cap in tokens; token-bucket rate limiter.
- [ ] Decode detector: base64, hex, ROT13; classify raw and all decoded forms.
- [ ] Findings returned as a typed list and written to the audit log.

### Phase 2: System Boundary
- [ ] `TrustedRenderer` with explicit markers and a data-labelling note.
- [ ] Policy in the system message; user text and documents in the user message.
- [ ] Measurement: `countLeakedInstructions` to quantify delimiter effectiveness.

### Phase 3: Tool Layer
- [ ] `ScopedRegistry` per role (read-only, support, admin).
- [ ] `ToolGate` with ordered checks: allowlist, read/write, schema, approval,
      side-effect cap, rate limit.
- [ ] Argument-scoped approvals with timeout -> deny.
- [ ] 3 tools: one read-only, one reversible write, one irreversible.

### Phase 4: Output Layer
- [ ] Eight stages, each `PASS`/`BLOCK`/`FAIL_CLOSED`.
- [ ] Every stage wrapped so an exception blocks.
- [ ] PII scrubber with re-scan verification.
- [ ] Grounding verifier using claim splitting.
- [ ] A stage that is deliberately made to throw, to prove fail-closed behavior.

### Phase 5: Attack Generation
- [ ] 12 mutation operators (base64, hex, rot13, leet, reverse, spaced, roleplay,
      hypothetical, manyshot, collision, fake-system, code-comment).
- [ ] Direct jailbreak set (40 prompts) and indirect injection set (40 documents).
- [ ] Multi-turn split payload set (20 conversations).
- [ ] Image-borne set (10 rendered payloads).

### Phase 6: Metrics
- [ ] Refusal rate on disallowed; over-refusal on benign lookalikes.
- [ ] Jailbreak success rate per family.
- [ ] Refusal consistency across paraphrases.
- [ ] Canary leak test over 1,000 requests.
- [ ] Per-layer attribution histogram.

### Phase 7: Regression Suite
- [ ] All cases as permanent tests with expected verdicts.
- [ ] Runner exits non-zero on any violation.
- [ ] Demonstrate a test with teeth: revert a fix and confirm failure.
- [ ] Audit log with hash chain; tampering detection verified.

### Phase 8: Safe Mode
- [ ] `SafeMode` with strict policy, tools off, no retrieval, blocking output.
- [ ] Anomaly trigger and verified graceful degradation.

## Directory Layout

```
lab10/
  src/com/genai/lab10/{input,context,tools,output,attack,audit,mode,eval}/
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

1. **M1** — sanitizer with findings; decode detector catches all encoding variants.
2. **M2** — renderer; delimiter effectiveness measured.
3. **M3** — tool gate; 100 injected documents produce zero unauthorized calls.
4. **M4** — output pipeline; deliberate exception verified to block.
5. **M5** — 110+ attack cases generated; baseline compliance measured.
6. **M6** — attribution histogram computed; weakest layer identified.
7. **M7** — fixes for the top two attribution buckets; compliance drops.
8. **M8** — refusal/over-refusal pair with a documented operating point.
9. **M9** — canary leak test over 1,000 requests; audit chain verified.
10. **M10** — safe-mode drill; full regression suite green.

## Acceptance Criteria

- [ ] 100% of unauthorized tool calls blocked across injected documents.
- [ ] Failing stage -> response blocked, never returned.
- [ ] PII scrub leaves zero residual matches on re-scan.
- [ ] Canary never appears in 1,000 outputs.
- [ ] Refusal and over-refusal both reported with a chosen operating point.
- [ ] Attribution sums to 1 across layers.
- [ ] Every attack family has a permanent regression test.
- [ ] Audit log tamper detection verified.
- [ ] A reverted fix causes a test failure.

## Stretch Goals

- [ ] Adversarial adapter training (Lab 06) reducing attack success rate.
- [ ] Constitutional critic (5 principles) vs single classifier comparison.
- [ ] Multi-turn stateful accumulation detector.
- [ ] Rate-limit enumeration detection.
- [ ] Representation probe separating compliant from refusing responses.
- [ ] Cost model: two-stage filtering vs uniform expensive filtering.
- [ ] Safe-mode auto-engage from an anomaly signal with a drill report.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Attack succeeds at L4 despite L3 | Read/write separation missing |
| Garbage decoded output in audit | Missing printability check |
| Legit questions refused after tuning | Over-refusal not measured |
| Stage exception returns content | try/catch that logs and continues |
| Canary in output only under load | Not tested at volume |
| Attribution always blames the model | No per-layer instrumentation |
| Rate limiter blocks legitimate bursts | Bucket too small or refill too slow |
| Multi-turn attack passes | Per-turn filters without accumulation |
| Audit chain verifies after edit | Chain not recomputed from sink |

## Definition of Done

`REPORT.md` contains: the layer architecture, the attack-family x layer matrix,
per-layer attribution with the weakest layer named, refusal/over-refusal frontier
with the chosen operating point, canary results, a safe-mode drill report, three
worked examples (one direct jailbreak, one indirect injection, one exfiltration
attempt) showing which layer caught each, and a list of remaining known gaps.