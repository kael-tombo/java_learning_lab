# Feature Stores — History (confident facts only)

## What can be said safely
- The term "feature store" entered industry vocabulary in the mid-2010s
  as teams at several large tech companies described internal ML
  platforms that centralized feature computation for training and
  serving. Precise "first" attribution is disputed, so this lab does
  not claim one.
- The underlying problems are older and well documented: Sculley et
  al., "Hidden Technical Debt in Complex Machine Learning Systems"
  (NIPS 2015) describes boundary erosion and correction cascades that
  motivate shared feature infrastructure.
- Google's "Rules of Machine Learning" (Zinkevich, living guide) gives
  the practitioner rules this lab follows: monitor training/serving
  skew, log features at serving time, keep the first model simple.
- Kleppmann's "Designing Data-Intensive Applications" (O'Reilly)
  covers the log/derived-state and batch/stream views that feature
  stores combine; it is the standard reference for the storage layer.

## What this lab does not claim
No founding dates, no vendor firsts, no benchmark numbers. The lab's
historical grounding is the documented shift from hand-rolled ETL per
model to versioned shared feature layers, driven by repeated skew and
leakage incidents described in the sources above.

## How to read the sources for this lab
- Sculley et al.: focus on the entanglement and boundary-erosion
  discussion; each anecdote maps to one store component (shared
  transforms fix entanglement, versioned definitions fix erosion).
- Zinkevich rules: Rules #29/#32 justify the skew monitor; Rules
  #8/#10/#11 justify freshness SLOs and feature ownership records.
- Kleppmann: the chapters on batch vs stream and on derived state
  explain why one log feeds two sinks with different consistency
  needs. Read for mechanism, not for product guidance.
