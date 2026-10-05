# MINI PROJECT — OOP Basics: Library Lending Domain

## Goal (2 weeks, ~8–10h)
Model a library (Book/Member/Loan) with airtight encapsulation: invariants enforced in constructors, no anemic getters/setters abuse.

## Requirements
### Functional
1. `Book` (ISBN validated, copies), `Member` (max 5 loans), `Loan` (due date, `returnBook()`, overdue fee via BigDecimal).
2. Factories: `Book.of(...)`, `Member.register(...)`; `record LoanReceipt(...)` for data-out.
3. Business rules: no loan when no copies; no loan when member at cap/overdue; immutable due dates (`LocalDate` defensive view).
4. `Library` service: checkout/return/check-overdue; in-memory with `List`.
### Non-functional
- Zero public mutable fields; `final` where possible; invariant documented per class.
- 20+ tests: cap, no-copies, overdue fee rounding, ISBN validation.
- UML-ish ASCII diagram in README.

## Phases
### Week 1 — Model (4–5h)
- Classes + factories + validation; invariant list.
- Deliverable: compiles + 10 invariant tests.
### Week 2 — Service + Rules (4–5h)
- Library service, fee calc, overdue scan, README diagram.
- Deliverable: demo script (checkout/return/overdue trace).

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Encapsulation | Private+validated, final | Mostly closed | Public fields |
| Factories/records | Named, intent-revealing | Present | Only raw ctors |
| Rules enforced | All + tested | Core tested | Rules in UI layer |
| Immutability | Defensive, final | Partial | Leaked mutables |
| Diagram/tests | Clear + 20 | Present/12+ | Missing |

Pass ≥ 70. Stretch: reservation queue; fine-policy strategy stub.
