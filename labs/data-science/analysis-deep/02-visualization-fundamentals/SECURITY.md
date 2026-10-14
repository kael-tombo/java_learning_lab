# Visualization Fundamentals - Security Notes

## Small-cell disclosure

Binned means with n = 1 or 2 (the lab's end cells) can expose individuals:
a cell mean of one person's value is that value. Suppress or merge cells
below a minimum-n threshold before publishing.

## Denominator attacks on proportions

Publishing 3/8-style fractions from tiny groups invites re-identification
when combined with outside knowledge. Round, band, or withhold small-n
breakdowns in public charts.

## Misleading graphics as integrity risk

Truncated axes and dual scales in external reports mislead regulators,
customers, and voters while staying technically "correct". Treat scale
choices as integrity controls: zero baselines and stated bins by policy.

## Log injection via labels

Category labels come from data; a label with newlines or terminal escapes
(`"food\nFAKE: 99/99"`) forges chart lines. Sanitize labels (strip control
characters, truncate length) before rendering bars.

## Resource exhaustion

A hostile feed with billions of distinct labels blows up the category map.
Bound distinct-label counts and fall back to top-k plus "other" with the
overflow counted, never silently dropped.

## Reproducibility as defense

Byte-stable text charts (fixed edges, ordered maps, no locale formatting)
make tampering detectable: any altered number changes the rendered string,
and tests can pin exact expected output.

## Provenance of pictured data

A chart without a stated source, filter, and n invites silent substitution:
swap the underlying extract and the picture changes with no trace. Caption
every shared chart with dataset, date range, filters, and row counts so
substitutions are detectable and reruns comparable.
