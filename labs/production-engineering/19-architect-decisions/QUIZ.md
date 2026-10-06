# Lab 19: Java Architect Decision Framework — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is an Architecture Decision Record, and what is it actually for?**
- A) Documentation for auditors
- B) A short, dated, immutable record of a decision *in its context*: what we decided, the alternatives, the forces, the consequences. Its value is that a future reader (or you in two years) can reconstruct the reasoning and therefore know whether it still applies
- C) A design document
- D) A meeting note

**Answer: B** — ADRs are append-only. When a decision is superseded, you write a new one that supersedes the old; you do not edit history. An ADR without context is just a note.

---

**Q2. Why must an ADR record the *rejected* alternatives?**
- A) To show thoroughness
- B) Because the value is in knowing that the alternatives were considered and why they lost under the *then-current* forces. Without them, a future team re-litigates the decision, or worse, reinvents a rejected option without knowing why it failed
- C) Legal requirement
- D) To help with reviews

**Answer: B** — Record the alternatives and the *specific reason* each lost. "We didn't like it" is not a reason; "single-writer throughput collapsed at 40k msg/s and operational complexity was too high for our team" is.

---

**Q3. What belongs in the "Consequences" section, and what does not?**
- A) Positive consequences only
- B) Both positive and negative consequences, including the obligations you are accepting and the costs you now carry. An ADR with only benefits is marketing
- C) A risk list
- D) Nothing

**Answer: B** — Negative consequences are the most useful part of an ADR, because they are what the future team must live with. If you cannot name a negative consequence, you have not thought about it.

---

**Q4. Why are ADRs immutable and append-only?**
- A) Simplicity
- B) Because a decision record is evidence of what was known at the time. Editing history destroys the ability to understand why the system looks like it does, and hides whether a decision was revisited
- C) Because git is immutable
- D) To prevent rewrites

**Answer: B** — The workflow is: `Accepted`, later `Superseded by ADR-0042`. Never edit the original body; add a status line and write a new record.

---

**Q5. When does an architecture decision need an ADR?**
- A) Every code change
- B) When a choice is expensive to reverse, affects more than one team or more than one release window, introduces a new dependency or platform commitment, or constrains future options. The test is reversibility and blast radius, not importance
- C) Only for technology choices
- D) Only for irreversible decisions

**Answer: B** — A one-line config change does not need one. Choosing a message broker, a data store, a sharding strategy, or an authentication model does.

---

**Q6. What is the difference between a decision and a proposal, and why does the distinction matter?**
- A) None
- B) A proposal is an argument for a decision; a decision is a commitment. Mixing them means the team never knows whether the debate is closed, and reversals happen informally without being recorded
- C) A decision is documented, a proposal is not
- D) A proposal is reversible

**Answer: B** — State explicitly in the ADR whether the decision is made, and what the revisit trigger is. "Proposed, awaiting sign-off from X" is a legitimate status.

---

**Q7. What is the "revisit trigger", and why is it the most valuable line in an ADR?**
- A) A date
- B) A stated, observable condition under which the decision should be reconsidered — e.g. "our Kafka retention requirement exceeds 2 weeks", "our read:write ratio exceeds 20:1", "our team's on-call load exceeds 2 pages/shift". It converts a permanent decision into a conditional one and gives the future team an objective trigger rather than a feeling
- C) A cost threshold
- D) An SLA

**Answer: B** — Without a trigger, an ADR is a decree. With one, it is a decision with an expiry condition, and the trigger is checkable.

---

**Q8. How do you evaluate a technology choice's total cost?**
- A) Licence cost only
- C) Implementation effort only
- B) TCO over the decision's horizon: licences/infrastructure, the implementation and migration effort, the operational cost (on-call load, failure modes, upgrades), the exit cost (data migration, API compatibility, retraining), and the opportunity cost of what you are *not* building with that time
- D) The salary of the engineers involved

**Answer: B** — The dominant term is usually exit cost and opportunity cost, and they are almost always the terms omitted.

