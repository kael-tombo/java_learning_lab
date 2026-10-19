# Mini Project: Transaction Management

## The assignment

This transaction management mini build produces a working community-bank transfer ledger you can run locally.
Scope stays deliberately small so every transaction management behavior remains observable.
Budget roughly one focused evening for the community-bank transfer ledger implementation.
Success means demonstrating transaction management judgment, not just compiling code.
Keep a lab journal noting each transaction management surprise encountered.
Nothing joins the work beyond what the acceptance checks already ask for.

## Parts you will wire

- ACID guarantees in practice.
- ReadCommitted versus RepeatableRead concepts.
- Serializable isolation trade-offs.
- Propagation across service calls.
- Rollback rules for failures.

## Build order

1. Model accounts and transfers with balance invariants for the service.
2. Move money between two accounts inside one transaction.
3. Demonstrate a dirty-read hazard and then its isolation fix.
4. Nest a fee-posting call with explicit propagation choice.
5. Prove a mid-transfer failure leaves both balances untouched.

## Acceptance checks

- [ ] 100 seeded accounts balance to the audited control total after every run in the solution.
- [ ] Transfer of 5 consecutive amounts preserves the ledger total in the platform.
- [ ] Isolation demonstration shows the anomaly before and the fix after.
- [ ] Failed transfer leaves zero partial postings across 10 attempts.
- [ ] Concurrent transfers never drive any balance negative.

## Stretch

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which transaction management decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
