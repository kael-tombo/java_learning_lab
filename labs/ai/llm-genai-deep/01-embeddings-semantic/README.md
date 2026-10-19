# 01-embeddings-semantic - Embeddings
## Overview
Embeddings map text to vectors; cosine a.b/(|a||b|) in [-1,1] measures semantic closeness. Retrieval ranks documents by this score (nearest neighbor).
## Key formulas
- cos = a.b / (|a| |b|); 1 = same direction, 0 = orthogonal.
- top1 = argmax cos(q, d_i).
## What the snippets show
- Lg01A: three cosine values incl. exact 0 for orthogonal pair.
- Lg01B: full ranking with top1=doc0.
## Try it
Normalize docs first, then confirm cosine equals plain dot product.
## Formula reference
- cos in [-1,1]; dot for unit vectors; Euclidean dist = sqrt(2-2cos) if unit.
- Pooling: mean/CLS/attention-weighted; normalize before indexing.
- top1 = argmax cos; ties broken arbitrarily, note it.
## Worked example
- cos(q,d1): (1+0.9)/(sqrt(2)*sqrt(1.81)) = 1.9/1.9026 = 0.9986.
- Orthogonal [1,0,1].[0,1,0] = 0 -> 0.0000 exactly.
- Ranking 0.9986 > 0.9959 > 0.2287 > 0.0000 deterministic.
## Pitfalls
- Unnormalized dot favors long vectors; normalize or use cosine.
- Anisotropy: raw LM embeddings cluster in cones; whiten/center helps.
- Case/punctuation shifts vectors; normalize text first.
## Connections
- RAG retrieves with these scores (pipeline lab).
- HNSW indexes these vectors approximately (indexing lab).
## Exercises
1. Normalize first; confirm dot equals cosine.
2. Add doc [1,0,0.99]; rerank.
3. Find a vector orthogonal to the query.
