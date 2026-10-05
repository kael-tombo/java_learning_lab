# MINI PROJECT — Polymorphism: Payment Plugin Hub

## Goal (2 weeks, ~8–10h)
Ship a checkout hub where adding a payment method = adding one class, zero `if (type)` edits — polymorphism doing its job.

## Requirements
### Functional
1. `Payment { authorize/capture/refund }`; impls: `Card`, `PayPal`, `BankTransfer`, `CryptoStub`; factory via `Map<String,Supplier<Payment>>`.
2. Checkout depends only on `Payment`; covariant `Receipt` returns; `instanceof`-pattern only in factory/adapter, never in core.
3. Add-4th-method drill: PR diff must show no hub/checkout file touched (CI-checkable via `git diff --name-only`).
4. Failure simulation: each method has decline path; uniform `PaymentException` (unchecked) with code.
### Non-functional
- 18+ tests incl. "add type without hub edit" + mock-decline matrix.
- Overload set audited for ambiguity; dynamic-dispatch sequence diagram in README.
- Logs show runtime class handling each call.

## Phases
### Week 1 — Core + 2 methods (4–5h)
- Interface, Card/PayPal, factory registry, checkout flow.
- Deliverable: 2-method checkout demo.
### Week 2 — Extend + Prove (4–5h)
- Add Bank/Crypto, no-touch proof, decline matrix.
- Deliverable: diff proof + failure table.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Zero-touch extend | Proved via diff | Claimed+tested | Hub edited |
| Supertype design | Checkout type-blind | Mostly | Type checks in core |
| Factory/patterns | Registry, pattern-match | Simple factory | if-chains |
| Failure model | Uniform codes+tests | Basic | Silent nulls |
| Overload hygiene | Audited | OK | Ambiguous |

Pass ≥ 70. Stretch: SPI `ServiceLoader` discovery; strategy-fee composition.
