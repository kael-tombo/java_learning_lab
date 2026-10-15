# Model Evaluation — Performance

## Cost structure
Scoring passes are linear in n; curve building adds one sort (n log n);
calibration adds one linear binning pass. All of it is dwarfed by
training cost on any real dataset, so evaluation shortcuts never pay.

## Throughput tactics
- Score sharded predictions per partition, then sum the four counts —
  confusion entries are additive.
- Retain scores once and derive all curves from the single sorted
  order rather than re-sorting per curve.
- Compute proper scores in the same pass as the matrix to avoid
  re-reading predictions.

## Latency tactics
- Incremental confusion updates per batch keep dashboards live during
  long evaluations.
- Approximate curves on large data via score histograms with enough
  bins; exact curves on samples for audit.

## What not to optimize
Do not subsample the test set to "speed up" evaluation — the test set
is usually the smallest split already, and subsampling destroys the
rare-class evidence. Do not cache test scores across preprocessing
changes; refits invalidate old numbers.

## Scale honesty
This lab uses n=10 and n=4 demos; timing claims at that scale are
meaningless. The complexity statements (linear passes, one sort) are
what transfer to production sizing.
