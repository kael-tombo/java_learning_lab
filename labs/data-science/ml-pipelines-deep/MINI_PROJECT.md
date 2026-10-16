# ML Pipelines Deep — Mini Project: Slice Pipeline

Pick one supervised task on a small open dataset and build the full
spine in miniature: a feature computation with as-of semantics (lab 01),
a training script with pinned seed and logged params (lab 02), an
evaluation gate with a locked test split (lab 03), and a batch-serving
script that scores new rows through the same transform code (labs 02+05).

Deliverable: a directory where `run.sh` reproduces the model and its
metrics from raw data, plus a one-page lineage card (data snapshot id,
code version, seed, test metrics, known caveats). Deliberately include
one failed gate (bad data batch) and show the run stopping — the halt
is a feature under test, not an accident. One weekend, no serving
infrastructure; the registry can be a JSON file.
