# Reflection: Probability Axioms

## Explain it in one breath
If someone asks "what is probability?", can you say: *a normalized, non-negative, countably additive measure on a sample space* — and then say what each of those three words forbids? Practice the forbidding: negative mass (impossible), total mass 2 (certainty plus extra), and a countable union whose probability exceeds the sum of its parts (a "measure" that leaks).

## Questions to answer in writing
1. Bertrand's chord paradox gives 1/3, 1/4 or 1/2. Which quantity was made uniform in each solution, and why does the axioms framework refuse to pick one for you?
2. In the medical-test example the posterior is 1/6, not 0.99. Write one sentence naming exactly which term is the likelihood and which is the prior — then explain why the 99% figure keeps reappearing in conversations about screening.
3. Give an example where P(A|B) is well-defined but P(B|A) is misleading *without* a base-rate difference — what does that tell you about conditioning direction?
4. A coin lands heads 10 times in a row. Under fair-coin model P = 1/1024. Does that make the coin biased? What would have to change — the measure or the model — for that inference to be legitimate? (This is lab 07's territory.)
5. Which of your intuitions about "random" actually assumed uniformity? List three real situations and the parameterization each one was uniform in.

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| Axioms (non-neg., normalization, countable additivity) | | | |
| Inclusion–exclusion (2 and 3 events) | | | |
| Product rule and marginalization | | | |
| Bayes' rule / likelihood ratio | | | |
| Independence vs. disjointness | | | |
| P = 0 vs. impossible | | | |

## Milestones
- [ ] Reproduce the medical-test posterior (1/6) and the odds-based check from memory
- [ ] Enumerate two dice and get P(sum ≥ 9) = 10/36 without looking anything up
- [ ] State why mutually exclusive positive-probability events cannot be independent
- [ ] Explain Kolmogorov's axioms to a colleague who thinks "probability = frequency"
- [ ] Name one question the axioms deliberately leave unanswered (the choice of measure)

## Extra prompts

- Re-derive P(disease | positive) = 1/6 twice — joint table and odds form — and mark exactly where the base rate enters each route.
- Collect three statements you heard this week of the form "X is 99% accurate" and reconstruct the missing sample space and base rate for each.
- For one published risk claim ("1 in a million"), write down what measure would have to be specified for the sentence to be testable.
- Prove to yourself why mutually exclusive positive-probability events cannot be independent, in two lines, from the definitions only.
