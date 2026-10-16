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
- Crankshaw et al., "Clipper: A Low-Latency Online Prediction Serving System" (NSDI 2017).
  Model-selection and adaptive batching layers for low-latency prediction serving; read for the
  batching and model-container mechanics behind online paths.
- Beyer et al., Site Reliability Engineering (O'Reilly, 2016).
  Service-level objectives, percentile-based targets, and rollout discipline behind p50/p99
  budgets and safe traffic shifts.
- Sculley et al., "Machine Learning: The High-Interest Credit Card of Technical Debt"
  (SE4ML workshop, 2014). Short precursor statement of the production-debt argument
  expanded in the 2015 paper above; useful for the audit-before-persuasion ordering.

## Application notes
- Apply Clipper's batching analysis next to the lab's latency formula to see the same
  overhead-plus-per-item shape in a served system.
- Apply the SRE book's SLO chapters when writing the per-leg p99 budget and the
  canary error/latency comparison procedure.
