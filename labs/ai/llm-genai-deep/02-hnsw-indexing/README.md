# 02-hnsw-indexing - HNSW Indexing
## Overview
HNSW layers graphs coarse-to-fine: greedy descent through upper layers, wider beam search at layer 0. Each node links ~M neighbors; recall trades against efSearch beam width. ANN is approximate: some true neighbors are missed.
## Key formulas
- Memory ~= n*dim*4 bytes (fp32 vectors) + graph edges.
- recall@k = hits@k / k on labeled queries.
## What the snippets show
- Lg02A: hop-count contrast plus 0.75 recall illustration.
- Lg02B: edge count and 5.12MB vector budget.
## Try it
Double M to 32 and recompute edge/degree numbers.
## Formula reference
- Layers: exponential decay level; M links; efConstruction/efSearch beams.
- Query cost ~ O(log n) hops; recall rises with efSearch.
- recall@k = |retrieved cap gold| / k on labeled sets.
## Worked example
- 10000*16 = 160000 directed edges; ~320000 undirected endpoints.
- Vectors 10000*128*4 = 5.12MB; graph overhead extra (ids + links).
- Toy 0.75 = 3/4: approximate search misses one by construction.
## Pitfalls
- M/ef too low: recall cliffs; too high: build time and RAM balloon.
- Deletes/updates fragment graphs; rebuild or tombstone + repair.
- High-dim curse: exact search degrades to scan; tune accordingly.
## Connections
- Embeddings lab supplies the vectors indexed here.
- RAG pipeline consumes top-k from this index.
## Exercises
1. Double M to 32; recompute edges.
2. Raise efSearch; predict recall direction.
3. Estimate RAM for n = 1e6, dim = 768.
