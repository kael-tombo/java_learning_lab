# Model Training Pipelines — History (confident facts only)

## What can be said safely
- Staged data pipelines predate ML: ETL practice and workflow
  schedulers established extract-transform-load ordering and retry
  discipline long before "MLOps" language existed.
- Sculley et al., "Hidden Technical Debt in Complex Machine Learning
  Systems" (NIPS 2015) documented why ML pipelines need special
  treatment: entanglement, correction cascades, and undeclared
  consumers make ad-hoc retraining hazardous.
- Breck et al., "The ML Test Score: A Rubric for ML Production
  Readiness" (extending the 2015 program) formalized production checks
  including data validation — the direct ancestor of validate gates.
- Experiment tracking and model registries grew out of the same
  reproducibility pressure: without recorded params, code, and data,
  results cannot be rerun or audited.
- Kleppmann's "Designing Data-Intensive Applications" (O'Reilly) gives
  the batch-processing and lineage background the pipeline layer rests
  on.

## What this lab does not claim
No first-pipeline dates, no vendor firsts, no adoption statistics. The
documented trend is from manual notebook retraining toward versioned,
gated, tracked pipelines — a response to repeated validation and
reproducibility failures described in the sources above.

## How to read the sources for this lab
- Sculley et al.: read for the failure taxonomy (entanglement,
  cascades, undeclared consumers) and map each failure to the stage
  or registry that prevents it.
- Breck et al.: read as a checklist author reads a spec — each rubric
  item becomes one gate predicate with a documented threshold.
- Kleppmann: read the batch-processing chapters for retry and
  idempotence semantics that stage contracts must satisfy.
- Zinkevich: read for launch and monitoring rules that turn pipeline
  outputs into production decisions.
