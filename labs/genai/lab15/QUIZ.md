# Lab 15: Building a GenAI Platform — Quiz

**Q1.** A GenAI platform is best described as...
- a) A model server
- b) Capabilities + interfaces + operations + governance + enablement
- c) A vector database
- d) A chat UI

**Q2.** Dependencies between platform layers must point...
- a) Upward
- b) Downward only
- c) Both ways for flexibility
- d) Randomly

**Q3.** Logical model names (`chat-quality`) are valuable because...
- a) They are shorter
- b) The underlying model can be swapped without changing product code
- c) They cost less
- d) They avoid rate limits

**Q4.** The routing dimension that is a functional requirement rather than a policy is...
- a) Quality tier
- b) Capability (e.g. vision support)
- c) Latency tier
- d) Cost ceiling

**Q5.** Fallback retry policy should skip retries on...
- a) Timeouts
- b) 4xx validation errors
- c) Circuit-open states
- d) Rate limits

**Q6.** Fallback capacity must be sized to...
- a) A fraction of peak
- b) Full peak capacity, since it exists for total primary failure
- c) Zero, since fallback is rare
- d) One replica

**Q7.** A circuit breaker on a model exists to...
- a) Reduce latency
- b) Stop hammering a failing dependency and shift traffic
- c) Improve quality
- d) Cache responses

**Q8.** Prompts belong in a registry because they are...
- a) Long
- b) Code: versioned, owned, and gated like source
- c) Generated at runtime
- d) Model-specific

**Q9.** Every prompt version must pass an evaluation gate before promotion because...
- a) It is fast
- b) Prompt changes alter every response
- c) The platform requires it
- d) Prompts are usually wrong

**Q10.** Typed prompt variables prevent...
- a) Long prompts
- b) Unfilled placeholders reaching the model
- c) Cost
- d) Refusals

**Q11.** Guardrails should be a platform service because...
- a) They are complex
- b) Every product reimplements them badly otherwise
- c) They are cheap
- d) Models require them

**Q12.** Products should be able to tighten guardrails but not disable them without...
- a) A reason
- b) An approval process
- c) A ticket
- d) Nothing

**Q13.** The tool registry's `side-effect class` exists so the platform can...
- a) Sort tools
- b) Require approvals for irreversible operations
- c) Cache tool output
- d) Version tools

**Q14.** Shared caches must namespace keys by tenant because otherwise...
- a) Hit rate drops
- b) One tenant's data can be served to another
- c) Latency rises
- d) Cost increases

**Q15.** Tenant isolation for retrieval should be implemented as...
- a) A post-filter after retrieval
- b) A pre-filter inside the index query
- c) A prompt instruction
- d) An ACL on the API only

**Q16.** The platform evaluation gate should include the product's own suite because...
- a) It is faster
- b) Platform suites do not know the product's tasks
- c) Products demand it
- d) It is free

**Q17.** Target utilization for capacity planning is...
- a) 1.0
- b) <= 0.6
- c) 0.2
- d) Undefined

**Q18.** The most commonly missing platform SLI is...
- a) Latency
- b) Time to first success for a new team
- c) Throughput
- d) Cost

**Q19.** "Time to first success" measures...
- a) Model warmup
- b) How quickly a new team ships its first production feature
- c) Cache warmup
- d) Index build time

**Q20.** Over-gating causes teams to...
- a) Be happy
- b) Route around the platform
- c) Use cheaper models
- d) Improve quality

**Q21.** The right build order starts with...
- a) A vector database
- b) One model, one route, telemetry from day one
- c) A developer portal
- d) A multi-model fleet

**Q22.** Cost attribution must exist from day one because...
- a) Finance requires it
- b) Without it nobody knows where spend goes, so nobody optimizes
- c) Invoices require it
- d) It is regulatory

**Q23.** A platform nobody uses is...
- a) Cheap
- b) Not a platform; teams will bypass it
- c) A success
- d) A documentation problem

**Q24.** Platform teams that own all reliability end up...
- a) Faster
- b) A bottleneck with burnout
- c) More accurate
- d) Safer

---

## Answers

1. **b** — capabilities alone are not a platform.
2. **b** — upward dependencies create coupling and outages.
3. **b** — abstraction over the model is the highest-value platform feature.
4. **b** — capability is a correctness requirement; the rest are policy.
5. **b** — a malformed request will fail again identically.
6. **b** — fallback exists for total primary failure, so it must carry full load.
7. **b** — otherwise a down model is hammered by every request.
8. **b** — prompts are versioned source code.
9. **b** — a prompt edit changes every response downstream.
10. **b** — `{{var}}` reaching the model is a silent data leak (Lab 03).
11. **b** — the alternative is 30 slightly different unsafe implementations.
12. **b** — governance requires an accountable approver.
13. **b** — approval policy keys off the side-effect class.
14. **b** — that is a security incident, not a performance issue.
15. **b** — post-filtering can leak through rankings and is harder to reason about.
16. **b** — the platform cannot know the product's intents.
17. **b** — tail latency explodes near saturation (Lab 11).
18. **b** — adoption is the platform's product metric.
19. **b** — the onboarding experience, end to end.
20. **b** — a platform that blocks work gets bypassed, including its guardrails.
21. **b** — capability and telemetry first; the portal is presentation.
22. **b** — unattributed spend cannot be optimized by anyone.
23. **b** — teams build around it, and the gate disappears with it.
24. **b** — tiered SLOs with explicit ownership prevent this.

## Score Guide

22-24: ready for ai-engineering labs 01 and 10.
16-21: redo Exercises 4, 12, 16.
0-15: reread THEORY sections 2-9.