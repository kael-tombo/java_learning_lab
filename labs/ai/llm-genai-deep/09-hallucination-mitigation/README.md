# 09-hallucination-mitigation - Hallucination Mitigation
## Overview
Mitigations: require citations (coverage = cited/total), self-consistency sampling with agreement thresholds, abstention when agreement < 0.5, retrieval grounding before answering.
## Key formulas
- Coverage = cited claims / total claims.
- Accept iff agreement >= threshold else abstain.
## What the snippets show
- Lg09A: 0.75 coverage count.
- Lg09B: 0.75 agreement accept path.
## Try it
Drop a citation and confirm coverage falls to 0.50.
## Formula reference
- Coverage = cited/total; precision of citations separately checkable via NLI.
- Agreement = top answer votes/n; abstain iff agreement < tau.
- Grounding: retrieve-then-generate; quote spans, not paraphrases.
## Worked example
- 3/4 = 0.75: one claim lacks a source span.
- Paris 3/4 = 0.75 >= 0.5 -> accept; 1/4 would abstain.
- Dropping one more citation: 2/4 = 0.50 (try-it check).
## Pitfalls
- Citations can be fake-but-plausible; verify spans resolve.
- High agreement on memorized facts != grounded; still cite.
- Over-abstention annoys; tune tau per risk tier.
## Connections
- RAG evaluation lab defines these metrics formally.
- Safety redaction handles the orthogonal PII risk.
## Exercises
1. Drop a citation; coverage becomes 0.50.
2. Votes 2/4; apply abstain rule.
3. Require spans; reject one paraphrase.
