# REAL_WORLD_PROJECT — Logic & Proofs in Production: Policy Spec Validator
> Production use-case: validating that a policy's rules don't contradict each other.

## 1. Scenario
- Service: admin tool encodes access rules as boolean formulas.
- Constraint: two rules must not allow-and-deny the same access.
- Choice: translate rules to propositional logic; check satisfiability of the conjunction.
- Data: `Rule{subject, action, condition}` → proposition.

## 2. Architecture
```
rules → to-DNF → SAT check on (allow_i ∧ deny_i) pairs → report conflicts
```

## 3. War-Story (plausible, representative)
- Incident: a "deny interns billing" rule was silently overridden by a later allow.
- Root cause: precedence was implicit; no consistency check ran.
- Fix: SAT check on merge; conflicts block the deploy.
- Lesson: boolean logic is code — CI it.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| contradictory rule pairs/quarter | 4 | 0 |
| deploy blocks for contradiction | 0 | 7 (safe) |

## 5. Prevention Checklist
- [ ] SAT check in CI and at deploy.
- [ ] Every allow/deny logs the fired rule.
- [ ] Deny-by-default on parse failure.
- [ ] Golden contradictory fixtures.

## 6. What "Good" Looks Like
- No contradictory policies reach production.

## 7. Stretch
- SMT (Z3) for conditions with arithmetic.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Boolean satisfiability problem: https://en.wikipedia.org/wiki/Boolean_satisfiability_problem
- Propositional calculus: https://en.wikipedia.org/wiki/Propositional_calculus
