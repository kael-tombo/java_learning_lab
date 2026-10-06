# Lab 01: Transformer Architecture — Flashcards

## Card 1
**Q**: What does the Transformer replace recurrence with?
**A**: Self-attention — enabling parallel processing of all tokens.

## Card 2
**Q**: Write the scaled dot-product attention formula.
**A**: Attention(Q,K,V) = softmax(Q·Kᵀ/√d_k)·V

## Card 3
**Q**: Why divide by √d_k in attention?
**A**: To prevent dot products from growing too large, which would push softmax into regions with vanishing gradients.

## Card 4
**Q**: What is multi-head attention?
**A**: Running h attention operations in parallel with different learned projections, then concatenating and projecting the results.

## Card 5
**Q**: What problem do positional encodings solve?
**A**: Attention is permutation-invariant; positional encodings inject sequence order information.

## Card 6
**Q**: What are the two sub-layers in an encoder layer?
**A**: (1) Multi-head self-attention, (2) Position-wise feed-forward network.

## Card 7
**Q**: What are the three sub-layers in a decoder layer?
**A**: (1) Masked self-attention, (2) Cross-attention, (3) FFN.

## Card 8
**Q**: What does the causal mask do?
**A**: Sets future positions to -∞ before softmax, so the model cannot attend to tokens it hasn't generated yet.

## Card 9
**Q**: What is a residual connection?
**A**: output = x + Sublayer(x) — lets gradients flow directly through the network.

## Card 10
**Q**: What does layer normalization do?
**A**: Normalizes activations to zero mean and unit variance across the feature dimension, stabilizing training.

## Card 11
**Q**: What is the typical FFN inner dimension relative to d_model?
**A**: 4× d_model (e.g., 2048 for d_model=512).

## Card 12
**Q**: What is the time complexity of self-attention?
**A**: O(n²·d) where n is sequence length and d is model dimension.

## Card 13
**Q**: What is cross-attention?
**A**: Attention where Q comes from the decoder and K,V come from the encoder output — connecting the two stacks.

## Card 14
**Q**: What is teacher forcing?
**A**: Feeding ground-truth tokens as decoder input during training (as opposed to the model's own predictions).

## Card 15
**Q**: Name the three main Transformer variants.
**A**: Encoder-only (BERT), decoder-only (GPT), encoder-decoder (T5, original Transformer).

## Card 16
**Q**: What is pre-norm vs post-norm?
**A**: Pre-norm: LayerNorm before the sub-layer. Post-norm: LayerNorm after. Modern LLMs use pre-norm for stability.

## Card 17
**Q**: What does the output projection W_o do in multi-head attention?
**A**: Projects the concatenated head outputs back to d_model dimension.

## Card 18
**Q**: Why is softmax used in attention?
**A**: To convert raw scores into a probability distribution (weights sum to 1).

## Card 19
**Q**: What is the purpose of the scaling factor in sinusoidal PE wavelengths?
**A**: Geometric progression of wavelengths lets the model learn relative positions via linear transformations.

## Card 20
**Q**: What is the main scaling challenge of Transformers?
**A**: The O(n²) attention cost in sequence length — motivating efficient attention variants.
