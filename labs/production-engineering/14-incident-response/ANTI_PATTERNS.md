# ANTI-PATTERNS: Incident Response & Management
## Lab 14 | Production Engineering Academy

---

## Anti-Pattern 1: The "Hero" Debugger / Swarming Chaos

### The Mistake
30 engineers join a war room without an Incident Commander. Multiple people start executing uncoordinated changes simultaneously: someone restarts the database, another rolls back a service, a third changes JVM flags.

### Why It Fails
- Diagnostic signals are invalidated because variables are changing continuously.
- Actions conflict, compounding the outage and doubling MTTR.
- Nobody knows which action caused recovery or further damage.

### The Correct Production Fix
Strict Incident Command System (ICS). Responders propose hypotheses to the IC; the IC approves one action at a time.

---

## Anti-Pattern 2: The Finger-Pointing / Punitive Post-Mortem

### The Mistake
Writing post-mortems concluding: "Developer Bob made a typo in the config file. Action item: Bob will be retrained to be more careful."

### Why It Fails
1. Punishing individuals creates a culture of fear: engineers hide mistakes, delay reporting incidents, and avoid risky but necessary innovations.
2. It fails to address the real systemic problem: *Why was a human able to ship an unvalidated typo directly to production without schema validation, linters, or canary gates?*

### The Correct Production Fix
Adopt Dekker's **Blameless Culture**: Focus on systemic safety guardrails, automated linting, canary rollouts, and blast radius reduction.
