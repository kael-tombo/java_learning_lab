# Lab 01: Transformer Architecture — Quiz

## Questions

**Q1.** What is the primary advantage of attention over RNNs?
- a) Lower memory usage
- b) Parallel processing of all tokens
- c) No need for positional information
- d) Simpler math

**Q2.** Why do we scale dot-product attention by 1/√d_k?
- a) To reduce memory
- b) To prevent softmax saturation from large dot products
- c) To make outputs sum to 1
- d) To speed up matrix multiplication

**Q3.** In multi-head attention, what does each head learn?
- a) The same representation
- b) Different aspects of token relationships
- c) Only positional information
- d) Only syntactic information

**Q4.** What problem do positional encodings solve?
- a) Vanishing gradients
- b) Attention's permutation invariance
- c) Overfitting
- d) Slow inference

**Q5.** What is the purpose of the causal mask in the decoder?
- a) To prevent attending to padding tokens
- b) To prevent attending to future tokens
- c) To improve training speed
- d) To reduce model size

**Q6.** What does a residual connection do?
- a) Adds the input to the sub-layer output
- b) Multiplies the input by the sub-layer output
- c) Normalizes the input
- d) Projects the input to a higher dimension

**Q7.** Which sub-layer connects the decoder to the encoder?
- a) Masked self-attention
- b) Feed-forward network
- c) Cross-attention
- d) Layer normalization

**Q8.** What is the time complexity of self-attention for sequence length n?
- a) O(n)
- b) O(n log n)
- c) O(n²)
- d) O(n³)

**Q9.** In the FFN, the inner dimension is typically:
- a) Equal to d_model
- b) Half of d_model
- c) 4× d_model
- d) 16× d_model

**Q10.** What does "teacher forcing" mean during training?
- a) Using a larger model to guide a smaller one
- b) Feeding ground-truth tokens as decoder input
- c) Forcing the model to attend to all positions
- d) Using multiple teachers for ensemble training

**Q11.** Pre-norm vs post-norm refers to:
- a) Where dropout is applied
- b) Where layer normalization is placed relative to the sub-layer
- c) How positional encodings are added
- d) How attention scores are scaled

**Q12.** Which models use only the decoder stack?
- a) BERT
- b) T5
- c) GPT
- d) Original Transformer

---

## Answer Key

| Q | Answer | Explanation |
|---|--------|-------------|
| 1 | b | Attention processes all tokens in parallel |
| 2 | b | Large dot products push softmax into flat regions |
| 3 | b | Different heads capture different relationships |
| 4 | b | Attention alone has no notion of order |
| 5 | b | Causal mask blocks future token visibility |
| 6 | a | Residual: output = x + Sublayer(x) |
| 7 | c | Cross-attention: Q from decoder, K/V from encoder |
| 8 | c | Q·Kᵀ is n×n — O(n²·d) |
| 9 | c | Typical FFN inner dim = 4·d_model |
| 10 | b | Ground-truth prefix fed during training |
| 11 | b | Pre-norm: LN before sub-layer; post-norm: after |
| 12 | c | GPT is decoder-only; BERT is encoder-only |
