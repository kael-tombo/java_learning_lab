# Lab 05: Prompt Engineering at Scale — Quiz

**Q1.** Prompts should be versioned like code because...
- a) They are text files
- b) A prompt change alters every response and must be attributable and reversible
- c) Version control requires it
- d) Models cannot read unversioned text

**Q2.** An active prompt version must be...
- a) Mutable for quick fixes
- b) Immutable; edits create a new version
- c) Deleted before release
- d) Shared with every team

**Q3.** Every prompt version must have...
- a) A description
- b) An owner and a risk tier
- c) A changelog only
- d) A model preference

**Q4.** Promotion of a prompt version must require...
- a) A code review
- b) A passing gate on the registered suite
- c) A ticket
- d) Manual approval from 2 people

**Q5.** Rollback should be...
- a) A re-render
- b) A single config call that also invalidates the render cache
- c) A redeploy
- d) Editing the version in place

**Q6.** Typed prompt variables prevent...
- a) Long prompts
- b) Unfilled placeholders and wrong-typed values reaching the model
- c) Cost
- d) Refusals

**Q7.** Canonical section order matters mainly because...
- a) It looks tidy
- b) It makes prefix caching work and diffs readable
- c) Models require it
- d) It reduces tokens

**Q8.** A/B experiments must compare systems on...
- a) Different item sets
- b) Identical items (paired)
- c) Random samples
- d) Production traffic only

**Q9.** Why is the paired test more sensitive?
- a) It uses more items
- b) Item difficulty cancels out
- c) It avoids bootstrap
- d) Judges are more accurate

**Q10.** The minimum sample size for a 5-point change on a rate near 0.5 is about...
- a) 20
- b) 40
- c) 384
- d) 3,840

**Q11.** "Within noise" is a valid experiment outcome because...
- a) It saves time
- b) The CI included zero; claiming a win would be false
- c) It always happens
- d) Judges are unreliable

**Q12.** Per-category diffs are required because...
- a) Categories are cheaper
- b) A collapse in one intent can hide inside a flat aggregate
- c) Aggregates are invalid
- d) Categories are easier to prompt

**Q13.** A missing canary metric should be treated as...
- a) A pass
- b) A breach, so broken telemetry cannot promote a bad prompt
- c) A warning with no effect
- d) A reason to increase traffic

**Q14.** Risk tiers exist so that...
- a) High-risk prompts get more gates
- b) All prompts are treated equally
- c) Low-risk prompts are skipped
- d) Reviewers can ignore medium risk

**Q15.** Prompt bundles are versioned atomically to prevent...
- a) Storage costs
- b) Family drift where one prompt updates and the rest go stale
- c) Cache misses
- d) Duplicate versions

**Q16.** Shadow evaluation's advantage is...
- a) Faster results
- b) Measuring a candidate at zero user risk
- c) Cheaper tokens
- d) Better accuracy

**Q17.** `tokens/correct` is reported alongside accuracy because...
- a) Tokens are cheap
- b) Accuracy alone rewards longer, more expensive prompts
- c) It is required by providers
- d) Accuracy is unreliable

**Q18.** Quality dropping with an unchanged prompt and model suggests...
- a) The prompt broke
- b) Input distribution drift
- c) The judge drifted
- d) Nothing

**Q19.** An optimizer that gains on the validation set and loses on a fresh set has...
- a) Improved the prompt
- b) Overfit the evaluator
- c) Found a better model
- d) Reduced latency

**Q20.** Deprecation auto-pinning at the deadline is needed because...
- a) Providers require it
- b) Otherwise un-migrated callers break in production
- c) It saves tokens
- d) It improves quality

---

## Answers

1. **b** — reproducibility and attribution are the whole point.
2. **b** — mutability destroys the ability to reason about what is live.
3. **b** — unowned prompts are unmaintained prompts.
4. **b** — gating is what makes a prompt change a controlled change.
5. **b** — slow rollback causes bad decisions under pressure.
6. **b** — `{{var}}` reaching the model is a silent data leak.
7. **b** — prefix caching depends on a stable prefix.
8. **b** — pairing is what removes item-difficulty variance.
9. **b** — differences on identical items are far less noisy.
10. **c** — `960/25 = 38.4`, so ~384 for 5% relative resolution; the practical figure
    for 5 points on a rate near 0.5 is a few hundred.
11. **b** — publishing a win inside the CI's noise is a false claim.
12. **b** — averages hide regressions by construction.
13. **b** — fail closed.
14. **a** — effort should scale with blast radius.
15. **b** — partial updates cause non-reproducible behaviour.
16. **b** — no user sees the candidate.
17. **b** — otherwise "improvement" can be bought with tokens.
18. **b** — check intent mix, length, and language first.
19. **b** — the held-out set is the honest measurement.
20. **b** — auto-pin is the safety net for missed migrations.

## Score Guide

18-20: ready for lab 07 (testing) and lab 08 (observability).
14-17: redo Exercises 2, 6, 9.
0-13: reread THEORY sections 1-8.