# Lab 01: Transformer Architecture Deep Dive

## Overview
Explore the Transformer architecture — the foundation of modern GenAI. Understand encoder-decoder structure, multi-head self-attention, positional encoding, and feed-forward networks.

## Learning Objectives
- Implement scaled dot-product attention in Java
- Build a multi-head attention module
- Understand positional encoding (sinusoidal)
- Grasp the encoder-decoder flow

## Prerequisites
- Java 21+
- Basic linear algebra (matrix multiplication)
- Familiarity with neural network concepts

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Attention Is All You Need" (submitted 12 Jun 2017; rev. 2 Aug 2023) — https://arxiv.org/abs/1706.03762 — takeaway for this lab: scaled dot-product attention dispenses with recurrence/convolution, which is exactly what the Java `attention()` exercise implements.
- "Attention Is All You Need" (submitted 12 Jun 2017; rev. 2 Aug 2023) — https://arxiv.org/abs/1706.03762 — takeaway for this lab: multi-head attention + sinusoidal positional encoding are core paper contributions, matching the lab's multi-head module and sinusoidal encoding objectives.
- "Attention Is All You Need" (submitted 12 Jun 2017; rev. 2 Aug 2023) — https://arxiv.org/abs/1706.03762 — takeaway for this lab: encoder-decoder with 28.4 BLEU (EN-DE) / 41.8 BLEU (EN-FR) validates the encoder-decoder flow traced in this lab; training took 3.5 days on 8 GPUs, motivating why the lab uses a miniature Java replica.
