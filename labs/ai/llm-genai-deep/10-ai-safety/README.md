# 10-ai-safety - AI Safety
## Overview
Safety layers: input classification (refuse/allow), PII redaction before logging, output filtering. Keyword gates illustrate the shape; production uses trained classifiers, policy review, and red-teaming.
## Key formulas
- Decision = REFUSE iff risk_score > threshold (demo uses substring proxy).
- Redaction: replace [0-9]{3}-[0-9]{4} and email patterns.
## What the snippets show
- Lg10A: 1 refusal in 3 prompts.
- Lg10B: exact redacted string with 2 spans.
## Try it
Add 'poison' prompt and confirm the gate refuses it.
## Formula reference
- Risk gate: REFUSE iff score > threshold; audit trail per decision.
- Redaction patterns: phones, emails, IDs; names need NER (kept here).
- Defense in depth: input filter, tool policy, output filter, logging.
## Worked example
- 3 prompts -> [ALLOW, REFUSE, ALLOW]: weapon substring triggers once.
- Regex [0-9]{3}-[0-9]{4} matches 555-1234; email pattern matches john@mail.com.
- Output keeps 'John' (name NER out of scope for this demo).
## Pitfalls
- Substring gates under/over-block; classifiers + review for production.
- Redaction after logging leaks; redact before persistence.
- Prompts evolve (jailbreaks); regression-test gates continuously.
## Connections
- Agents need per-action authorization, not just prompt gates.
- Evaluation lab can score refusal correctness (precision/recall of refuses).
## Exercises
1. Add poison prompt; confirm refusal.
2. Redact ID 123-45-6789 with new pattern.
3. Log before vs after redaction; spot leak.
