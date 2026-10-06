# Lab 19: Java Architect Decision Framework — Flashcards

~60 cards. Most answers are a structure, a question, or a rule.

---

## ADR structure

Q: What are the standard ADR sections?
A: Title, Status, Context, Decision, Alternatives considered, Consequences (positive and negative), Revisit trigger. Optional: decision date, decider, links to evidence.

Q: Status values?
A: Proposed, Accepted, Rejected, Deprecated, Superseded by ADR-NNNN. Never "In progress" without an owner.

Q: Immutable?
A: Body is immutable once Accepted. To change it, write a new ADR and mark the old one Superseded. Editing history destroys the reasoning.

Q: Length?
A: One page is usually right. If it needs ten pages, it is a design document with a decision at the top — split it.

Q: What is the most valuable section?
A: Consequences with the negatives, and the Revisit trigger.

Q: When does an ADR not need to exist?
A: Cheap, local, easily reversible changes: a library bump, a config value, a private method.

Q: When does it?
A: Expensive to reverse, cross-team, or release-crossing; new dependency or platform commitment; constrains future options.

Q: Who writes it?
A: The person closest to the decision, with the decider accountable for the outcome. Do not delegate the writing to a committee.

Q: Where do ADRs live?
A: In the repository, as `adr/NNNN-title.md`, reviewed like code. Not in a wiki nobody can find.

Q: Does an ADR need a diagram?
A: Only if it clarifies. A diagram with three boxes adds nothing; a data-flow that explains a boundary can save a page.

---

## Content of a decision

Q: Context must contain?
A: The forces: business drivers, technical constraints, team skills, time pressure, existing investments, and what is already expensive to undo. If the context omits the time pressure, the decision is not explainable.

Q: Decision must contain?
A: What exactly, stated so an implementer can act on it, including the boundary and the contract.

Q: Alternatives must contain?
A: Each real option considered, with the specific reason it lost *under the current forces*. "We did not like it" is not a reason.

Q: Consequences must contain?
A: Positive and negative, the obligations accepted, the ongoing cost, and what becomes harder.

Q: Revisit trigger?
A: An observable condition: a metric threshold, a volume threshold, a date, a staffing change, or a dependency release. It makes the decision conditional and checkable.

Q: Good examples of revisit triggers?
A: "If our read:write ratio exceeds 20:1"; "if consumer lag p99 exceeds 5 min at peak"; "if the on-call rotation exceeds 2 pages/shift"; "if the vendor deprecates the API we depend on".

Q: Bad examples?
A: "If it does not scale" (not observable), "in two years" (a date, not a trigger), "if we have time" (not observable).

Q: Record what you rejected *because of a risk*, and name the risk?
A: Yes — "rejected because its single-writer model cannot meet our 40k msg/s peak; revisit if our peak falls below 15k msg/s". Now the rejection is reversible knowledge rather than a lost option.

---

## Evaluating options

Q: TCO components?
A: Infrastructure/licence, implementation and migration effort, operational cost (on-call load, failure modes, upgrade pain), exit cost (data migration, API compatibility, retraining), opportunity cost of the time not spent elsewhere.

Q: What is usually the largest TCO term and most often omitted?
A: Exit cost, followed by opportunity cost.

Q: Build vs buy — who decides?
A: Engineering assesses technical and operational fit; the business weighs differentiation, lock-in, and TCO over the horizon. Usually: buy the commodity, build the differentiator.

Q: What is "not building it" worth?
A: The opportunity cost. Six engineer-months spent on a commodity authentication service is six engineer-months not spent on the product. Always price it.

Q: Quantify reliability in the comparison?
A: Give each option an expected-annual-loss estimate (Lab 14/18 arithmetic). It makes "more reliable" comparable to "cheaper".

Q: Quantify latency?
A: Model it (Lab 15): capacity, saturation point, and whether the option can meet the SLO at peak.

Q: How many options should a serious decision present?
A: Two to four real ones. A list of eight is a sign you have not chosen, and it hides the actual trade-off.

---

## Making it reversible

Q: What makes a decision irreversible?
A: Data written in a format you cannot read elsewhere, an API contract consumed by parties you do not control, a commitment of people rather than code, and a vendor dependency with a proprietary protocol.

Q: What is cheap to commit to early?
A: Interfaces and boundaries: the API shape, the event schema, the module boundary. Expensive: the implementation behind them.

Q: Techniques for reversibility?
A: Adapters at boundaries, feature flags for behaviour changes, a strangler pattern for migrations, dual-write with a planned cutover, and an explicit exit plan written *before* adoption.

Q: Should the exit plan be an ADR?
A: Yes, or a section of the ADR: how you would leave, what it costs, and who does it.

Q: When is a big-bang migration justified?
A: When the coupling is at the data layer, the system is small, downtime is acceptable, and there is no incremental path. Be honest about it; do not default to it.

---

## Process and governance

Q: Who decides?
A: Name a single decider. Consult widely; decide with one owner. Consensus is not a decision procedure.

Q: What happens without an explicit decider?
A: The loudest participant wins, or the default (existing system, vendor recommendation) decides by omission. This is the most common way architecture happens by accident.

