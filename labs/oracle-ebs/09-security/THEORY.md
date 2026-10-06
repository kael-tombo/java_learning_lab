# Lab 09: Security (SOD Remediation) — Theory

## The Scenario

Internal audit at a financial services client found 45 users holding conflicting
responsibilities. Users in the AP "Manager" responsibility can create suppliers,
approve invoices, and process payments — all without secondary approval. The
audit committee demands immediate remediation.

## Principle 1: SOD conflicts are fraud enablers, not rule violations

The fraud pattern SOD prevents:

```
Create supplier   →  a supplier you control
Create invoice    →  a bill for that supplier
Approve invoice   →  authorise your own bill
Process payment   →  take the money
Net result        →  money leaves the company, and the audit trail shows
                     one person did everything legitimately
```

Each step is permitted by the system. The system behaved correctly. **The
control failure is the absence of a conflict rule**, not any single permission.

This is why SOD cannot be fixed by tightening individual permissions. Removing
"create supplier" from everyone breaks the business. The control is the
**separation between steps**, not the absence of steps.

## Principle 2: A risk matrix makes SOD auditable

"SOD conflicts" is not an enforceable concept. It must be enumerated:

```
Duty A: Create supplier      (PO_VENDOR)
Duty B: Approve invoice      (AP_INVOICE_APPROVAL)
Duty C: Process payment      (AP_PAYMENT_PROCESS)
Duty D: Maintain GL          (GL_JOURNAL_CREATE)
Duty E: Execute reports      (PAYMENT_EXECUTE_REPORT)

Conflicts:
  A ↔ B   Supplier master vs invoice approval   — vendor creation bias
  A ↔ C   Supplier master vs payment execution
  B ↔ C   Invoice approval vs payment execution — the classic AP fraud
  B ↔ D   Invoice approval vs GL maintenance
  C ↔ E   Payment execution vs payment report    — conceal by omission
  D ↔ E   GL maintenance vs payment report
```

**Without this enumeration, no detection query can be written.** With it, each
conflict becomes a specific, testable rule. This artefact is also what an auditor
will ask for: "show me your risk matrix".

## Principle 3: Detection requires self-joins on the user, not the responsibility

The query shape matters enormously:

```sql
-- WRONG: finds responsibilities that conflict with each other
-- This detects bad DESIGN of the responsibility, not bad ASSIGNMENTS.
SELECT * FROM fnd_responsibilities r1, fnd_responsibilities r2
 WHERE r1.responsibility_name LIKE 'AP%'
   AND r2.responsibility_name LIKE '%PAYMENT%';
```

```sql
-- RIGHT: finds USERS who hold conflicting duties
SELECT fu.user_name, r1.responsibility_name duty_a, r2.responsibility_name duty_b
  FROM fnd_users fu
  JOIN fnd_user_responsibilities ur1 ON ur1.user_id = fu.user_id
  JOIN fnd_user_responsibilities ur2 ON ur2.user_id = fu.user_id AND ur2.responsibility_id <> ur1.responsibility_id
  JOIN fnd_responsibilities r1 ON r1.responsibility_id = ur1.responsibility_id
  JOIN fnd_responsibilities r2 ON r2.responsibility_id = ur2.responsibility_id
 WHERE r1.responsibility_name = 'AP Supplier Maintenance'
   AND r2.responsibility_name = 'AP Payment Processing';
```

The violation is a property of a **user's assignment set**, not of any single
responsibility. Every one of the three responsibilities may be individually
reasonable; the combination is the problem.

## Principle 4: Remediation has a business cost, so it must be sequenced

Revoking 45 users' access without a plan stops the business. The sequence:

```
1. RISK-RANK     — by value at risk, not by user count
2. PATH-REPLACE  — identify who can perform the duty today
3. ALTERNATE     — reassign to a compliant user, or split the work
4. REMOVE        — revoke the conflicting responsibility only
5. EXCEPTION     — where removal is impossible, document and time-box
6. VERIFY        — re-run detection; the count must fall
```

**Remove only the conflicting responsibility, not the whole role.** A user who
needs supplier creation for their job keeps it; what they lose is the ability to
also process payments. Over-revocation creates workarounds — shared logins,
manual approvals by email — which are *worse* controls than the original
violation.

### Over-remediation is a real failure mode

```
Violations found:              45
Users remediated correctly:    45
Workarounds created:           12 shared logins, 30 email approval trails
Actual control state:          WORSE than before
```

The audit finding is closed and the risk is higher. This is why exceptions with
owners and expiry dates are legitimate: a managed exception is a control, an
unmanaged workaround is not.

## Principle 5: Detective control finds the past; preventive control stops the future

```
DETECTIVE  — monthly SOD report, findings after the fact
PREVENTIVE — block the assignment at grant time
```

Both are required. A detective control alone means every month you find new
violations. A preventive control alone means you never discover the conflicts
that already exist.

**Preventive implementation options** (in increasing order of strength):

| Option | Mechanism | Strength |
|--------|-----------|----------|
| Report only | Query | Detective only |
| Email alert on assignment | Trigger on `FND_USER_RESPONSIBILITIES` | Delayed detective |
| Approval workflow | Assignment triggers approval | Strong preventive |
| **Enforced block** | Assignment fails on conflict | Strongest |

