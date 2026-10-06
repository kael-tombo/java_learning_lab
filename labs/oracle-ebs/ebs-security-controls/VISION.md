# EBS Security Controls — Vision

## Where this lab takes you
From how a sign-on request actually flows to proving to an auditor that no user
holds a conflicting role — the full EBS security model end to end.

## The Arc
1. **Sign-on** — the authentication flow and where it can fail.
2. **Responsibility security** — the context every other control hangs off.
3. **Function, form, data security** — narrowing within a responsibility.
4. **Row-level** — VPD and `FND_MOBS` for tenant-style scoping.
5. **Users** — provisioning, password policy, and dormancy.
6. **SOD** — designing conflicts and enforcing them preventively.
7. **Crypto** — TLS in transit, TDE and encryption at rest.
8. **Audit** — what to log, where it goes, and who reviews it.

## Milestones (checkable)
- [ ] M1: Trace the sign-on flow and name each failure point.
- [ ] M2: Explain the responsibility context and why it governs everything.
- [ ] M3: Apply function security to narrow a responsibility safely.
- [ ] M4: Implement row-level security with `FND_MOBS`/VPD on one table.
- [ ] M5: Set a password policy and demonstrate lockout behaviour.
- [ ] M6: Build an SOD conflict matrix and detect a real violation.
- [ ] M7: Enable TDE for tablespace-level encryption and verify it.
- [ ] M8: Produce an audit report an external auditor would accept.

## Anti-Goals
- Treating the profile as a security boundary rather than a convenience.
- Granting a role to fix an access problem and leaving the SOD conflict.
- Logging everything and reviewing nothing.
- Assuming network placement is a substitute for authentication.

## The one-sentence thesis
EBS security is layered and contextual — a user with the right responsibility
can still be denied by a data-level rule, and that is the point.