# Feature Stores — Common Mistakes

## 1. Naive latest-value join
Taking the newest feature row regardless of label time leaks the
future. In this lab's demo the leaked value is 0.95 against a correct
as-of value of 0.2 — on real data the same mistake systematically
inflates validation scores. Always filter ts <= t first, then take
the latest.

## 2. Two copies of the transform
A notebook function for training and a service function for serving
drift apart within weeks. The demo stale path differs by a constant
1.0 shift. Keep one versioned implementation imported by both paths.

## 3. Silent zero-fill of missing features
Filling "no history" with 0.0 conflates missing with a real zero and
hides cold-start problems. A key with no snapshot at or before the
event time must surface as an explicit unknown (like the demo's MISS
path for unseen keys) or route to a declared imputation whose default
is logged and versioned — never as a silent plausible-looking number.

## 4. Editing store rows by hand
Patching a bad value in place destroys reproducibility: the log no
longer explains the data. Append corrections as new rows; backfills
recompute from the log.

## 5. No TTL or infinite retention
Without expiry, serving silently reads ancient values after upstream
outages. Set a TTL per feature, monitor coverage, and alert on drops.

## 6. Floating "latest" version pins
Serving configured to "latest" picks up experimental versions
automatically. Pin exact versions per model; promote versions
explicitly after backfill validation.

## 7. Confusing event time with processing time
Using arrival time instead of event time in the join breaks causality
whenever data arrives late. Stamp rows with event time at the source
and join on that.

## 8. Skipping backfill validation
Marking v2 live without per-partition counts and null-rate checks lets
a buggy transform poison both training and serving. Gate promotion on
validation receipts.
