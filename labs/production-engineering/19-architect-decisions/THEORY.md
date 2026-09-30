# THEORY: Architecture Decisions & Trade-Off Engineering
## Lab 19 | Production Engineering Academy

---

## 1. Michael Nygard Architecture Decision Record (ADR) Structure

An Architecture Decision Record captures an important architectural decision made along with its context and consequences:

1. **Title**: Short noun phrase with sequential ID (e.g. `ADR-042: Adoption of Kafka over RabbitMQ for Ledger Events`).
2. **Status**: `PROPOSED`, `ACCEPTED`, `REJECTED`, `DEPRECATED`, `SUPERSEDED by ADR-xxx`.
3. **Context**: The business, organizational, or technical forces influencing the decision (facts only, non-judgmental).
4. **Decision Drivers**: The non-negotiable requirements (e.g. p99 latency $< 50\text{ms}$, financial auditability, zero data loss).
5. **Considered Options**: Unbiased evaluation of all viable alternatives with pros and cons.
6. **Decision Outcome**: The chosen option and explicit rationale.
7. **Consequences**:
   - *Positive*: Benefits realized.
   - *Negative / Trade-offs*: Costs, risks, and technical debt accepted.
   - *Compliance / Operational Impact*: What teams must do differently.

---

## 2. Reversible (Type 2) vs Irreversible (Type 1) Decisions

Jeff Bezos's framework applied to software architecture:
- **Type 1 (One-Way Doors / Irreversible)**:
  - Decisions that are extremely costly, risky, or almost impossible to reverse once executed.
  - Examples: Core database engine selection (e.g. PostgreSQL vs Cassandra), multi-tenant vs single-tenant database partitioning, primary programming language runtime, external cloud provider.
  - *Process*: Require rigorous RFC reviews, prototyping, benchmark data, and consensus among Principal Architects.
- **Type 2 (Two-Way Doors / Reversible)**:
  - Decisions that can be easily undone with low blast radius if proven suboptimal.
  - Examples: Library selection for JSON parsing, local caching strategy, internal REST endpoint URL path.
  - *Process*: Encourage rapid experimentation; empower individual engineering teams to decide without bureaucratic delays.

---

## 3. Multi-Criteria Trade-Off Matrices & Cost of Delay

When choosing between architectures, subjective opinions cause paralysis. Architects use quantitative trade-off matrices:

$$\text{Option Score} = \sum_{i=1}^{n} (\text{Weight}_i \times \text{Rating}_{i})$$

Criteria weights ($1-5$):
- Developer Velocity
- Operational Complexity
- Total Cost of Ownership (TCO)
- Fault Tolerance / Availability
- Latency / Throughput Scalability
