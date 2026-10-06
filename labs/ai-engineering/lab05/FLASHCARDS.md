# Lab 05: Prompt Engineering at Scale — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Prompt as code | Versioned, owned, tested, rollback-able |
| 2 | Registry record | id, version, hash, owner, risk tier, evals, rollout, changelog |
| 3 | Immutable versions | Edits create new versions |
| 4 | Hash-addressed | Reproducibility and cache keys |
| 5 | Owner required | Unowned prompts are unmaintained |
| 6 | Risk tiers | low / medium / high; determine required gates |
| 7 | Lifecycle | draft -> evaluated -> canary -> active -> deprecated |
| 8 | Promotion gate | Must pass the registered suite |
| 9 | Rollback | Single config call, invalidates render cache |
| 10 | Typed variables | Catch unfilled and wrong-typed values |
| 11 | assertNoUnfilled | Render-time invariant |
| 12 | Canonical order | system, instructions, context, schema, question |
| 13 | Stable/variable split | Derived from section order |
| 14 | Prefix cache dependency | Stable prefix is what makes caching work |
| 15 | Prompt families | system, tasks, guardrails, fewshot, output |
| 16 | Bundle versioning | Prevents family drift |
| 17 | A/B pairing | Identical items for both variants |
| 18 | Paired advantage | Item difficulty cancels |
| 19 | Bootstrap CI | Distribution-free interval on the delta |
| 20 | Sample size | `n ≈ 960/d^2` |
| 21 | "Within noise" | A valid published outcome |
| 22 | Per-category diff | Aggregates hide collapses |
| 23 | Stable bucketing | hash(userId, salt) |
| 24 | Salt per experiment | Randomize across experiments |
| 25 | Minimum dwell | Long enough at 1% to resolve |
| 26 | Missing metric | Counts as a breach |
| 27 | Auto rollback | No human decision under pressure |
| 28 | Shadow | Mirror traffic, do not serve |
| 29 | Canary ladder | 1 / 5 / 25 / 100 |
| 30 | Blue-green | 0 or 100, instant flip |
| 31 | metrics/correct | Accuracy alone rewards spending |
| 32 | cost/correct | The business metric |
| 33 | format validity | Structural correctness |
| 34 | refusal rate | Safety behaviour per prompt |
| 35 | repair rate | Parse failures needing a retry |
| 36 | cache hit rate | Layout health |
| 37 | rollback events | Change-failure rate |
| 38 | drift vs change | Quality drop with no version change = input drift |
| 39 | intent mix | First thing to check on drift |
| 40 | prompt length | Second drift dimension |
| 41 | judge version | Part of the manifest |
| 42 | judge calibration | Re-measure agreement periodically |
| 43 | optimizer patience | Stop on no improvement |
| 44 | optimizer held-out | Never tune on the test set |
| 45 | multi-seed confirmation | Guards against ordering luck |
| 46 | mutation operators | Add/reorder/reword/counter-example |
| 47 | deprecation notices | Promotion, 50%, deadline |
| 48 | auto-pin | Safety net for un-migrated callers |
| 49 | compatibility shim | Reduces migration friction |
| 50 | lint rules | Order, unfilled vars, banned phrases, schema |
| 51 | CI block | Unversioned prompts cannot ship |
| 52 | spec completeness | Template + vars + sampling + evaluator |
| 53 | fast path | Low-risk prompts skip heavy gates |
| 54 | avoid over-gating | Over-gating causes bypass |
| 55 | multi-model portability | Not every optimization transfers |
| 56 | reverse prompting | Infer a prompt from I/O pairs |
| 57 | demo selection | Max validation accuracy, report marginal value |
| 58 | position variance | Average over orderings |
| 59 | schema adjacency | Keep the schema next to its instruction |
| 60 | prompt bloat | 40 tool schemas per step is a real cost |

## Self-Check

55+ = solid, 45-54 = redo Exercises 6 and 9, below that reread THEORY 1-8.