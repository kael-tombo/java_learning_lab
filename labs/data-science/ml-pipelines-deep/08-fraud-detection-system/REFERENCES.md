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
- Van Rijsbergen, Information Retrieval (Butterworths, 1979).
  The precision/recall and operating-point vocabulary this lab applies to flags
  versus fraud; read for the measurement habits behind skewed-class evaluation.
- Provost and Fawcett, Data Science for Business (O'Reilly, 2013).
  Expected-value framing and cost-sensitive decisions behind threshold math;
  read for pricing misses against reviews before minimizing.
- Breck et al., "Data Validation for Machine Learning" (SysML, 2019).
  Automated checks behind the feature-parity habit: single shared paths verified
  by joining serving logs against training values.

## Application notes
- Apply the retrieval measures to the snippet triple (80/120/20) to reproduce
  P 0.400, R 0.800, F1 0.533 by hand before trusting any dashboard.
- Apply the expected-value framing to refit the illustrative 10:1 ratio with
  organizational numbers; the lab's method stands, its ratio does not travel.
