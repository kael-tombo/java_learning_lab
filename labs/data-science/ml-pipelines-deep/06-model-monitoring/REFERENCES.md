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
- Gama et al., "A Survey on Concept Drift Adaptation" (ACM Computing Surveys, 2014).
  Drift taxonomy and adaptation strategies behind the data-drift versus concept-drift
  split used throughout this lab.
- Quiñonero-Candela et al., Dataset Shift in Machine Learning (MIT Press, 2009).
  The edited volume on training-serving distribution mismatch; read for the shift
  vocabulary behind reference-vs-current comparisons.
- Breck et al., "Data Validation for Machine Learning" (SysML, 2019).
  Automated data checks and schema validation that map to the pipeline-health-first
  triage order in these monitors.

## Application notes
- Apply the Gama taxonomy when deciding whether a PSI jump is data drift (reweight
  or refresh features) or concept drift (retrain the mapping).
- Apply the data-validation paper's check catalog when writing the pipeline-health
  monitors that run before any model-cause investigation.
