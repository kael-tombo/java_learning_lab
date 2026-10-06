# Lab 09: Security (SOD Remediation) — Math Foundation

## 1. The Fraud Arithmetic — Why SOD Exists

The conflict chain:

```
D1 Create supplier    →  supplier you control
D2 Approve invoice    →  bill for that supplier
D3 Process payment    →  money out
```

### Expected loss per occurrence

| Step | Amount |
|------|--------|
| Invoice value | $250,000 |
| Recovery rate | 10% (rarely recovered once paid) |
| **Expected loss** | **$225,000** |

### Expected annual loss without SOD control

```
Users holding all three duties:  45
Users who would act (fraud base rate): 0.1% per year
45 × 0.001 = 0.045 expected occurrences/year
```

That is 0.045 — which reads as negligible. **This is the classic mistake in SOD
argumentation.**

### Why the low base rate still justifies the control

Compare against the control cost:

```
Remediation cost (one-off):        $80,000
Ongoing control cost (quarterly):  $15,000/yr
Total 3-year cost:                 $125,000

Expected loss per occurrence:      $225,000
P(loss in 3 years at 0.1%/user):   1 - (1 - 0.045)^3 ≈ 12.7%
Expected loss:                     0.127 × $225,000 = $28,575
```

```
Control cost $125,000  >  Expected loss $28,575
```

**By that arithmetic the control is not economically justified.** Yet every SOX
framework mandates it. Why?

Because the base rate of 0.1% is not the relevant number. Two things are:

1. **Regulatory consequence.** A control deficiency is a material weakness. That
   carries cost far exceeding the fraud: restatement, qualified opinion,
   management liability, and in the financial services sector, regulatory action.

2. **Adverse selection.** The users who *can* commit this fraud are precisely the
   ones with the access to find it attractive. The population is not random.

```
Cost of a material weakness:  $2M–$50M in remediation, fees, and credibility
Cost of 45 unremediated SOD findings: contributes to that figure
```

**Report this honestly.** Framing SOD purely as fraud loss invites the correct
observation that the base rate is low. Framing it as a regulatory control
requirement is both accurate and unarguable.

## 2. Violation Prevalence

```
Population:        2,400 active users
Users with SOD conflicts:  45
Prevalence:        45 / 2,400 = 1.875%
```

### Is 1.875% high?

| Context | Typical |
|---------|---------|
| Mature program, quarterly certification | < 0.5% |
| First-time detection, no preventive control | 2–5% |
| This client | 1.875% |

The figure is **consistent with a system that has never been tested**. It is not
evidence of active fraud — it is evidence of an absent control.

```
Control absent  →  violations accumulate  →  first scan finds 1.875%
Control present →  preventive block stops them → steady state < 0.5%
```

This matters for expectation-setting: the 45 findings are a **baseline
measurement**, not a backlog to be cleared.

## 3. Conflict Density

Average SOD duties per user:

```
Users with conflicts:       45
Average conflicting pairs:  2.4 each
Total conflict instances:   108
```

Breakdown by severity:

| Severity | Pairs | % |
|----------|-------|---|
| HIGH | 61 | 56% |
| MEDIUM | 47 | 44% |

**56% of conflicts are high severity** — the approve/pay and GL chains. This is
what determines remediation order: not user count, not effort, but severity
weighted by value at risk.

## 4. Remediation Prioritisation

Rank by severity × annual value touched:

```
Score = severity_weight × annual_duty_value
        HIGH = 3, MEDIUM = 2, LOW = 1
```

| Tier | Users | Severity | Avg annual value | Score |
|------|-------|----------|-------------------|-------|
| 1 | 8 | HIGH | $18M | 3 × 18 = 54 |
| 2 | 19 | HIGH | $4M | 3 × 4 = 12 |
| 3 | 12 | MEDIUM | $2.5M | 2 × 2.5 = 5 |
| 4 | 6 | MEDIUM | $0.5M | 2 × 0.5 = 1 |

```
Tier 1 = 8 users = 18% of the finding
       = ~65% of total value at risk
```

**Remediating 8 users addresses most of the exposure.** Sequencing by user count
would spread effort evenly across 45 users and reach full remediation on
schedule — at the cost of leaving the worst exposure live for longer.

## 5. Over-Remediation Cost

The failure mode nobody budgets for:

```
Users remediated:                45
Users who need an alternate path:  38 (84%)
Alternate paths available:        6 users per business unit
```

Resulting workarounds if no alternate path exists:

| Workaround | Users adopting | Control quality |
|------------|----------------|-----------------|
| Shared login | ~12 | **Worse** — no attribution at all |
| Email approval trail | ~30 | **Worse** — outside the system of record |
| Manual escalation to a compliant user | ~8 | Acceptable, with cost |

```
Zero workarounds:    0 shared logins, 0 email trails
Twelve shared logins: attribution completely lost for 12 users
```

**A shared login is a worse control than the original violation**, because the
original at least had a user ID. This is the single most important reason to
provide alternate paths during SOD remediation.

## 6. Remediation Effort

Per user:

