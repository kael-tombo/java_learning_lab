# Model Serving - Reflection

## Core recall
- In one paragraph: Putting a trained model behind an interface that returns predictions for new inputs.
- Which of (batch (offline, scheduled scoring of stored data), online (request/response per input), streaming (continuous scoring of an event flow)) did you confuse before, and what distinguishes them now?
- Reproduce one snippet result from memory (value and reading), then check yourself.

## Decisions
- Name one decision you would now make differently: threshold, gate, rollout, or alert choice.
- What signal would tell you within a day whether that decision was right?
- What is the rollback path if it was wrong, and have you tested it?

## Tradeoffs
- What did you optimize, and what got worse as a side effect?
- Where is the capacity limit in your design: latency, reviewers, compute, or labels?
- Which simplifying assumption breaks first under ten times the load?

## Evidence
- Which numbers in your write-up are measured, and which are illustrative?
- What would you log to turn each illustrative number into a measured one?
- Write the follow-up question you still cannot answer; that is your next experiment.

## Transfer
- Name one idea from this lab that applies to a system you already operate.
- What is the smallest change that captures half the benefit?

## Serving-specific probes
- Sketch the three serving patterns from memory with their latency contracts.
- Write the batching formulas (latency and throughput) and the cap inequality without looking.
- State what shadow, canary, and blue-green each cost and each prove.

## Failure rehearsal
- Describe the last tail-latency incident shape: which leg moved, how you knew.
- Which guard (warmup, version pin, batch cap, rollback drill) would have caught it earliest?
- What single metric would have paged before users noticed?

## Calibration
- Which latency numbers in your notes are measured versus illustrative?
- What load shape produced each measured number: concurrency, warmup, traffic mix?
- Name the next measurement that would change a sizing decision.

## Teaching test
- Explain p99 to a teammate using the outlier example, then check their paraphrase.
- Explain canary z-noise without jargon; stop when they can state the decision rule.
- Whatever they garble is the part your own notes leave vague; fix the notes.
