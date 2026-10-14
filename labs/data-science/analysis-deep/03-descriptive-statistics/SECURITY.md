# Descriptive Statistics - Security Notes

## Summary disclosure

Means and variances of small groups leak individuals: with n = 2, the mean
plus one known value reveals the other. Suppress or noise summaries below a
minimum-n threshold before external release.

## Outlier exposure

Max 21 in a published five-number summary spotlights an extreme individual
when data are personal (salaries, diagnoses). Band or top-code extremes in
public reports; keep exact values internal.

## Untrusted numeric feeds

A hostile column of `1e308` values overflows sums to Infinity; NaN payloads
poison every downstream moment. Validate finiteness (`Double.isFinite`)
at ingest and quarantine non-finite cells with counts.

## Reproducibility as tamper evidence

Pinned expected strings (mean 10.571428571428571, r 0.9901475429766744)
make silent substitution detectable: any altered value changes printed
output, and byte-comparison tests catch it. Version datasets with hashes so
"same code, different data" is distinguishable from "different code".

## Denominator honesty under regulation

Reporting sample variance as population variance (or vice versa) misstates
risk and uncertainty to decision-makers. Label the divisor wherever a
variance crosses a trust boundary (reports, filings, model cards).

## No secrets in summary code

Summary routines are safe to share; the data they ran on is not. Keep
dataset paths, credentials, and raw PII out of snippet repos and logs.

## Finiteness first

Validate `Double.isFinite` on every ingested value before any accumulation:
one Infinity or NaN anywhere makes all four moments meaningless, and the
quarantine counts are themselves the first finding about feed health.

## Small-n correlation exposure

r on tiny groups (n = 5 here) plus published means can let readers solve for
withheld values algebraically. Treat small-group correlations like small
counts: suppress, band, or noise them before release outside the team.
