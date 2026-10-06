# Lab 09: AI Security — Quiz

**Q1.** Prompt injection differs from jailbreaking because injection...
- a) Uses fewer tokens
- b) Arrives through content the application treats as data
- c) Always succeeds
- d) Requires base64

**Q2.** Which of these is a genuine security boundary?
- a) The system prompt
- b) The tool registry and gate in code
- c) A content classifier
- d) A deny-list of phrases

**Q3.** Delimiters around untrusted content are...
- a) A security boundary
- b) A defence-in-depth layer that raises cost and buys time
- c) Unnecessary with a good model
- d) Only needed on output

**Q4.** Privilege separation means capability comes from...
- a) The prompt text
- b) Code: the registry, the gate, and approval policies
- c) The user's request
- d) Retrieved documents

**Q5.** A read-only agent should have...
- a) Write tools with a confirmation prompt
- b) No write tools registered at all
- c) Write tools the model approves
- d) Write tools with argument validation

**Q6.** A guardrail that returns content when its classifier throws is...
- a) Optimistic and fine
- b) Failing open, therefore not a guardrail
- c) Faster
- d) Correct for low-risk categories

**Q7.** Refusal and over-refusal must be reported together because...
- a) They are the same number
- b) Tuning one moves the other in the opposite direction
- c) Only one is measurable
- d) They sum to 1

**Q8.** "How do I kill a stuck process" is a classic...
- a) Jailbreak
- b) Over-refusal false positive
- c) Injection payload
- d) Exfiltration attempt

**Q9.** Deleting suspicious input rather than quoting it is bad because...
- a) It is slower
- b) It destroys legitimate content and teaches attackers which characters to use
- c) It breaks the tokenizer
- d) It uses more memory

**Q10.** Zero-width characters are dangerous because...
- a) They cost tokens
- b) They hide instructions from human reviewers while remaining visible to the model
- c) They slow inference
- d) They compress the prompt

**Q11.** Multi-turn injection defeats per-turn filters because...
- a) Filters only run on the first turn
- b) Each turn alone looks benign; the payload is only complete across turns
- c) The model forgets
- d) Turns are encrypted

**Q12.** Argument-scoped approvals prevent...
- a) Slow tools
- b) Approving one call and then reusing that approval for different arguments
- c) Prompt injection
- d) Cost overruns

**Q13.** Tenant isolation for retrieval must be a pre-filter because...
- a) Post-filters are slower
- b) Unauthorized content must never influence ranking or the prompt
- c) Pre-filters use less memory
- d) Providers require it

**Q14.** Cross-tenant cache leaks are prevented by...
- a) Short TTLs
- b) Tenant and authz scope in the cache key
- c) More replicas
- d) Larger batches

**Q15.** A system-prompt canary exists to detect...
- a) Slow responses
- b) Leakage of the system prompt into outputs
- c) Tokenizer bugs
- d) Rate-limit violations

**Q16.** Canaries must be tested at volume because...
- a) Providers require it
- b) Small per-token leak probabilities compound into a near-certain incident rate
- c) Volumetric tests are faster
- d) Small tests are unreliable

**Q17.** Hash-chained audit logs detect tampering by...
- a) Encryption
- b) Recomputation of the chain from an append-only sink
- c) Access control
- d) Hashing the file

**Q18.** Pinning a base model by commit SHA is a supply-chain control because...
- a) It is faster to load
- b) A floating tag can silently change what you serve
- c) SHAs compress better
- d) It reduces cost

**Q19.** Abuse detection should throttle rather than hard-block because...
- a) Throttling is cheaper to implement
- b) Legitimate users behind shared IPs must not be punished
- c) Blocking is illegal
- d) Throttling catches more attackers

**Q20.** Every security incident should produce...
- a) A post-mortem only
- b) A permanent red-team regression test
- c) A new policy
- d) A model upgrade

---

## Answers

1. **b** — the application supplies the channel, which is what makes it dangerous.
2. **b** — capability is decided where the attacker cannot reach.
3. **b** — honest defence-in-depth framing is what makes it defensible.
4. **b** — a model statement of authority is data, never authority.
5. **b** — nothing to inject into.
6. **b** — fail closed or it is not a guardrail.
7. **b** — tightening raises both.
8. **b** — developer tooling is the classic false positive.
9. **b** — deletion is lossy and a discoverable side channel.
10. **b** — invisible to reviewers, effective against the model.
11. **b** — stateful accumulation is required.
12. **b** — approvals must bind to exact arguments and expire.
13. **b** — post-filtering can leak through ranking and is harder to reason about.
14. **b** — scoping is the only structural prevention.
15. **b** — any appearance is a hard failure.
16. **b** — `1 - (1-q)^n` compounds quickly.
17. **b** — recomputation against an external sink detects rewrites.
18. **b** — tags move; reproducibility requires immutability.
19. **b** — shared IPs and NAT are real.
20. **b** — otherwise the next refactor reintroduces it.

## Score Guide

18-20: ready for lab 10 (deployment) and genai lab10.
14-17: redo Exercises 5, 7, 11.
0-13: reread THEORY sections 1-8.