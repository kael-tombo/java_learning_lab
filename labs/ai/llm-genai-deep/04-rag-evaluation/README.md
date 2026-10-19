# 04-rag-evaluation - RAG Evaluation
## Overview
RAG triad: faithfulness (claims supported by context), answer relevance (response answers the question), context precision/recall (retrieved set quality). Precision@k = relevant@k/k; recall = gold covered/gold.
## Key formulas
- Faithfulness = supported/total; relevance = mean rater score.
- P@k and recall separate ranking quality from coverage.
## What the snippets show
- Lg04A: 0.80 faithfulness, 0.8000 relevance.
- Lg04B: P@3 0.6667 with recall 1.0000.
## Try it
Move the irrelevant chunk to rank 4 and confirm P@3 hits 1.0.
## Formula reference
- Faithfulness = supported claims/total; needs claim splitting + NLI check.
- Answer relevance: LLM-judged or cosine(question, hypothetical answer).
- P@k = relevant@k/k; recall = gold covered/gold.
## Worked example
- 4/5 = 0.80: one unsupported claim fails the response.
- Relevance (0.9+0.7+0.8)/3 = 2.4/3 = 0.8000.
- Flags [1,0,1]: P@3 = 2/3 = 0.6667; all gold present -> recall 1.0.
## Pitfalls
- LLM judges favor verbosity; calibrate with human spot checks.
- Claim splitting granularity changes faithfulness denominators.
- Precision without recall hides missing coverage.
## Connections
- Hallucination lab turns these metrics into mitigations.
- Agents need the same grounding checks per tool result.
## Exercises
1. Move bad chunk to rank 4; P@3 becomes 1.0.
2. Score 2/3 supported; new faithfulness.
3. Add a 4th gold; recompute recall.
