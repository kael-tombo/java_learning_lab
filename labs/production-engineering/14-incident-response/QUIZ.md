# Lab 14: Production Incident Response & RCA — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is the single most important thing to do in the first five minutes of an incident?**
- A) Find the root cause
- B) Establish command: name an incident commander, open the channel, start the timeline, and state the current impact — before touching anything. Parallel investigation without a commander produces duplicate work and conflicting changes
- C) Roll back immediately
- D) Post in Slack

**Answer: B** — Mitigation and diagnosis can happen in parallel; *coordination* cannot. Root cause is not an incident-time goal.

---

**Q2. What is an incident timeline, and why is it the highest-value artefact?**
- A) An optional document
- B) A timestamped record of every observed fact, action taken, decision, and change — written *during* the incident. It is the only reliable memory; memory 20 minutes later is reconstructive fiction, and it is the raw material for the postmortem
- C) The postmortem
- D) The alert history

**Answer: B** — Keep it in a shared doc, append-only, with timestamps from a single clock. Write "assumed X, verified Y" so confidence is explicit.

---

**Q3. Why does "quickly roll back the last deploy" fail as a first move?**
- A) It is always wrong
- B) The last deploy may be unrelated, may already be fully rolled out, may not be rollback-capable (schema/data change), and rolling back under uncertainty can convert a partial outage into a total one if the previous version cannot read the current data
- C) Rollback is too slow
- D) The deploy was a good change

**Answer: B** — Rollback is a *hypothesis test*, not a reflex. Ask: is the deploy correlated in time, is rollback available, and is the previous version safe against current state? A change log plus the timeline gives you that in 60 seconds.

---

**Q4. What is MTTD vs MTTR vs MTTM, and why distinguish them?**
- A) They are the same
- B) MTTD = time to *detect* (alerting/observability design). MTTA = time to *acknowledge*. MTTM = time to *mitigate* (stop the bleeding). MTTR = time to *restore* (including permanent fix or full resolution). Each has a different owner and a different fix
- C) MTTR includes prevention
- D) MTTD is the only one that matters

**Answer: B** — Conflating them hides the fact that a good alerting investment moves MTTD while a good runbook moves MTTM/MTTR. Most teams measure only one and misdiagnose their own problem.

---

**Q5. When should you declare an incident formally?**
- A) Only for SEV-1
- B) Earlier than feels comfortable — the declaration triggers the machinery (commander, roles, comms, status page, bridge). A small incident handled as an incident costs ten minutes; a large incident handled as "just a bug" costs hours
- C) After you know the cause
- D) Only when customers are affected

**Answer: B** — Customer impact is one criterion; sustained degradation, a novel failure, an unowned alert, or a fix requiring risky action are others. Pre-declare the criteria.

---

**Q6. What are the incident roles, and what is the most common failure?**
- A) Commander, comms lead, operations lead, scribe — the common failure is role confusion: three people "coordinating" and nobody writing the timeline or talking to stakeholders
- B) Only an IC is needed
- C) Scribe, writer, reviewer
- D) Roles are optional for small incidents

**Answer: A** — For small incidents the IC *is* the ops lead *and* the scribe; what must never happen is two people making production changes at once without the IC knowing.

---

**Q7. Why is "mitigate first, diagnose later" correct even for a subtle bug?**
- A) Because root cause is not real
- B) Restoring service reduces blast radius and buys time for a proper diagnosis; the cause is often inferable afterwards from logs and metrics that will still be there, whereas the outage window is not recoverable
- C) Because root cause takes days
- D) Because customers do not care

**Answer: B** — The exception: mitigation must be *reversible and understood*. A fix that might make things worse belongs after diagnosis or behind a flag.

---

**Q8. What makes a postmortem useful instead of performative?**
- A) It assigns blame
- B) It produces specific, owned, time-boxed actions with a stated success measure, and it explains *why the system allowed* the incident — including the detection and decision gaps. If the actions are "be more careful", it failed
- C) It is long
- D) It is confidential

**Answer: B** — Blameless does not mean consequence-free; it means naming systems and decisions rather than people. An action with no owner and no date is a wish.

---

**Q9. Why does "human error" almost never appear as a root cause?**
- A) People do make mistakes
- B) Human error is a *symptom* — of inadequate system design, tooling, review, or interfaces that permitted the mistake under time pressure. A postmortem that stops at "operator ran the wrong command" has found where the mistake surfaced, not why it was possible
- C) It is politically sensitive
- D) Errors are rare

**Answer: B** — The productive question is: what would have made the correct action the easy action, and what would have blocked the incorrect one?

---

**Q10. What is a "contributing factor" versus the "root cause"?**
- A) They are the same
- B) The root cause is the deepest condition you can reasonably change; contributing factors are the conditions that made the failure likely or the damage worse (no canary, no alert, no runbook, a single point of failure). Most incidents have several contributing factors and rarely one root cause
- C) Root cause is technical
- D) Contributing factors are irrelevant

**Answer: B** — Insisting on a single root cause produces false certainty and single-action fixes that leave the other factors untouched.

---

**Q11. Why must incident communication be scheduled rather than remembered?**
- A) Because rules require it
- B) Because silence is interpreted as ignorance and the cost of a late update compounds. A pre-agreed cadence (e.g. every 30 min, even when there is no change: "no change, still investigating X") sets stakeholder expectations and prevents the "are you still working on it?" flood
- C) Communication slows resolution
- D) Only customers care

**Answer: B** — "No change" updates are the ones teams skip and are the ones stakeholders need most.

---

**Q12. What is the difference between an incident review and a postmortem?**
- A) Synonyms
- B) The review is immediate and narrow: what happened, what we did, what to fix, by when. The postmortem is broader and later: systemic causes, class-of-incident analysis, and whether this is a recurrence. Skipping the immediate review guarantees the postmortem is written from memory weeks later
- C) Postmortem is for SEV-1 only
- D) Review is for customers

**Answer: B** — Also: the most valuable question is "is this a recurrence, and if so why did the previous action not prevent it?"

---

**Q13. Why does a game day outperform a tabletop exercise?**
- A) It is cheaper
- B) A tabletop tests understanding; a game day tests the *system* — the runbook's commands, the alert routing, the access permissions, the dashboards, and whether anyone can actually reach production under pressure. It finds the gaps you did not know to write down
- C) It is more realistic for communication
- D) It does not require preparation

**Answer: B** — The highest-value findings in game days are almost always mundane: a runbook command that no longer exists, a dashboard behind a VPN, an escalation path with an unreachable person.

---

**Q14. What makes an action item actually get done?**
- A) A clear title
- B) A named owner, a date, a definition of done that is observable, and a tracking mechanism in the team's normal work — plus escalation when it slips. "Improve monitoring" has none of these
- C) High priority
- D) A Slack thread

**Answer: B** — Track completion as a metric in the same review that raised it; if action-item completion is under ~70%, the problem is the process, not the items.

---

**Q15. The single most common reason incident response does not improve over time is?**
- A) Not enough incidents
- B) The same failures recur because postmortem actions are unowned, and because nothing measures whether they worked. Without a recurrence check per action, the organisation cannot tell improvement from documentation
- C) The on-call is small
- D) Postmortems take too long

**Answer: B** — The metric that matters is recurrence rate per incident class, plus action completion rate. Measure both, or the practice is theatre.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and run an incident exercise end to end.
- 12–10: revisit roles, timeline discipline, and postmortem structure; redo EXERCISES 2–5.
- <10: re-read THEORY + RUNBOOKS cold and retake in 48 hours.
