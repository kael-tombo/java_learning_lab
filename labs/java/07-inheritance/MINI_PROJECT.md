# MINI PROJECT — Inheritance: Payroll Hierarchy (then Compose)

## Goal (2 weeks, ~8–10h)
Build a payroll hierarchy that starts with `extends`, proves Liskov pain, then refactors half to composition — learning when not to inherit.

## Requirements
### Functional
1. v1: `Employee` ← `Salaried`, `Hourly`, `Contractor`; `pay()` polymorphic; `super(...)` chaining; `final` helper `annualize()`.
2. Liskov demo: `Contractor extends Employee` breaks `benefits()` — document violation + failing test kept as proof.
3. v2: extract `PayPolicy` interface; `Employee` composes policy (strangler); keep one legit `extends` (e.g., `Manager extends Salaried` with invariant preserved).
4. `equals/hashCode`: final classes or composition-forwarding; symmetry tests.
### Non-functional
- Never call overridable method from constructor (static check in review).
- 18+ tests: pay math, Liskov proof, symmetry, constructor-chain order log.
- README: is-a justification per remaining `extends`.

## Phases
### Week 1 — Hierarchy (4–5h)
- Base + 3 subtypes, pay calc, Object overrides.
- Deliverable: v1 tag + Liskov failing test.
### Week 2 — Refactor (4–5h)
- PayPolicy composition, migration tests, justification doc.
- Deliverable: before/after diagram + review notes.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Chaining/final | Correct order, logged | Works | super bugs |
| Liskov proof | Failing test + doc | Described | Ignored |
| Refactor | Policy-composed, tested | Partial | Still deep tree |
| equals/hash | Symmetric, tested | Works happy | Broken |
| Justification | Each extends defended | Present | Missing |

Pass ≥ 70. Stretch: sealed `Employee` permits list; template-method audit log.
