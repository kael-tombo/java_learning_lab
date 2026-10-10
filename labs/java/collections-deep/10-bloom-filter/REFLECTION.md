# Reflection: Bloom Filter

## What surprised you?

Certainty is asymmetric here: the filter *proves* absence and only
*suggests* presence — the reverse of most data structures. Write down
where your intuition placed certainty before this lab, and what the zero-
bit proof changed.

## Check your model

1. Derive p from scratch: (1−1/m)^(kn) → e^(−kn/m) → the kth power. Name
   the approximation step and when it fails (small m).
2. k=10 scores worse than k=7 at canonical load. Explain both penalties
   (per-op work + saturation) in one paragraph.
3. Two teams build filters with different hash seeds and OR them. What
   breaks, at the bit level? What check prevents it?

## Connect

- Which costly confirmation in your systems (disk seek, RPC, scan) sits
  behind a mostly-negative check? What p would you buy, and how many
  bits/element does it cost?
- Where would deletion or enumeration requirements disqualify the filter
  — and which variant (counting, cuckoo, XOR) fits instead?

## The one-line takeaway

Bits are shared evidence, half-full is tuned, one zero decides: spend ~10
bits/element per 1% decade and confirm every hit. If your summary holds
the formula, the optimum, and the union rule, it is complete.