| Task | Minutes |
|------|---------|
| Identify conflict | 5 |
| Identify alternate path | 15 |
| Business approval | 20 |
| Execute revocation | 5 |
| Verify | 5 |
| **Total** | **50** |

For 45 users:

```
45 × 50 min = 2,250 min = 37.5 hours
```

But approvals are the bottleneck and they run in parallel with HR:

```
Sequential technical work:  45 × 15 min = 11.25 hours
Parallel business approvals: 20 min elapsed per user, batched daily

Critical path ≈ 5 days for one business unit
8 business units (piloted sequentially) ≈ 20 working days
```

Against a 30-day window:

```
Day 20: remediation complete
Day 23: verification
Day 26: evidence pack
Day 30: buffer
```

**The buffer exists because remediation always uncovers more.** If discovery is
continuous, a plan without verification time meets the audit committee with an
open finding.

## 7. Preventive Control Effectiveness

Before: detective only, monthly scan.

```
Expected new violations/year = assignments/yr × conflict probability
Assume 3,000 responsibility assignments/yr, 2% conflict rate
                          = 60 new violations/year = 5/month
```

With a preventive block:

```
New HIGH severity violations:  ~0
New MEDIUM (allowed with approval): ~20/yr, each with evidence
```

Reduction:

```
60 → ~20 annually = 67% reduction
Residual: each residual has an approval trail, so it is a documented decision
```

**The 33% residual is not a failure** — those are conflicts granted with
justification. The control changed the default from silent to documented.

## 8. Dormancy Risk

```
Dormant accounts with elevated access:  12
Average annual payment value in scope:  $240M

P(account compromised while dormant):  depends entirely on password control
```

With strong password controls and MFA: low — but still nonzero.
With password reuse from other systems: not negligible.

```
Dormant + reused password + unpatched system + no monitoring
= a valid credential for $240M of payment capability, unused
```

Auto-deactivation after 120 days eliminates the exposure entirely at the cost of
a small reactivation effort for anyone who genuinely returns:

```
Reactivation requests/month (est.): 2-3
Reactivation effort:                 5 min each
```

The comparison is unambiguous.

## 9. Password Exposure Blast Radius

`FND_HIDE_DB_PASSWORD='N'` exposes the database password. The escalation path:

```
Exposed EBS DB password
   →  direct SQL access to the EBS schema
   →  BYPASSES every application-layer control:
        • function security      (not evaluated by direct DML)
        • row-level security    (VPD policies may still apply, but
                                  responsibility-based filtering does not)
        • SOD                    (responsibilities are not consulted)
   →  read and write any table the schema owns
```

**Every control remediated in this project is irrelevant if this finding is left
open.** The 45 SOD violations take three weeks to fix; the password exposure
defeats all of them permanently until closed.

```
Priority: password exposure > all SOD findings combined
Time to fix: ~1 hour
```

## 10. Certification Coverage

```
Users in scope for certification:  2,400
Managers certifying:                  180
Users per manager:                  13.3

Certification effort per manager:
  Review 13 users × 2 min each  = 26 min
  Sign off                        = 5 min
  Total                          = 31 min/month

Annual effort = 180 × 31 × 12 = 66,960 min = 1,116 hours/year
```

That is a significant ongoing cost, which is the honest objection to monthly
certification. Options:

| Cadence | Annual effort | Risk exposure |
|---------|---------------|---------------|
| Monthly | 1,116 hrs | Lowest |
| Quarterly | 279 hrs | Moderate |
| Annual | 70 hrs | Highest |

**Quarterly is the pragmatic choice** for most organisations, with monthly
certification retained for HIGH severity duties. Cost is a legitimate constraint —
but note that skipping certification entirely is not on the list, because an
uncertified control is not a control.

## 11. Compliance Outcome Metrics

Report these after remediation:

```
Open SOD violations:              45   →    0
High-severity violations:         26   →    0
Approved exceptions (time-bound):  0   →    7 (each with owner + expiry)
Preventive control:            absent →    active
Dormant elevated accounts:        12   →    0
Password exposure:                1   →    0
Certification coverage:           0%  →   100% (quarterly cycle)
```

Note that exceptions rise from 0 to 7. **That is a positive outcome** — those
conflicts were always present and previously undocumented. Making them visible
with owners and expiry dates is the control working, not failing.

## 12. The 30-Day Plan

| Days | Activity | Deliverable |
|------|----------|-------------|
| 1–7 | Risk matrix, detection query, risk ranking | SOD risk matrix; 45 findings quantified |
| 8–14 | Preventive control, remediation scripts, exception form | Design pack; business sign-off |
| 15–21 | Pilot one business unit (8 users, Tier 1) | Validated approach; no disruption |
| 22–26 | Execute remaining units | All 45 remediated or excepted |
| 27–28 | Verification re-run | Zero open violations confirmed |
| 29–30 | Evidence pack, audit committee | Closed finding with evidence |

**Days 27–30 are not padding.** The verification re-run routinely finds 2–5
violations created during remediation itself — by administrators fixing other
problems. Without that window, the finding reopens.