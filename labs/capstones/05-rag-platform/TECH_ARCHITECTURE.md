# Technical Architecture: RAG Platform

## Architecture Overview

```
[Document Sources]
  PDF  DOCX  HTML  MD  TXT
       |
       v
+------------------+
| Document         |
| Ingestor         |
+--------+---------+
         |
+--------v---------+
| Chunking Engine   |
| - Fixed (256/512) |
| - Semantic        |
| - Recursive       |
+--------+---------+
         |
+--------v---------+
| Embedding Service |
| - OpenAI / Mock   |
| - Batch embed     |
+--------+---------+
         |
+--------v---------+
| Vector Store      |
| - HNSW Index      |
| - Metadata store  |
+--------+---------+
         |
+==================+
|   Retrieval API   |
+==================+
         |
+--------v---------+
| Hybrid Retriever  |
| Dense + Sparse    |
+--------+---------+
         |
+--------v---------+
| Reranker          |
| (Cross-encoder)   |
+--------+---------+
         |
+--------v---------+
| Context Builder   |
| - Token budget    |
| - Prompt assembly |
+--------+---------+
         |
+--------v---------+
| LLM (external)    |
+------------------+
```

## Component Breakdown

### 1. Document Ingestor
- **Input**: File path or byte stream + document ID
- **Parsers**: Apache Tika (PDF, DOCX), JSoup (HTML), custom (MD, TXT)
- **Metadata extraction**: Apache Tika metadata + custom extractors (title from filename, date from content)
- **Output**: Raw text string + DocumentMetadata map
- **Error handling**: Per-document try-catch; errors logged to error topic for reprocessing

### 2. Chunking Engine
- **FixedSizeChunking**: Token-aware (GPT-2/LLaMA tokenizer), configurable size 128-1024, overlap 10-25%
- **SemanticChunking**: Splits on sentence boundaries using regex + NLTK-like sentence detection
- **RecursiveChunking**: Hierarchy-based (headers > paragraphs > fixed-size); preserves structure in metadata
- **Chunk metadata**: Each chunk tagged with doc_id, chunk_index, total_chunks, chunk_strategy, positions

### 3. Embedding Service
- **Interface**: Pluggable via EmbeddingInterface: embed(text), embedBatch(texts)
- **Mock service**: Deterministic embeddings via seeded hash-based random for testing
- **Production implementation**: REST call to OpenAI/Cohere API or local ONNX model
- **Batching**: embedBatch with configurable batch size (default 32) for throughput
- **Normalization**: All embeddings normalized to unit length during ingestion

### 4. Vector Store
- **Primary**: HNSW index (M=16, ef=200) for ANN search
- **Fallback**: Flat index for exact search (verification/evaluation)
- **Metadata**: ConcurrentHashMap<Integer, Map<String, String>> for attribute filtering
- **Storage**: Persisted as binary vectors.bin + serialized hnsw.idx + metadata.json

### 5. Hybrid Retriever
- **Dense path**: Query -> embed -> HNSW search -> top-(K*2) candidates
- **Sparse path**: Query -> tokenize -> BM25 index -> top-(K*2) candidates
- **Fusion**: Reciprocal Rank Fusion (RRF) with configurable dense:sparse weight (default 0.7:0.3)
- **Scoring gap**: K=60 for RRF constant; prevents domination by either path

### 6. BM25 Index
- **Structure**: Inverted index: term -> {docId -> frequency}
- **Scoring**: Standard BM25Okapi formula with k1=1.5, b=0.75
- **Tokenization**: Lowercase + regex word split; stop-word removal optional
- **Updates**: Incremental add via addDocument; full rebuild on 20%+ document changes

### 7. Reranker
- **Input**: Query + top-(K*2) results from hybrid retrieval
- **Model**: Cross-encoder (mock or BAAI/bge-reranker-v2 via ONNX)
- **Output**: Reranked list with normalized relevance scores
- **Latency**: 15ms for 20 candidates with 6-layer MiniLM model

### 8. Context Builder
- **Token budget**: Configurable per model (4K for Llama2-7B, 8K for Mistral, 128K for GPT-4)
- **Budget split**: 25% prompt/instruction, 60% context, 15% reserved for generation
- **Scoring-based truncation**: Fill context budget with highest-scored chunks first
- **Prompt template**: Standard "Answer based on context\n\nContext: [N]\n\nQuestion: Q\n\nAnswer:"

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Java 21 | Runtime |
| Document parsing | Apache Tika 2.9 | Multi-format parsing |
| HTML parsing | JSoup 1.17 | HTML sanitization |
| Embeddings | OpenAI API / Mock | Vector generation |
| Vector store | Custom HNSW | ANN search |
| Inverted index | Custom BM25 | Sparse retrieval |
| Serialization | Jackson | Metadata persistence |
| Tokenizer | HuggingFace/LLaMA tokenizer | Token counting |
| Metrics | Micrometer | Observability |

## Query Flow

```
1. User submits query: "What is the refund policy for digital items?"
2. Embedding service: embed(query) -> float[768]
3. Dense search: HNSW search(query_embedding, topK=20, ef=100) -> 20 results
4. Sparse search: BM25 search("refund policy digital items", topK=20) -> 20 results
5. RRF fusion: merge and weight dense+sparse -> 20 combined results
6. Reranker: query + passage pairs -> cross-encoder scores -> 10 reranked results
7. Context builder: tokenize, fit to budget (25% prompt/60% context/15% generation)
8. Prompt assembly: template + context_chunks + query
9. LLM call: send prompt to LLM, receive answer
10. Total latency: 45ms retrieval + 15ms rerank + 5ms assembly + LLM call
```

## Performance Targets

| Stage | P50 | P95 | P99 | Throughput |
|-------|-----|-----|-----|------------|
| Document ingest (100KB) | 200ms | 500ms | 1000ms | 5 docs/sec |
| Chunking (fixed 512) | 5ms | 10ms | 20ms | 200 docs/sec |
| Embedding (batch 32) | 10ms | 15ms | 25ms | 1000 chunks/sec |
| Vector insert | 2ms | 5ms | 10ms | 500 vecs/sec |
| Dense retrieval (1M) | 2ms | 5ms | 10ms | 500 QPS |
| Sparse retrieval (5M) | 5ms | 15ms | 30ms | 200 QPS |
| Hybrid retrieval | 10ms | 20ms | 40ms | 150 QPS |
| Reranking (20 items) | 10ms | 15ms | 25ms | 100 QPS |
| Full pipeline | 25ms | 45ms | 80ms | 50 QPS |
