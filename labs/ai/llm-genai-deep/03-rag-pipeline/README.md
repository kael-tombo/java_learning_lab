# 03-rag-pipeline - RAG Pipeline
## Overview
RAG order: chunk -> embed -> retrieve top-k by similarity -> augment prompt -> generate. Quality is measured by rank metrics: MRR averages 1/rank; recall@k counts gold hits in top k.
## Key formulas
- MRR = mean(1/rank_i); recall@k = hits@k / gold.
- Retrieve-then-read: context tokens bound answerable questions.
## What the snippets show
- Lg03A: full stage order with real scores.
- Lg03B: MRR 0.6111, recall@2 0.6667.
## Try it
Add a duplicate chunk and watch top-2 fill with redundant context.
## Formula reference
- Stages: chunk (size/overlap) -> embed -> retrieve k -> rerank? -> augment -> generate.
- MRR = mean 1/rank; recall@k; nDCG weights positions logarithmically.
- Context budget: k * chunk_tokens <= window minus generation reserve.
## Worked example
- Scores 1.0/0.7071/0.0: top-2 = chunks 0,1 deterministically.
- MRR (1 + 1/3 + 1/2)/3 = 1.8333/3 = 0.6111.
- recall@2: ranks {1,2} hit, {3} missed -> 2/3 = 0.6667.
## Pitfalls
- Chunk too big: dilutes scores; too small: splits answers.
- Top-1 wrong poisons generation; rerank or raise k.
- Stale index: re-embed after doc updates.
## Connections
- Evaluation lab scores this pipeline's outputs.
- Agents call this pipeline as a search tool.
## Exercises
1. Add duplicate chunk; watch top-2 redundancy.
2. Score ranks [2,1,3]; recompute MRR.
3. Shrink chunk size; argue recall effect.
