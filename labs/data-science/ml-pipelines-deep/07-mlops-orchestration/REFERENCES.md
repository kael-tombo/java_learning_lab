# References

## Core sources
- Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017).
  Batch versus stream processing, storage engines, and log-based integration behind serving choices.
- Sculley et al., "Hidden Technical Debt in Machine Learning Systems," NIPS 2015.
  Why serving code, glue code, pipeline jungles, and monitoring dominate production ML cost.
- Breck and colleagues, "The ML Test Score" rubric for production ML readiness.
  Scored checks across data, model, and infrastructure that map directly to deployment gates.
- Leonard Richardson and Mike Amundsen, RESTful Web APIs (O'Reilly, 2013).
  Resource design and versioning patterns behind stable request/response serving contracts.

## How to use them
- Start with Sculley et al. for motivation: it names the failure modes every other file addresses.
- Use Kleppmann when choosing batch, online, or streaming shapes and their storage.
- Use the ML Test Score rubric as a checklist when writing promotion gates.
- Use Richardson and Amundsen when versioning serving schemas and error responses.

## Reading order for this lab
1. Sculley et al., sections on serving, monitoring, and feedback loops.
2. Kleppmann chapters on batch versus stream processing and derived data.
3. The ML Test Score rubric, marking which checks this lab implements.
4. Richardson and Amundsen on versioning, applied to model and schema versions.

## Lab-specific sources
- Baylor et al., "TFX: A TensorFlow-Based Production-Scale Machine Learning Platform" (KDD 2017).
  Continuous training, validation, and deployment pipelines in production; read for the
  gate-and-lineage shape behind metric-gated promotion.
- Zaharia et al., "Accelerating the Machine Learning Lifecycle with MLflow"
  (IEEE Data Engineering Bulletin, 2018). Model registry and experiment tracking
  for the lineage-pointer habit: data, code, parameters, and environment per run.
- Sculley et al., "Machine Learning: The High-Interest Credit Card of Technical Debt"
  (SE4ML workshop, 2014). Pipeline jungles and glue code as the debt this lab's
  DAGs, pins, and queues are built to pay down.

## Application notes
- Apply the TFX validation-and-promotion shape when drawing the ingest-to-promote
  DAG and placing data-validation versus metric gates.
- Apply the MLflow lineage habit when defining the run fingerprint: every pointer
  the registry tracks belongs in the hash.
