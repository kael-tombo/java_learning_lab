# Lab 14: LLMOps (LLM Operations) — Quiz

**Q1.** In an LLM system the deployable artifact is...
- a) The model weights only
- b) Model + prompt + retrieval index + tools + policy
- c) The training data
- d) The tokenizer

**Q2.** A prompt template edit is...
- a) A config tweak, not a release
- b) A release that must be versioned like any other
- c) Not worth versioning
- d) Only a release for system prompts

**Q3.** The release hash should cover...
- a) Only the model version
- b) Every versioned component in the manifest
- c) Only the prompt version
- d) Only the index version

**Q4.** Why must the release hash appear in every response?
- a) For billing
- b) So any response can be attributed to the exact configuration that produced it
- c) To enable caching
- d) For rate limiting

**Q5.** Shadow deployment means...
- a) Serving 1% to real users
- b) Mirroring traffic to a candidate without serving its responses
- c) Deploying to a second region
- d) Encrypting responses

**Q6.** Canary traffic should be assigned by...
- a) Request, randomly each time
- b) User, so a user sees one version per session
- c) Time of day
- d) API key hash only

**Q7.** Advancing a canary step should require...
- a) A human looking at it
- b) A minimum sample size with passing automated gates
- c) No time limit
- d) Zero errors

**Q8.** Which metric is "cost per successful outcome"?
- a) Cost per request
- b) Cost divided by the fraction of requests that achieved the user's goal
- c) Cost per input token
- d) Total monthly spend

**Q9.** A sudden cost increase usually indicates...
- a) A pricing change
- b) A retry loop, cache miss, context growth, or runaway agent steps
- c) Growth in users
- d) Nothing

**Q10.** Drift detection compares...
- a) Two models
- b) A rolling window of production inputs against a reference window
- c) Training and test loss
- d) Two prompts

**Q11.** PSI above 0.25 means...
- a) Stable
- b) A significant distribution shift worth investigating
- c) Perfect calibration
- d) Nothing to worry about

**Q12.** Which online sample is the unbiased quality estimate?
- a) All errors
- b) All escalations
- c) The random stratified sample
- d) High-value users only

**Q13.** Why sample errors 100% if they bias the quality metric?
- a) They are not part of the metric
- b) They drive the fix queue; the metric uses the random sample
- c) They are free to judge
- d) They are rare enough not to matter

**Q14.** Which cheap signals can run on 100% of responses?
- a) Faithfulness via NLI
- b) Schema validity, refusal, length, PII scan
- c) Win rate against a judge
- d) Task correctness

**Q15.** A trace should inline full prompts because...
- a) It is always safe
- b) Prompts may contain PII; hash and store a pointer instead
- c) Hashes cannot be reproduced
- d) It reduces storage

**Q16.** The first question for a quality-drop alert should be...
- a) "Is the model down?"
- b) "Did any versioned component change?"
- c) "Did traffic spike?"
- d) "Who is on call?"

**Q17.** The correct first action during an incident is...
- a) Roll back immediately
- b) Freeze releases and investigate from the trace
- c) Restart everything
- d) Raise temperature

**Q18.** Rollback must be...
- a) A rebuild
- b) A config change, because slow rollback causes bad decisions under pressure
- c) A code deploy
- d) Manual only

**Q19.** "Everything is a release" implies...
- a) Release often
- b) Version prompt, index, tools, and policy changes too
- c) Never release on Fridays
- d) Freeze forever

**Q20.** Feature flags with independent kill switches limit...
- a) Code size
- b) Blast radius
- c) Latency
- d) Token count

**Q21.** User signals map to training data as...
- a) Nothing
- b) Preference pairs, labeled items, and gold answers from human agents
- c) Only negative examples
- d) Only thumbs up

**Q22.** Implicit corrections (the user rewriting your answer) are valuable because...
- a) They are free
- b) They are a labeled preference pair produced at scale
- c) They fix bugs automatically
- d) They reduce cost

**Q23.** Toil analysis is useful because...
- a) It reduces headcount
- b) It tells you which operational work to automate next
- c) It is required by auditors
- d) It replaces runbooks

**Q24.** Load shedding should protect...
- a) Batch traffic first
- b) Interactive traffic first
- c) Long-context requests
- d) Whatever is cheapest

---

## Answers

1. **b** — four of the five artifacts are configuration, not weights.
2. **b** — it changes every response.
3. **b** — attribution requires the full set.
4. **b** — without it, every bug investigation starts from scratch.
5. **b** — measured with zero user impact.
6. **b** — otherwise a user sees two versions in one session.
7. **b** — decisions on tiny samples are noise.
8. **b** — the denominator that reflects value delivered.
9. **b** — cost spikes are usually a symptom, not a cause.
10. **b** — comparing windows reveals change.
11. **b** — investigate and freeze.
12. **c** — the other samples are deliberately biased.
13. **b** — mix of purposes, measured separately.
14. **b** — no model call required.
15. **b** — logs are a liability.
16. **b** — most quality incidents are a prompt or index change.
17. **b** — blind rollbacks hide the cause and sometimes make it worse.
18. **b** — minutes matter.
19. **b** — every artifact gets a version.
20. **b** — bounded blast radius.
21. **b** — that is how preference data and gold answers are produced.
22. **b** — scale plus ground truth.
23. **b** — prioritization of automation work.
24. **b** — shed batch first, then long contexts, then interactive last.

## Score Guide

22-24: ready for ai-engineering labs 08 and 10.
16-21: redo Exercises 5, 11, 17.
0-15: reread THEORY sections 2-7.