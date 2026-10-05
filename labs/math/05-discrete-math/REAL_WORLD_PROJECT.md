# REAL_WORLD_PROJECT — Discrete Math in Production: Access-Control Policy Evaluator
> Production use-case: deciding allow/deny with provably consistent rules.

## 1. Scenario
- Service: internal admin tool evaluates RBAC/ABAC policies per request.
- Constraint: policies must be explainable; contradictory rules fail closed.
- Choice: encode rules as boolean formulas; check satisfiability before deploy.
- Data: `Policy{role, resource, action, condition}` → proposition per rule.

## 2. Architecture
```
policy repo → parse to boolean exprs → SAT-style consistency check → decision engine → audit log
```
- Every allow/deny logs the rule chain that fired (explanation).
- Nightly job re-validates all policy combos for new contradictions.

## 3. War-Story (plausible, representative)
- Incident: a "deny interns from billing" rule was silently overridden by a later "allow finance-view".
- Symptom: intern pulled a billing report; audit found the gap weeks later.
- Root cause: rule precedence was implicit; no consistency proof ran on merge.
- Fix: explicit precedence + deploy-time contradiction check; conflicting pairs block rollout.
- Lesson: boolean logic needs the same rigor as code — prove, don't assume.

## 4. Metrics (before → after, one quarter)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| contradictory rule pairs in prod | 4 | 0 | −100% |
| unexplained denies | 60% | 0% | −100% |
| policy deploy failures (contradiction) | 0 (silent) | 7 blocked | safer |
| audit finding time | weeks | same day | −95% |

## 5. Prevention Checklist
- [ ] Precedence explicit in policy schema; no "last write wins".
- [ ] Contradiction check runs in CI and at deploy.
- [ ] Every decision logs fired rules.
- [ ] Deny-by-default on parse failure.
- [ ] Randomized fuzzing of policy inputs vs spec oracle.
- [ ] Review checklist: is the intended semantics actually the written formula?
- [ ] Cache decision per (role,resource,action) with TTL.
- [ ] Dashboard: deny rate, contradiction count, deploy blocks.

## 6. What "Good" Looks Like
- Security can explain any decision in one sentence from the log.

## 7. Stretch
- Graduate to SMT solving (Z3) for richer conditions (see 15-numerical-methods contrasts).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Propositional logic: https://en.wikipedia.org/wiki/Propositional_logic
- SAT solving: https://en.wikipedia.org/wiki/Boolean_satisfiability_problem
