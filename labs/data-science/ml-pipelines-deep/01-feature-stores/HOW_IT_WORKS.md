# Feature Stores — How It Works

## 1. Ingestion
Raw events land in a log with (entity, event time, payload). A
scheduler runs each versioned transform and appends (entity, ts, value)
rows to the offline store. Late events are handled by watermark rules:
rows arriving after the watermark trigger a bounded recompute, not an
in-place edit.

## 2. Training dataset build
For each label (entity, label time), the builder runs an as-of join:
latest feature row with ts <= label time per feature. The output row
carries feature values plus (name, version) lineage. If no feature row
qualifies, the field is missing and the declared imputation applies.

## 3. Online materialization
A streamer tails the offline log and upserts the newest row per entity
into the online key-value store. Serving reads one key and gets the full
vector. TTL is enforced at read time: expired fields return missing.

## 4. Version rollout
New transform v2 is registered, backfilled over history, validated, then
marked live. Online materialization switches to v2 rows; v1 rows remain
for models pinned to v1. Rollback is a pointer change, not a data edit.

## 5. Skew monitoring loop
Serving logs (entity, time, served vector). A job recomputes expected
vectors from the offline store with the pinned version and compares.
Per-feature max absolute difference and null-rate deltas page the owner
when thresholds break.

## 6. Failure modes it prevents
- Future leakage from naive joins.
- Silent transform drift between training and serving code.
- Unreproducible datasets from unversioned SQL.
- Stale serving reads with no expiry.
