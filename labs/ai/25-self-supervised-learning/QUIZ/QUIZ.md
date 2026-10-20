# Self-Supervised Learning — Quiz

Answer keys stated; standard results only.

**Q1. Write the InfoNCE formula.**
A: `-log [ exp(s+ / tau) / sum_i exp(s_i / tau) ]`, with `s_i = cos(q, k_i)` and `tau` the
temperature.

**Q2. What role does the temperature play?**
A: A sharpness knob for the softmax over similarities: small `tau` makes the ranking
winner take nearly all probability; large `tau` drives all candidates toward uniform.

**Q3. What is a positive pair and where do negatives come from?**
A: Two augmented views of the same instance; negatives are the other samples' embeddings
in the batch (one-sided contrastive convention).

**Q4. Why is a projection head used before the loss?**
A: Similarity comparison happens in a separate head's space while the representation the
downstream tasks consume stays in the encoder output; the head is discarded afterward.

**Q5. What does the masked diagonal in NT-Xent mean?**
A: The anchor's similarity to itself (`cos = 1`) is excluded from the denominator, so the
softmax ranks the positive against other candidates, not against a trivial constant.

**Q6. What is the standard evaluation for a learned encoder?**
A: Linear-probe transfer: freeze the encoder, fit a linear classifier on a small labelled
set, compare against a from-scratch training-run baseline.

**Q7. How do predictive (masked-style) objectives differ from contrastive ones?**
A: They learn by reconstructing or predicting a held part of the input rather than by
ranking candidates, so they need no negatives.

**Q8. Why can't you compare an InfoNCE loss of `0.3` across two papers directly?**
A: Because batch size, augmentation stack, temperature, and dataset all change the
attainable value; the safe answer is to retrain your own baseline.

**Q9. Why does batch composition matter more here than in supervised learning?**
A: Negatives are the other instances' views; batch diversity sets the difficulty and the
attainable loss pair of the run.

**Q10. What does `p(pos)` collapsing toward uniform indicate about an encoder?**
A: Similarities have flattened — the representation fails to separate positive pairs from
background; check augmentation and temperature before anything else.
