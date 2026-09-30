# INTERVIEW QUESTIONS: Architecture Decisions & Trade-Off Engineering
## Lab 19 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What makes a good Architecture Decision Record (ADR), and why must it include negative consequences?
**Answer**:
A good ADR captures the context, decision drivers, considered alternatives, and outcomes at a specific point in time. It is vital to document negative consequences and accepted trade-offs because every real architectural decision involves trade-offs (e.g. choosing Kafka provides high throughput and durability, but increases operational complexity and requires consumer lag management). If an ADR only lists benefits, it indicates that the author has not fully understood the costs or failure modes. Documenting trade-offs prevents future engineers from wondering "Why did they make this terrible choice?" when operational challenges arise later.

---

## Staff / Principal Level (8+ Years)

### Q2: Contrast Type 1 (Irreversible) vs Type 2 (Reversible) decisions in enterprise software architecture. How do you govern each?
**Answer**:
- **Type 1 (One-Way Doors)**: Decisions that have high switching costs, multi-year lock-in, or severe data risk (e.g. primary cloud provider, fundamental data storage paradigm like relational vs graph, choosing between microservices vs modular monolith).
  - *Governance*: Require rigorous multi-stakeholder RFC reviews, proof-of-concept prototypes, quantitative benchmark data, formal Architecture Review Board sign-off, and explicit exit strategies.
- **Type 2 (Two-Way Doors)**: Decisions that can be easily undone with low blast radius (e.g. choice of JSON parsing library, internal naming conventions, caching algorithm).
  - *Governance*: Must be decentralized to autonomous development teams. Requiring central approval for Type 2 decisions paralyzes developer velocity and creates an inefficient bureaucracy.