Q: Every decision must end in what two states?
A: Decided (with an ADR) or explicitly deferred (with an owner, a date, and what will resolve it). There is no third state.

Q: When does a decision need review by a principal/staff engineer?
A: Cross-team, expensive to reverse, novel dependency, or an entry point that couples teams. Not every local decision.

Q: How long should a decision take?
A: Enough to hear the people who will live with it. Days, not months — a slow decision is usually an unstated disagreement, and surfacing it is faster than more documents.

Q: What is "decision debt"?
A: Decisions made implicitly and never written down, which are unreviewable, unrevisitable, and invisible to newcomers. It compounds faster than technical debt.

Q: How do you keep ADRs discoverable?
A: Numbered files in the repo, an index with titles and statuses, and a rule that a change touching a superseded decision must cite the superseding ADR.

---

## Explaining decisions upward

Q: What does a business audience need?
A: Options with cost, risk, and business consequence; a recommendation with reasoning; the explicit decision you need (budget, deadline, accepted risk); and what happens if we do nothing.

Q: What must never go in?
A: Technology preference, framework names, internal jargon. "We need 2 engineer-weeks and the alternative is a 3%-of-revenue incident risk" is the message.

Q: Frame the status quo?
A: Always include "no decision / continue as-is" as an option with its cost. It is usually cheaper than people assume, and its presence makes the ask legitimate.

Q: Present the risk in expected value?
A: Yes — `P(impact) × cost`, and a range, not a point estimate. Businesses discount expected values; give them the range and the worst case.

Q: Who signs off?
A: Whoever owns the budget or the risk. Make it explicit in the ask so no one assumes they already approved it.

---

## Boring technology and novelty

Q: When choose the boring option?
A: When the differentiation is not in this layer, when operational maturity cost exceeds value, and when you lack the people to run it.

Q: What does novelty cost?
A: Unproven under your load, fewer docs for your context, harder hiring, more on-call, and a bigger blast radius on failure.

Q: Where should novelty budget go?
A: Where it differentiates the product — the algorithm, the user experience, the domain logic — not in the persistence layer or the deployment substrate.

Q: "Second adopter" strategy?
A: Use a technology in a non-critical service first, learn it, then adopt in the critical path. Converts novelty risk into a bounded experiment.

Q: What is the real argument for a mature technology?
A: Predictability under failure and the size of the on-call burden — not performance, which is usually comparable.

---

## Technical debt and trade-offs

Q: Definition of technical debt?
A: A deliberate suboptimal choice *without a plan to return*. A documented trade-off with a revisit trigger is engineering, not debt.

Q: The real debt is?
A: Shortcuts **and** missing ADRs. Undocumented decisions are unrevisitable.

Q: How to pay down debt without a hero?
A: Tie repayment to change: "every change to this module must leave the seam cleaner", plus a standing 10–15% allocation that is protected in planning.

Q: Interest on debt?
A: `interest = frequency_of_change × cost_of_confusion`. A badly factored module nobody touches costs nothing; the one we change weekly costs the most.

Q: How do you make a trade-off visible?
A: An ADR with the negative consequences and a trigger. Then it appears in every discussion of that area, which is the entire point.

---

## Scaling decisions

Q: When does a single service become a platform problem?
A: When N teams are blocked on the same deployment, on-call, or data access pattern — the shared cost crosses a threshold where standardising beats duplicating.

Q: Platform as a product?
A: Publish an SLO, a support model, a deprecation policy, and an adoption path. A platform without a support model is a bottleneck with good branding.

Q: What is a good architectural boundary?
A: One that changes for one reason — a business capability, an ownership boundary, a data ownership boundary, or a scaling characteristic. Boundaries defined by technology rather than by reason tend to leak.

Q: When do you need a platform team at all?
A: When there are enough teams to amortise it, and the shared problem is genuinely shared. One team does not need a platform; it needs fewer tools.

Q: What is a "reverse API"?
A: An internal API designed from the consumer's needs and owned by the consumer, so the provider cannot break it unilaterally. Powerful for unpicking an unwanted dependency.

Q: When is a monolith the right answer?
A: More often than fashionable. A modular monolith with enforced boundaries gives you most of the benefit of separation at a fraction of the operational cost. Split when a specific scaling, ownership, or release need is demonstrated.

---

## Numbers and defaults to memorize

Q: ADR length?
A: About one page. Longer means it should be split into a design document plus a decision.

Q: How many alternatives?
A: Two to four real ones.

Q: Decision deadline?
A: Days, not months. A slow decision is an unstated disagreement.

Q: What an ADR must always contain?
A: Status, context, decision, alternatives with reasons, positive *and negative* consequences, and a revisit trigger.

Q: TCO horizon?
A: The expected life of the decision — typically 3 years for infrastructure.

Q: Novelty budget?
A: Spend it where the product differentiates; treat everything else as a place to be boring.

Q: Minimum viable governance?
A: A named decider, and every decision ending in "decided" or "deferred with an owner and a date".

Q: When to revisit a decision?
A: When its stated trigger fires — objectively, not on feeling.

Q: Debt repayment allocation?
A: ~10–15% of engineering time, protected, plus "leave it cleaner" on every change.

Q: Platform trigger?
A: When the shared cost of N teams exceeds the cost of standardising.
