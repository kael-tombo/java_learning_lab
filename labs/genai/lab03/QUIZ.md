# Lab 03: Prompt Engineering Patterns — Quiz

## Questions

**Q1.** What is the most reliable way to make a model return machine-parseable output?
- a) "Return only JSON"
- b) Adjectives like "be precise"
- c) A schema plus constrained decoding, with validation
- d) Lower temperature to 0

**Q2.** Few-shot demonstrations work best when they...
- a) are sampled uniformly at random
- b) are numerous (>20)
- c) straddle the decision boundary of the label space
- d) are sorted alphabetically

**Q3.** "Let's think step by step" is an example of...
- a) zero-shot chain of thought
- b) prompt caching
- c) structured output
- d) role framing

**Q4.** Self-consistency means...
- a) Using the same temperature on every call
- b) Sampling k reasoning paths and taking the majority answer
- c) Caching identical prompts
- d) Validating with a schema

**Q5.** Tree-of-thought adds what over chain of thought?
- a) Branch expansion with backtracking
- b) Longer prompts
- c) Lower latency
- d) Fewer tokens

**Q6.** In decomposed prompting, sub-task outputs should be...
- a) Free text concatenated
- b) Typed records passed between stages
- c) Returned to the user
- d) Discarded

**Q7.** Why put stable content at the start of the prompt?
- a) Models read the end more carefully
- b) Prefix-based prompt caching can reuse it
- c) It reduces total tokens
- d) Required by the API

**Q8.** Where should retrieved document text be placed relative to policy?
- a) Before the system instructions
- b) After, clearly delimited as data
- c) Interleaved
- d) It should be omitted

**Q9.** What is the correct response to a model that emits invalid JSON?
- a) eval() the string
- b) Retry once with a repair prompt, then fall back to rule-based extraction
- c) Increase max_tokens and retry forever
- d) Return the raw string to the caller

**Q10.** Which statement about `stop` sequences is correct?
- a) They are ignored when temperature is 0
- b) They truncate output at the matched text
- c) They must be at least 4 tokens
- d) They only work on user messages

**Q11.** Decomposed prompting maps most directly to which Java pattern?
- a) Singleton
- b) Method composition over typed interfaces
- c) Thread pool
- d) Singleton registry

**Q12.** A prompt optimizer that keeps mutating without a validation set will...
- a) Converge faster
- b) Overfit the evaluator
- c) Use fewer tokens
- d) Improve generalization

**Q13.** Role framing ("You are a ...") works because pretraining contains...
- a) Explicit role tags
- b) Many role-conditioned continuations
- c) System prompts only
- d) Nothing role related

**Q14.** Which is NOT a text-level prompt lever?
- a) Format specification
- b) Role framing
- c) `max_tokens` decoding control
- d) Demonstration formatting

**Q15.** Why is `assertNoUnfilled()` valuable in a `PromptBuilder`?
- a) It shortens prompts
- b) Unfilled placeholders silently become literal text and confuse the model
- c) It counts tokens
- d) It encrypts variables

---

## Answers

1. **c** — constrained decoding plus validation and repair; instruction alone is a request, not a guarantee.
2. **c** — boundary examples carry the decision information.
3. **a** — zero-shot CoT elicits rationales already present in pretraining.
4. **b** — majority voting over sampled paths.
5. **a** — branching plus evaluation plus backtracking.
6. **b** — typed records keep stages testable and composable.
7. **b** — cached prefixes are billed/dispatched by prefix hash.
8. **b** — policy stays in the system message; retrieved text is data.
9. **b** — bounded repair then deterministic fallback.
10. **b** — matched text terminates generation.
11. **b** — planner/solver/combiner are plain Java interfaces.
12. **b** — you will chase evaluator-specific artifacts.
13. **b** — role-conditioned text is abundant in web-scale corpora.
14. **c** — `max_tokens` is a sampling/API control.
15. **b** — `{{user_name}}` reaching the model as literal text is a silent data leak.

## Score Guide

14-15: ready for Lab 04 (RAG) and ai-engineering lab05 (prompt ops).
11-13: redo Exercises 4, 6, 10.
0-10: reread THEORY sections 2-9.