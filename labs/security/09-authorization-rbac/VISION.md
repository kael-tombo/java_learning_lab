# VISION — Authorization & RBAC: From Roles to Policy
> Where this lab takes you: from `hasRole("ADMIN")` to a model that handles per-tenant, per-resource, and contextual decisions.

## The Arc
1. **Vocabulary** — authentication vs authorization, subjects, objects, actions, and policies.
2. **RBAC** — role hierarchies, privilege creep, role explosion, and the flat-role trap.
3. **Beyond roles** — ABAC attributes, ReBAC relationships, permission-based checks.
4. **Enforcement** — deny by default, layering (URL + method + data), and TOCTOU gaps.
5. **Multi-tenancy** — tenant-scoped authorization, row-level security, and isolation testing.

## Milestones (checkable)
- [ ] M1: convert a set of scattered `if (user.isManager())` checks into a named permission model.
- [ ] M2: detect privilege escalation from role hierarchy design in under five minutes.
- [ ] M3: express "can access this record" with an attribute check that roles cannot capture.
- [ ] M4: implement deny-by-default and write a test proving a new endpoint is closed by default.
- [ ] M5: demonstrate a cross-tenant access attempt and the test that catches it.

## Core Competencies
- RBAC vs ABAC vs ReBAC decision, and hybrid designs that stay comprehensible.
- Deny-by-default policy, fail-closed on missing attributes, and least privilege by construction.
- Service-layer enforcement so internal calls are covered, not just HTTP entry points.
- Auditing every authorization decision with subject, action, resource, and outcome.

## Anti-Goals
- Checking authorization only in controllers, leaving the service layer open.
- Wildcard `ROLE_ADMIN` grants in a system with tenant boundaries.
- Trusting a role claim for a decision that depends on record state.

## Interview Lens
- "How do you authorize 'edit this order' when the answer depends on status and region?"
- "Where do you enforce authorization for a message consumer with no HTTP request?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: map an existing app's authorization logic.
- Wk2 QUIZ/FLASHCARDS to 90%+; implement permission checks with a guard bean.
- Wk3 MINI_PROJECT with RBAC + attribute rules.
- Wk4 REAL_WORLD_PROJECT: multi-tenant policy engine and isolation test suite.

## Done = You Can
- Replace scattered ad-hoc checks with a single auditable policy layer, and prove no
  bypass exists via HTTP, service, or message-driven entry points.
