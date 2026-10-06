# Lab 03: Financials — Theory

## The Scenario

30% of supplier invoices land on Payables Invoice Holds. The AP manager cannot
explain them. Suppliers wait weeks for payment. Someone suggests mass-releasing
the holds — which would be both wrong and a SOX finding.

## Principle 1: A hold rate is a signal, not a defect to suppress

A hold is a **control firing**. It means the system detected a discrepancy
between what was ordered, what was received, and what was billed.

Two readings are possible:

- **Too many holds** — the rules are stricter than how the business actually
  trades. The control is miscalibrated.
- **Too few holds** — a real discrepancy is passing undetected. The control is
  broken.

Both present as "a number". Only measurement distinguishes them. 30% is not
automatically wrong; **30% that nobody can explain** is the actual problem.

## Principle 2: Holds are typed, and the type tells you the fix

`AP_HOLDS_ALL` records a `hold_type` and `hold_code`. Common families:

| Hold type | Fires when | Usual fix |
|-----------|-----------|-----------|
| Price variance | Invoice amount exceeds PO price by more than tolerance | Tolerance or price update |
| Quantity variance | Invoice quantity differs from matched quantity | Matching rule or tolerance |
| Terms mismatch | Payment terms disagree between PO and invoice | Terms maintenance |
| Exchange rate | Currency rate differs beyond tolerance | Rate tolerance or rate source |
| Tax calculation | Calculated tax disagrees with invoiced tax | Tax setup |
| Invalid supplier | Supplier inactive or on hold | Supplier master |

The dominant type determines the entire remediation. **Build the taxonomy
first.** A project that starts by changing tolerances without knowing the
distribution is guessing.

## Principle 3: Ordered vs received is a semantics mismatch

This is the root cause in this lab.

```
PO says:        100 units ordered
Receipt says:    97 units actually delivered
Supplier bills: 97 units
```

If the matching rule compares the **invoiced 97** against the **ordered 100**,
every short shipment produces a 3% quantity variance hold. The supplier did
nothing wrong. The rule compared the wrong quantities.

The fix is matching on **received quantity**. Short shipments then flow
through cleanly, and genuine over-invoicing is still caught.

**The distinction matters**: quantity tolerance makes an incorrect comparison
merely tolerable; matching-rule correction makes it correct. Prefer the latter.

## Principle 4: Tolerances are statistical, not conventional

A 0% price variance tolerance means *any* rounding difference holds the invoice.
But prices are rarely exact:

- Currency conversion and rounding
- Volume rebates applied at invoice time
- Contract pricing with periodic true-ups
- Freight and tax apportionment

Real price variance is a **distribution**, not a point. The tolerance should sit
above the level where differences are noise and below the level where they
indicate a real problem.

Procedure:

1. Measure the variance distribution on held invoices.
2. Identify the noise band (the bulk of small differences).
3. Set the tolerance above that band.
4. Verify the tail — large variances — is still caught.

A tolerance set this way is **defensible to an auditor** because it is derived
from observed data, not chosen to make a number look good.

## Principle 5: Releasing holds is an audited decision

Mass release is prohibited for good reason: it converts a control into a rubber
stamp. The defensible pattern is:

- Candidate holds identified **automatically** by explicit, narrow criteria
- Each release requiring a **reason code**
- Every release **logged** with who, when, which hold, which reason
- The criteria themselves **documented** and approved

With that, releasing a hold is a documented application of an agreed rule, not
an individual judgement call. That is what survives SOX testing.

## Principle 6: Workflow is a latency problem

A hold that sits for three days because nobody was notified costs the supplier
three days of working capital. The hold itself may be correct; the *time to
resolve* it is the fixable part.

Routing matters more than the notification:

- Which approver? Depends on value threshold and category.
- Which buyer? Depends on the PO owner.
- Escalation? If unresolved after N hours, who is chased?

Automated routing turns a queue of invisible problems into a queue of assigned
work.

## Principle 7: Lowering the hold rate without weakening control

The obvious risk: if you loosen tolerances until holds disappear, you have
removed the control. Distinguish two things:

| Measure | Meaning |
|---------|---------|
| Hold rate | Fraction of invoices held |
| **Escape rate** | Fraction of invoices with a *real* discrepancy that passed |

Only the second indicates control weakness. A remediation that drops hold rate
from 30% to 8% while escape rate stays at zero has worked.

**This is the metric that must be reported.** Without it, the whole project is
indistinguishable from disabling the three-way match.

## Diagnostic Order

1. Build the hold taxonomy by reason, volume, and value.
2. Identify the dominant cause.
3. Determine *why* the rule fires — semantic mismatch or genuine variance?
4. Measure the variance distribution before setting any tolerance.
5. Prefer rule correction over tolerance widening.
6. Change, re-measure hold rate **and** escape rate together.
7. Automate release with reason codes; route with workflow.

## Anti-Patterns

- Mass-releasing holds to hit a number.
- Setting tolerances without measuring the distribution.
- Widening quantity tolerance instead of fixing the matching basis.
- Reporting hold rate improvement without escape rate.
- Assuming a hold is an error rather than a control firing.

## Summary

The 30% hold rate was a mismatch between how the system was configured and how
the business actually trades. The remedy was measurement first (taxonomy),
semantics second (matching on received quantity), statistics third (tolerances
derived from observed variance), and only then automation — with escape rate
tracked throughout to prove the control survived.