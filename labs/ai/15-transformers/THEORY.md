# 15-transformers � Theory\n\nCore theoretical foundations of 15-transformers.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Attention Is All You Need (12 Jun 2017) — https://arxiv.org/abs/1706.03762 — Takeaway for transformer-build exercises: the paper replaces recurrence/convolutions with self-attention alone, so lab implementations of encoder-decoder blocks should center on scaled dot-product attention rather than RNN loops.
- Attention Is All You Need (12 Jun 2017) — https://arxiv.org/abs/1706.03762 — Takeaway for multi-head-attention exercises: parallel attention heads with positional encodings are what let the model capture diverse token relations at O(1) path length; verify head-count vs. quality trade-offs when configuring heads.
- Attention Is All You Need (12 Jun 2017) — https://arxiv.org/abs/1706.03762 — Takeaway for training-parallelism exercises: reported 28.4 BLEU (EN-DE) and 41.8 BLEU (EN-FR) after 3.5 days on 8 GPUs demonstrates the parallelization payoff to measure when comparing transformer vs. recurrent training time.
- Attention Is All You Need (12 Jun 2017) — https://arxiv.org/abs/1706.03762 — Takeaway for parsing/generalization exercises: the same architecture succeeded on English constituency parsing with large and limited data, so test lab models on a second task beyond translation to confirm generalization.
