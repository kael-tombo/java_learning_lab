# Lab 03: Prompt Engineering Patterns — Mini Project

## Project: Production Prompt Library with Gating, Versioning, and Evaluation

Build the prompt system a production service actually needs: typed templates,
versioned registry, boundary-stratified few-shot selection, robust structured-output
parsing with repair and fallback, self-consistency, a validation-gated optimizer, and
injection defense — with measurements for each claim.

## Goal

A library where every prompt is versioned, gated, measured, and rollback-able, with
numbers behind claims like "few-shot helps" and "delimiters reduce injection
compliance".

## Requirements

### Phase 1: Template Layer
- [ ] `PromptTemplate` with `{{var}}` substitution; throws on missing variables.
- [ ] `VariableSchema` with declared types (STRING n, ENUM, INT, BOOL) and validation.
- [ ] `PromptBuilder` enforcing canonical section order; no duplicate sections.
- [ ] `assertNoUnfilled` at render time.
- [ ] Unit tests: missing variable, wrong type, extra variable, out-of-order section.

### Phase 2: Prompt Registry
- [ ] Immutable versions, owner, risk tier, changelog, template hash.
- [ ] `promote` requires a passing gate result.
- [ ] `rollback` is a single call and warms the render cache.
- [ ] Render cache keyed by `sha256(name + version + rendered)`; invalidated on change.

### Phase 3: Few-Shot Selection
- [ ] Boundary-stratified selector: coverage of all labels first, then hard/easy mix.
- [ ] Seeded; final shuffle to neutralize position order.
- [ ] Measure accuracy variance across 5 seeds.
- [ ] Compare boundary-selected vs random-selected at matched k.

### Phase 4: Structured Output
- [ ] Schema-driven parser with escape-aware balanced-JSON extraction.
- [ ] Validation per field (range, enum, length).
- [ ] Bounded repair loop (1-2 attempts) with typed error context.
- [ ] Deterministic rule-based fallback flagged `usedFallback=true`.
- [ ] Test on 20 fixtures including truncation, trailing prose, nested objects,
      escaped quotes.

### Phase 5: Reasoning Patterns
- [ ] Self-consistency with k samples, majority vote, agreement rate reported.
- [ ] Chain-of-verification: atomic claims checked against evidence.
- [ ] Decomposed prompting with typed planner/solver/combiner for a numeric task.

### Phase 6: Prompt Optimizer
- [ ] Six mutation operators; hill-climbing with patience.
- [ ] Held-out validation set not used for tuning decisions.
- [ ] Re-run across 3 seeds; report the spread.
- [ ] Guard against length-driven wins: report tokens/correct alongside accuracy.

### Phase 7: Injection Defense
- [ ] `InjectionDetector` with role markers, base64/hex/ROT13 decoding, depth limit.
- [ ] `UntrustedRenderer` with markers and a data-labelling note.
- [ ] 8 attack fixtures; compliance measured with and without markers.

### Phase 8: Budget Management
- [ ] Token-budget enforcement: truncate context first, never schema or question.
- [ ] Report what was dropped.
- [ ] Prefix-stable split verified across 100 renders.

### Phase 9: Harness
- [ ] JSONL task set: 120 items across 5 intents with gold labels.
- [ ] Runner producing per-intent accuracy, tokens/correct, repair rate,
      fallback rate, agreement rate.
- [ ] A/B comparison between two prompt versions with paired analysis.

## Directory Layout

```
lab03/
  src/com/genai/lab03/{template,fewshot,parse,chain,optimize,security}/
  tasks/items.jsonl
  out/reports/eval.json
  out/reports/ab.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — template layer with all four validation tests passing.
2. **M2** — registry; promotion blocked on a failing gate; rollback verified.
3. **M3** — few-shot selection; boundary beats random at matched k.
4. **M4** — parser passes 20 fixtures; repair and fallback exercised.
5. **M5** — self-consistency agreement rates; CoV flags unsupported claims.
6. **M6** — optimizer improves validation score; seed spread reported.
7. **M7** — injection fixtures caught; marker effectiveness measured.
8. **M8** — budget enforcement never drops schema or question.
9. **M9** — 120-item harness; per-intent report produced.
10. **M10** — A/B run between two prompt versions with paired analysis.

## Acceptance Criteria

- [ ] Missing variables fail to render (never emit literal `{{var}}`).
- [ ] Rollback restores the previous version in one call.
- [ ] Boundary-selected demos beat random at matched k on at least 3 of 5 intents.
- [ ] Parser handles all 20 fixtures including escaped quotes and trailing prose.
- [ ] Repair loop bounded at 2 attempts; fallback always available.
- [ ] Optimizer gain holds across 3 seeds.
- [ ] All 8 injection fixtures flagged.
- [ ] Marker wrapping measurably reduces compliance rate.
- [ ] Schema and question survive every truncation.
- [ ] Per-intent report includes tokens/correct, not just accuracy.

## Stretch Goals

- [ ] Prompt compiler: detect duplicate or contradictory instructions.
- [ ] Automatic demo-set pruning by marginal contribution.
- [ ] Per-intent prompt specialization with a router.
- [ ] Token-level diff between prompt versions with an impact estimate.
- [ ] Adversarial task set (prompt injection, format traps, ambiguity).
- [ ] Latency per prompt length bucket.
- [ ] A prompt linter in CI: ordering, unfilled vars, banned phrases.
- [ ] Multi-model comparison: does the optimal prompt differ by model?

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Literal `{{var}}` in output | Substitution left placeholders instead of throwing |
| Cache always missing | Volatile content inside the prefix |
| Few-shot hurts accuracy | Demonstrations sampled randomly, not at boundaries |
| A/B shows a win that vanishes | Single ordering; position variance not averaged |
| Parse fails on valid JSON | Naive brace regex instead of escape-aware scanner |
| Repair loop infinite | No max attempts |
| Optimizer wins by being longer | Accuracy reported without tokens/correct |
| Injection not detected | Only literal patterns; no decoding step |
| Truncation removed the schema | Wrong truncation priority |

## Definition of Done

`REPORT.md` contains: the prompt anatomy diagram, the template/registry design, the
boundary-vs-random few-shot comparison, the parser fixture results, the self-consistency
agreement analysis, the optimizer trajectory with seed spread, the injection matrix with
and without markers, the budget enforcement results, the 120-item per-intent report,
the A/B result with paired analysis, and a "which prompt decisions we would not make
again" section.