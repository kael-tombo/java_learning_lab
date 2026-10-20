# Self-Supervised Learning — Real-World Project

**Goal**: prototype the evaluation plumbing for a pre-trained-code-similarity feature in
a dev-tools setting: agreement of retrieval top-k with reviewer-approved groupings. All
data is bounded, self-fabricated samples.

## Scenario

Take a set of 50 self-written utility-method records (name, small AST-ish feature vector
you define as 8 hand-chosen numbers). Pretend an embedding service gives you vectors; here
you will build the eval harness only, and a trivial deterministic "embedding" so you own
end-to-end reproducibility.

## Build components

1. `CorpusFixture`: 50 records across 5 semantic groups (string utils, math utils, ...)
   with hand-composed vectors; store as constants in code, not external files.
2. `EmbedderStub`: deterministic map — vector = group prototype + small record-specific
   offset you choose; document it as obviously lossy (named "stub" in code and text).
3. `RetrievalEvaluator`: for each record, retrieve top-3 by cosine; measure
   `hitRate@3` = fraction of retrieved whose true group equals the anchor's group; report
   also mean similarity of retrieved groups vs wrong-group baseline.
4. `ThresholdTuner`: choose a similarity cutoff for "probably same group"; sweep cutoffs
   to trade pair-recall vs pair-precision and emit the trade table (structure identical
   to the coverage/accuracy sheet in the safety lab).

## Ethics & limits section (mandatory, bulleted)

- False sense of relatedness: naming-similar but semantically-different records can rank
  high; give one fixture example violating it and show its actual similarity score.
- No benchmark claim: this stub cannot tell you whether a real model would be better;
  describe (2 sentences) what a swapping experiment would look like instead.
- Human-in-the-loop advice: top-3 lists go to a reviewer for dedupe triage, with abstain
  rules mirroring the selective-prediction pattern from dir 30.

## Deliverables

- `javac --release 21` compile of `EvaluatorMain`, deterministic top-3 tables.
- Trade table from `ThresholdTuner` at 6 cutoffs (pair precision vs recall quotes).
- Two-paragraph memo stating which limitation surprised you, with code-line references.
