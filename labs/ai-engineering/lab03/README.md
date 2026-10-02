# Lab 03: RAG System Architecture

## Learning Objectives
- Build a complete retrieval-augmented generation pipeline
- Implement multiple chunking strategies (fixed-size, sentence-aware)
- Combine vector similarity with keyword search (hybrid search)
- Understand the tradeoffs in retrieval quality vs. latency

## Concepts Covered
- **Chunking**: Splitting documents into retrievable units
- **Embedding-Based Retrieval**: Semantic search via vector similarity
- **BM25/Keyword Search**: Lexical matching for precision
- **Hybrid Search**: Weighted combination of vector + keyword scores
- **Re-ranking**: Improving retrieval quality with a second pass

## Setup
```bash
cd lab03
javac src/com/aiengineering/lab03/RagSystemArchitectureDemo.java
java com.aiengineering.lab03.RagSystemArchitectureDemo
```

## Key Takeaways
- Chunk size and overlap significantly impact retrieval quality
- Hybrid search outperforms pure vector or pure keyword search
- Sentence-aware chunking preserves semantic boundaries

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Introducing Contextual Retrieval" by Anthropic Engineering (published 19 Sep 2024) — https://www.anthropic.com/engineering/contextual-retrieval — takeaway for this lab: prepending 50–100 tokens of chunk-specific context before embedding (Contextual Embeddings) fixes the "company revenue grew 3%" decontextualization problem the lab's fixed-size vs sentence-aware chunking exercise demonstrates.
- "Introducing Contextual Retrieval" by Anthropic Engineering (published 19 Sep 2024) — https://www.anthropic.com/engineering/contextual-retrieval — takeaway for this lab: Contextual Embeddings + Contextual BM25 hybrid search cut top-20 retrieval failures by 49% (5.7% → 2.9%), directly supporting the lab's hybrid vector + keyword search with rank fusion.
- "Introducing Contextual Retrieval" by Anthropic Engineering (published 19 Sep 2024) — https://www.anthropic.com/engineering/contextual-retrieval — takeaway for this lab: adding a Cohere reranker over top-150 → top-20 cuts failures by 67% (to 1.9%), quantifying the lab's retrieval-quality-vs-latency tradeoff and its second-pass re-ranking step.
