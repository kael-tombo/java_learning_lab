# Model Training Pipelines — How It Works

## 1. Trigger
A pipeline launches on schedule (nightly), on data arrival, or manually.
The trigger records its cause and the dataset version it will consume.

## 2. Ingest pins data
The ingest stage snapshots the source (query + timestamp) and writes an
immutable dataset version with a hash. Everything downstream references
this version id, so late-arriving source changes cannot move the ground
under a running pipeline.

## 3. Validate gates progress
Schema checks run first (columns, types), then statistical checks (null
rates, ranges). The demo gate trips at null rate 0.3 over threshold
0.25. On failure the run stops, the owner is paged, and no model is
produced. A stopped pipeline is a successful defense, not an outage.

## 4. Transform deterministically
Validated rows flow through versioned feature code. Same dataset
version plus same transform version always yields the same feature
matrix. No randomness belongs here; sampling happens in training with
a recorded seed.

## 5. Train and evaluate
Training consumes features plus a seed and config, emits parameters and
training metrics. Evaluation scores the fitted model on held-out data
with the fixed metric set and compares against the production baseline
plus promotion thresholds.

## 6. Register with lineage
Passing models are stored under a new version with the full tracking
record (params, metrics, code+data hashes, seed). Failed candidates are
still recorded — negative results are data — but marked unpromotable.

## 7. Retraining loop
Scheduled retrains repeat the same graph on fresh dataset versions.
Determinism (same seed, same code) means metric changes reflect data
changes, not noise, which is what makes retraining a monitoring tool.
