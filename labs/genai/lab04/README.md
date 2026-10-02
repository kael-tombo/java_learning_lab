# Lab 04: RAG System Design

## Overview
Design and implement a Retrieval-Augmented Generation (RAG) pipeline — document chunking, embedding-based retrieval, and context-augmented generation.

## Learning Objectives
- Implement document chunking strategies
- Build a simple embedding-based retriever (cosine similarity)
- Construct augmentation prompts
- Create the full retrieval-generation pipeline

## Prerequisites
- Java 21+
- Labs 01–03
- Vector similarity concepts

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (submitted 22 May 2020; accepted NeurIPS 2020) — https://arxiv.org/abs/2005.11401 — takeaway for this lab: RAG combines parametric seq2seq memory with non-parametric dense-vector Wikipedia index, the architecture the lab's retrieval-generation pipeline mirrors.
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (submitted 22 May 2020; accepted NeurIPS 2020) — https://arxiv.org/abs/2005.11401 — takeaway for this lab: RAG-Sequence (same passages per answer) vs RAG-Token (different passage per token) informs how the lab constructs augmentation prompts and conditions generation on retrieved chunks.
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (submitted 22 May 2020; accepted NeurIPS 2020) — https://arxiv.org/abs/2005.11401 — takeaway for this lab: paper reports SOTA on 3 open-domain QA tasks with more specific/factual output, justifying the lab's cosine-similarity retriever + chunking strategy to ground generation and reduce hallucination.
