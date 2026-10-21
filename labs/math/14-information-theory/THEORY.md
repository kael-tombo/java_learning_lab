# Information Theory: A Comprehensive Treatment

## 1. Entropy and Information

### 1.1 Self-Information
The information content of an event with probability p is I(p) = -log₂(p) bits.

### 1.2 Shannon Entropy
H(X) = -Σ p(x) log₂ p(x)

Entropy measures the average uncertainty in a random variable. It represents the minimum number of bits needed to encode the variable optimally.

### 1.3 Properties of Entropy
- Non-negative: H(X) ≥ 0
- Maximum: H(X) ≤ log₂|X| (uniform distribution)
- H(X) = 0 iff X is deterministic
- Concave in p(x)

### 1.4 Joint Entropy
H(X, Y) = -Σ Σ p(x, y) log₂ p(x, y)

### 1.5 Conditional Entropy
H(Y|X) = Σ p(x) H(Y|X=x) = H(X, Y) - H(X)

## 2. Mutual Information

### 2.1 Definition
I(X; Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)

Mutual information measures how much knowing X reduces uncertainty about Y (and vice versa).

### 2.2 Properties
- I(X; Y) ≥ 0 with equality iff X and Y are independent
- I(X; Y) = I(Y; X)
- I(X; Y) = H(X) + H(Y) - H(X, Y)
- I(X; X) = H(X)

### 2.3 Chain Rule
I(X, Y; Z) = I(X; Z) + I(Y; Z|X)

### 2.4 Data Processing Inequality
If X → Y → Z (Markov chain), then I(X; Y) ≥ I(X; Z).

## 3. KL Divergence and Cross Entropy

### 3.1 Kullback-Leibler Divergence
D_KL(P||Q) = Σ p(x) log₂(p(x)/q(x))

KL divergence measures the inefficiency of using distribution Q to approximate distribution P.

### 3.2 Properties
- D_KL(P||Q) ≥ 0 with equality iff P = Q
- Not symmetric: D_KL(P||Q) ≠ D_KL(Q||P) generally
- Not a metric (doesn't satisfy triangle inequality)

### 3.3 Cross Entropy
H(P, Q) = H(P) + D_KL(P||Q) = -Σ p(x) log₂ q(x)

Cross entropy is widely used as a loss function in machine learning classification.

## 4. Channel Capacity

### 4.1 Definition
C = max_{p(x)} I(X; Y)

Channel capacity is the maximum rate at which information can be reliably transmitted through a noisy channel.

### 4.2 Binary Symmetric Channel (BSC)
For a BSC with crossover probability p:
C = 1 - H(p) where H(p) = -p log p - (1-p) log(1-p)

### 4.3 Shannon's Channel Coding Theorem
For any rate R < C, there exist codes that achieve arbitrarily low error probability. For R > C, reliable communication is impossible.

### 4.4 Continuous Channels
For additive white Gaussian noise (AWGN):
C = 0.5 log₂(1 + SNR) bits per channel use

## 5. Source Coding (Compression)

### 5.1 Shannon's Source Coding Theorem
The minimum expected code length satisfies H(X) ≤ L* < H(X) + 1.

### 5.2 Huffman Coding
Optimal prefix code that achieves the minimum expected length. Builds a binary tree from leaf probabilities.

### 5.3 Shannon-Fano Coding
Suboptimal prefix code using recursive splitting.

### 5.4 Arithmetic Coding
Encodes entire message as a single number in [0,1). Achieves near-optimal compression.

### 5.5 Lempel-Ziv Coding
Dictionary-based compression used in gzip, PNG, and many formats.

## 6. Differential Entropy

For continuous random variables:
h(X) = -∫ f(x) log₂ f(x) dx

### 6.1 Gaussian Distribution
For X ~ N(μ, σ²): h(X) = 0.5 log₂(2πeσ²) nats

### 6.2 Uniform Distribution
For X ~ Uniform[a,b]: h(X) = log₂(b-a)

## 7. Rate-Distortion Theory

### 7.1 Distortion Measures
- Hamming distortion: d(x, x̂) = 1 if x ≠ x̂, 0 otherwise
- Squared error: d(x, x̂) = (x - x̂)²

### 7.2 Rate-Distortion Function
R(D) = min_{p(x̂|x): E[d(X, X̂)] ≤ D} I(X; X̂)

## 8. Network Information Theory

### 8.1 Multiple Access Channel
Multiple senders, one receiver.
Capacity region defined by mutual information constraints.

### 8.2 Broadcast Channel
One sender, multiple receivers.

### 8.3 Relay Channel
Intermediate node helps forward information.

## 9. Applications

- Data compression (ZIP, MP3, JPEG, H.264)
- Error-correcting codes (LDPC, Turbo, Polar)
- Machine learning (cross-entropy loss, variational inference)
- Cryptography (key agreement, randomness extraction)
- Neuroscience (neural coding analysis)
- Natural language processing (mutual information for collocations)
- Feature selection (maximizing mutual information)

## 10. Historical Context

- 1948: Shannon's "A Mathematical Theory of Communication"
- 1950s: Huffman coding, channel capacity extensions
- 1960s: Rate-distortion theory
- 1970s: Network information theory
- 1990s: Turbo codes approach Shannon limit
- 2000s: Polar codes achieve symmetric capacity
- 2010s: Information-theoretic deep learning analysis