---

**Q9. What is the standard way to present a decision to a non-technical audience?**
- A) A diagram
- B) Options, each with its cost, risk, and what it means for the business; a recommendation with the reasoning; and the specific decision you need from them (a budget, a deadline, an accepted risk). Do not teach them the technology
- C) A technical document
- D) A presentation with slides

**Answer: B** — The ask must be explicit. "We're using Kafka because it's better" is not a decision request; "we need 2 engineer-weeks and 6 months of dual-write, and the alternative is a 3% revenue-risk incident, approve?" is.

---

**Q10. When is "build vs buy" decided by engineering, and when by the business?**
- A) Always engineering
- B) Engineering assesses technical fit and operational cost; the business weighs strategic differentiation, vendor lock-in, and total cost of ownership over the horizon. The decision is usually a hybrid — buy the commodity, build the differentiator
- C) Always the business
- D) Never a business decision

**Answer: B** — Presenting this as a purely technical choice is a category error, and it produces the worst outcomes (buying a differentiating component, or rebuilding a commodity badly).

---

**Q11. What is technical debt, and how do you distinguish it from deliberate, documented trade-offs?**
- A) Any shortcut
- B) Technical debt is a *deliberate* choice to take a suboptimal path *without* a plan to return to the optimal one. A documented trade-off with a revisit trigger is not debt — it is engineering. Undocumented shortcuts are debt; documented ones with triggers are strategy
- C) Old code
- D) Any code that needs maintenance

**Answer: B** — This reframing kills most arguments: if you write the ADR with the trigger, you have converted debt into a decision. The debt is shortcuts *and* missing ADRs together.

---

**Q12. What is the most common failure mode of architecture decision-making in large teams?**
- A) Too many decisions
- B) Decisions made without a decision-maker: the loudest participant wins, or the decision is deferred until a default (an existing system, a vendor's recommendation) effectively makes it. Absence of an explicit owner and an explicit decision is the most common way architecture happens by accident
- C) Bad technology choices
- D) Too many ADRs

**Answer: B** — Naming a decision-maker and requiring an explicit "decided" or "deferred" outcome, with a default, is the cheapest governance improvement available.

---

**Q13. When should you choose the "boring" option?**
- A) Never; innovate
- B) When the differentiation is not in this layer, when the operational maturity cost of the novel option exceeds the value, and when you lack the people to run it. Novelty is a cost: it is unproven under your load, undocumented in your context, and it makes hiring and on-call harder
- C) Boring always
- D) When there is no time

**Answer: B** — The interesting quote for a staff engineer: **"the most revolutionary thing you can do is stop choosing revolutionary technology."** Novelty should be spent where it differentiates the product.

---

**Q14. What is the right way to handle a decision that is genuinely uncertain?**
- A) Pick the safest and move on
- B) Reduce the decision's size: make it reversible, split it (decide the interface now, the implementation later), or run the smallest experiment that would resolve the uncertainty. Most irreversibility comes from committing early to a wide surface, not from the technology
- C) Wait for certainty
- D) Ask the vendor

**Answer: B** — Interfaces are the cheap commitment; implementations are the expensive ones. Deciding an interface early is usually safe; deciding an implementation early usually is not.

---

**Q15. What separates a staff/principal engineer's architecture decisions from a senior's?**
- A) Better technology choices
- B) Scope and consequence: the principal decides fewer, later, more reversibly-decided things, writes down the reasoning so the organisation can act without them, chooses boundaries over components, and spends novelty budget where it differentiates. The measure is whether the team's decisions continue to be correct when they are not in the room
- C) More ADRs
- D) Longer documents

**Answer: B** — The practical test: does the system still make sense when the person who designed it has left? If the reasoning is only in one person's head, it is not architecture.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and write real ADRs.
- 12–10: revisit ADR structure, TCO, and revisit triggers; redo EXERCISES 2–5.
- <10: re-read THEORY + `ARCHITECTURAL_FITNESS_METRICS` cold and retake in 48 hours.
