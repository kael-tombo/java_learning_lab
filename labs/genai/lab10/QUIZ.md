# Lab 10: LLM Safety & Alignment — Quiz

**Q1.** Prompt injection differs from jailbreaking because injection...
- a) Uses fewer tokens
- b) Arrives through content the application treats as data
- c) Always succeeds
- d) Requires base64

**Q2.** Delimiters around untrusted content are...
- a) A security boundary
- b) A helpful prior that reduces but does not prevent injection
- c) Unnecessary if the model is good enough
- d) Only needed on output

**Q3.** Privilege separation means tool permissions come from...
- a) The prompt text
- b) Code (the registry and the gate), never from model output
- c) The user's request
- d) Retrieved documents

**Q4.** A read-only agent should have...
- a) Write tools with a confirmation prompt
- b) No write tools in its registry at all
- c) Write tools approved by the model
- d) Write tools with argument validation

**Q5.** A guardrail that returns the content when its classifier throws is...
- a) Optimistic and fine
- b) Failing open, which makes it not a guardrail
- c) Faster
- d) Correct for low-risk categories

**Q6.** Refusal rate and over-refusal rate must be reported together because...
- a) They are the same number
- b) Guardrail tuning moves them in opposite directions
- c) Only one is measurable
- d) They must sum to 1

**Q7.** "How do I kill a stuck process" is an example of...
- a) A jailbreak
- b) A benign request vulnerable to over-refusal
- c) An injection payload
- d) A prompt injection

**Q8.** Encoding-based attacks (base64, ROT13) are defeated by...
- a) Longer system prompts
- b) Decoding suspicious segments and classifying the decoded text too
- c) A bigger model
- d) Lower temperature

**Q9.** Deleting suspicious input rather than quoting it is bad because...
- a) It is slower
- b) It destroys legitimate content and teaches attackers which characters to use
- c) It breaks the tokenizer
- d) It uses more memory

**Q10.** Zero-width characters are dangerous because they...
- a) Increase token count only
- b) Hide instructions from human reviewers while remaining visible to the model
- c) Speed up inference
- d) Compress the prompt

**Q11.** Multi-turn injection defeats per-turn filters because...
- a) Each turn alone looks benign
- b) Turns are processed independently by design
- c) Filters only run on the first turn
- d) The model forgets

**Q12.** The purpose of turning a red-team finding into a permanent test is to...
- a) Satisfy compliance
- b) Prevent the same bypass being reintroduced by a later refactor
- c) Increase coverage numbers
- d) Reduce model size

**Q13.** Instruction collision is best described as...
- a) Two users racing
- b) An attacker instruction appended after content, competing with the real one
- c) A concurrency bug
- d) A tokenizer issue

**Q14.** Alignment training (SFT/RLHF/constitutional) raises the floor but...
- a) Eliminates the need for runtime guardrails
- b) Does not transfer reliably to new attack families
- c) Slows the model
- d) Increases cost only

**Q15.** Output guardrails exist to protect...
- a) The system
- b) The user, from harmful or malformed model output
- c) The tokenizer
- d) The index

**Q16.** Category-specific refusal thresholds beat one global threshold because...
- a) They are cheaper
- b) Legitimate and harmful requests in different categories need different bars
- c) Global thresholds do not work at all
- d) They avoid false negatives entirely

**Q17.** A self-harm-related request should be handled differently from a security
research request because...
- a) Self-harm is not a safety category
- b) The appropriate response differs fundamentally in urgency and referral
- c) Security research is always allowed
- d) Cost differs

**Q18.** The two operational safety metrics that matter in a drill are...
- a) Refusal rate and over-refusal rate
- b) Time to detect and time to contain
- c) Tokens and cost
- d) Recall and precision

**Q19.** Safe mode typically means...
- a) Turning the model off
- b) Strictest policy, tools disabled, retrieval off, output blocking forced
- c) Increasing max tokens
- d) Raising temperature

**Q20.** A canary string in the system prompt is used to detect...
- a) Slow responses
- b) Leaks of the system prompt into outputs
- c) Tokenizer bugs
- d) Rate limit violations

---

## Answers

1. **b** — the channel is the difference, and that is what makes it dangerous.
2. **b** — helpful, not a boundary. Code-level privilege separation is the boundary.
3. **b** — capability must not be grantable by text.
4. **b** — no write tool means no write to inject.
5. **b** — fail-closed or it is not a guardrail.
6. **b** — tightening a filter raises both.
7. **b** — the classic over-refusal case in developer tooling.
8. **b** — classify the decoded text as well as the raw text.
9. **b** — deletion is both lossy and a discoverable side channel.
10. **b** — invisible to reviewers, effective against the model.
11. **a** — the payload is only complete across turns.
12. **b** — that is the whole point of a regression test.
13. **b** — the attacker's instruction competes with yours.
14. **b** — new attack families are exactly where training-time robustness fails.
15. **b** — input guardrails protect the system; output guardrails protect the user.
16. **b** — one bar cannot serve both legitimate security education and weapon
   synthesis requests.
17. **b** — urgency, tone, and the need for a referral differ.
18. **b** — everything else is a proxy for those two.
19. **b** — degrade capability while preserving safety.
20. **b** — any appearance of the canary is a hard failure.

## Score Guide

18-20: ready for ai-engineering lab09 and lab10.
14-17: redo Exercises 6, 11, 13.
0-13: reread THEORY sections 2-8.