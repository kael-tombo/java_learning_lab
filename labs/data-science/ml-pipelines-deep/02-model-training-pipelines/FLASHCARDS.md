# Model Training Pipelines — Flashcards

Q: Name the six standard DAG stages in order.
A: Ingest, validate, transform, train, evaluate, register. Demo prints
exactly this order with gate_pass=true.

Q: What does the validate gate do?
A: Runs schema and statistical checks; on failure the run stops before
transform and no model is produced.

Q: Demo validation numbers?
A: n=10, nulls=3, null_rate=0.3, threshold=0.25, drift_flag=true,
range [1.0, 13.0], schema_ok=true.

Q: What makes retraining deterministic?
A: Fixed seeds plus pinned code and data versions. Demo: seed 42 gives
[2, 6, 3, 1, 4, 0, 7, 5] on both runs; seed 7 differs.

Q: What is an artifact registry?
A: Immutable versioned storage for datasets, transforms, and models;
reruns reference version ids, never mutable paths.

Q: Minimum experiment-tracking fields?
A: Params, metrics, code hash, data hash, seed, timestamps, output
artifact version. Missing any one breaks reproducibility.

Q: Demo config record?
A: `lr=0.01|depth=6|seed=42|data=v3`, hash -1652323048.

Q: Why record failed runs?
A: Negative results are data: they prevent repeated dead ends and show
what was tried with which data and code.

Q: Where does randomness belong?
A: In training under a recorded seed — never hidden inside transform,
which must be a pure function of versioned inputs.

Q: What does a stopped pipeline mean?
A: A successful defense: validation caught bad data before it could
become a bad model.
