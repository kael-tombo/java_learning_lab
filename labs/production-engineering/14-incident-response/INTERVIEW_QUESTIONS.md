# INTERVIEW QUESTIONS: Incident Response & SRE Operations
## Lab 14 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Describe the responsibilities of an Incident Commander during a production outage.
**Answer**:
The Incident Commander (IC) is responsible for the overall strategy and management of the incident.
Key duties:
1. Establish command and maintain clear communication on the bridge.
2. Ensure only one person speaks at a time and prevent chaotic speculative action.
3. Assign operational tasks to technical SMEs (e.g. "Engineer A: check database locks; Engineer B: inspect recent commit diffs").
4. Protect responders from executive interference by delegating external updates to a Communications Lead.
5. Make final decisions on high-impact mitigation actions (rollbacks, database failovers, traffic shedding).
6. Crucially, the IC does NOT look at code, run commands, or debug directly; doing so causes loss of situational awareness.

---

## Staff / Principal Level (8+ Years)

### Q2: How do you institutionalize a genuine Blameless Post-Mortem culture in an organization with a history of finger-pointing?
**Answer**:
1. **Executive Sponsorship & Cultural Safety**: Leadership must explicitly reinforce that finding scapegoats encourages people to hide near-misses and errors, making the system vastly more dangerous.
2. **Focus on Latent Systemic Traps**: Reframe questions from "Who did this?" to:
   - *What information was available to the engineer at the moment of decision?*
   - *Why did the system make the wrong action look reasonable or easy to execute?*
   - *What automated safety guardrail was missing that allowed human action to propagate to production unchecked?*
3. **Action Items Quality**: Mandate that post-mortem action items focus on engineering guardrails (e.g. linters, canary aborts, permissions, circuit breakers), and forbid action items like "Retrain engineer" or "Remind team to be careful".