The enforced block is the goal. It converts "we will catch this" into "this
cannot happen".

## Principle 6: Exceptions must be time-bound and owned

Some conflicts cannot be removed:

- A one-person finance team genuinely cannot separate duties.
- A segregation requirement is waived for a system during a migration.
- A small entity's controller legitimately does both.

The legitimate form:

```
Conflict:        AP Supervisor (approve) + AP Payment Processing
User:            J. Smith, Controller
Business reason: Entity has 3 finance staff; no fourth to separate payment
Compensating control: Payments > $50K require CFO email approval (documented)
Owner:            CFO
Expires:          2027-03-31  ← NOT "indefinite"
Review:           Quarterly by the audit committee
```

**"Indefinite" is not an exception; it is an undocumented acceptance of risk.**
Every exception needs an expiry date, and expiry must be enforced by a report
that lists overdue exceptions.

## Principle 7: Certification is a control activity, not a report

Monthly certification:

```
Report produced → Manager reviews → Attests: correct / incorrect / accept risk
               → Incorrect → remediated
               → Accept risk → exception logged with owner + expiry
               → Evidence retained (who certified what, when)
```

The value is the **attestation**, not the report. A report nobody signs proves
nothing. The evidence trail — who certified, on what date, with what decision —
is what an auditor examines.

## Principle 8: Hardening findings are not SOD findings but travel together

Audit found three distinct issues:

| Finding | Nature | Control |
|---------|--------|---------|
| 45 SOD conflicts | Control design | SOD risk matrix + preventive control |
| 12 dormant accounts with elevated access | Access management | Dormancy review + auto-deactivation |
| `FND_HIDE_DB_PASSWORD='N'` | Information disclosure | Set to `Y`, scan for recurrence |

### Why password visibility matters

`FND_HIDE_DB_PASSWORD='N'` exposes database credentials in:

- The "Check Connectivity" diagnostic page
- Support request logs
- Screenshots in tickets
- Session recordings for training

```
Exposed credential → read access to the EBS database schema
                    → direct table access, bypassing ALL EBS security
```

**This is a privilege escalation path that bypasses the entire security model.**
Every application-layer control is irrelevant if the DB password is visible.

### Dormant accounts

A dormant account with elevated access is pure risk:

```
Last signin: 8 months ago
Still holds:  AP Payment Processing

Probability it is needed: ~0
Probability it is compromised: non-zero
```

Dormancy is the strongest single indicator for unused-account compromise.
Auto-deactivation after a defined period (90 days) with an exception process is
the control.

## Principle 9: Least privilege must be measured, not asserted

Two reports that must exist:

```
JUST-IN-TIME (roles held by fewer than N users)
                    → likely over-provisioning
STALE PRIVILEGE   (roles held by users who changed function)
                    → access from a previous job
```

```
Users holding 3+ AP responsibilities:  45
Users whose current job requires fewer:   38
Excess assignments removable:             ~90
```

Remediation of the 45 SOD violations usually uncovers a larger set of stale
privileges. Treating the SOD finding as a data cleanup exercise rather than a
fraud-control exercise means missing that.

## Principle 10: The 30-day window is a constraint, not a plan

```
Days 1-7:   Analysis — risk matrix, detection query, risk ranking
Days 8-14:  Design — preventive control, remediation scripts, exception form
Days 15-21: Pilot — remediate one business unit, validate no disruption
Days 22-26: Execute — remaining units, business-signed
Days 27-30: Verify — re-run detection, evidence pack, audit committee
```

**The buffer is days 27–30, and it exists because remediation always reveals
more than the initial scan.** If discovery is continuous, the plan must have a
verification phase or the audit committee meets with an open finding.

## Diagnostic Order

1. Enumerate duties and conflicts into a risk matrix (before any query).
2. Detect at the user-assignment level, not the responsibility level.
3. Risk-rank by value at risk, not by count.
4. Sequence remediation with an alternate path for each removed duty.
5. Implement preventive blocking at grant time.
6. Log time-bound exceptions with owners and compensating controls.
7. Establish certification with attestation and evidence.
8. Harden: password visibility, dormancy, least privilege.
9. Reserve a verification window in the plan.

## Anti-Patterns

- Detecting conflicts between responsibilities rather than between user assignments.
- Revoking whole roles instead of the conflicting responsibility only.
- Ignoring the business path for a removed duty, creating workarounds.
- Treating "indefinite" as an acceptable exception expiry.
- Shipping detective control only and finding new violations monthly.
- Generating a certification report nobody signs.
- Closing the SOD finding while leaving the password exposure in place.
- Planning the remediation to consume the entire 30-day window.

## Summary

The 45 violations were a missing control, not 45 individual mistakes. A risk
matrix made the concept enforceable; detection at the user-assignment level
found what responsibility-level queries cannot; remediation removed only the
conflicting duty with an alternate path, avoiding the worse outcome of unmanaged
workarounds; a preventive control at grant time stopped recurrence;
time-bound exceptions handled the irreducible cases honestly; and certification
with attestation made the control sustainable. Hardening — password visibility
and dormancy — closed the escalation path that would otherwise have made every
application-layer control irrelevant.