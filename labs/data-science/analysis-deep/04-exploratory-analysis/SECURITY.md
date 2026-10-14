# Exploratory Analysis - Security Notes

## Stratum re-identification

Ward B control (n = 80) is small enough that rate 68.75% plus outside
knowledge can isolate individuals. Suppress, band, or noise small-stratum
rates before any external release; internal analysis keeps them exact.

## Composition as sensitive metadata

Which ward holds which patients (or customers) is itself sensitive. The mix
audit (270 vs 90) needed for the paradox is also a roster summary - restrict
its circulation like the underlying assignment data.

## Causal claims as integrity risk

Upgrading r 0.99 to "drives" in external communications misleads customers,
regulators, or voters. Gate causal verbs behind design evidence in review;
association wording is the default the pipeline enforces.

## Untrusted grouping keys

Group keys from user input (region strings) can collide, overflow maps, or
carry control characters into reports. Normalize, bound distinct counts
(top-k plus counted "other"), and sanitize keys before rendering.

## Provenance of exploration records

Loop-records that drive funding or launch decisions must cite dataset
hashes and row counts; otherwise a swapped extract silently replays "the
same analysis" on different data. Pin inputs, then trust outputs.

## No raw data in shared snippets

The ward counts here are synthetic and safe; real strata counts travel with
access controls. Keep PII-bearing displays out of code repos and logs - the
methods are shareable, the rosters are not.

## Display data minimization

Shape displays (sorted lists, scatters) expose raw values by nature. Prefer
binned or aggregated displays for shared EDA artifacts, reserving
row-level views for access-controlled sessions - the finding (right skew,
two strays) survives binning while the roster does not travel.
