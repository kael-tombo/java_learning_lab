# Mathematical Foundations of AI Safety and Alignment

## 1. Introduction
This document provides a comprehensive treatment of the mathematical concepts underlying AI Safety and Alignment. Understanding these foundations is essential for developing intuition, implementing algorithms correctly, and advancing to more complex topics.

## 2. Probability Theory

### 2.1 Fundamentals
Probability theory quantifies uncertainty. A probability space consists of a sample space Ω (all possible outcomes), an event space F (set of events), and a probability measure P that assigns probabilities to events satisfying P(Ω)=1 and countable additivity.

### 2.2 Random Variables
A random variable X is a function from the sample space to real numbers. For discrete variables, the probability mass function p(x)=P(X=x). For continuous variables, the probability density function f(x) such that P(a≤X≤b)=âˆ«â‚áµ‡ f(x)dx.

### 2.3 Important Distributions
- **Normal (Gaussian)**: N(μ,σ²) with pdf f(x)=1/√(2πσ²)·exp(-(x-μ)²/(2σ²)). Central by the Central Limit Theorem.
- **Bernoulli**: Bern(p) for binary outcomes, P(X=1)=p, P(X=0)=1-p.
- **Categorical**: Generalization to K categories with probabilities pâ‚,...,p_K summing to 1.
- **Uniform**: U(a,b) where all values in [a,b] are equally likely.

### 2.4 Expectation and Moments
E[X]=∫x·f(x)dx or Σx·p(x). Variance σ²=E[(X-μ)²]=E[X²]-(E[X])². Covariance Cov(X,Y)=E[(X-μ_X)(Y-μ_Y)] measures linear dependence.

### 2.5 Bayes' Theorem
P(A|B)=P(B|A)P(A)/P(B). This is the foundation of Bayesian inference where we update prior beliefs P(θ) with data likelihood P(D|θ) to obtain posterior P(θ|D).

## 3. Linear Algebra

### 3.1 Vectors
A vector vâˆˆâ„â¿ is an ordered n-tuple. Operations include addition (u+v)ᵢ=uᵢ+vᵢ, scalar multiplication (αv)ᵢ=αvᵢ, and dot product u·v=Σuᵢvᵢ=||u||·||v||·cosθ.

### 3.2 Matrices
A matrix Aâˆˆâ„^(m×n) maps vectors from â„â¿ to â„áµ. Matrix multiplication (AB)ᵢⱼ=ΣₖAᵢₖBₖⱼ is associative but not commutative. The transpose Aᵀ has entries (Aᵀ)ᵢⱼ=Aⱼᵢ.

### 3.3 Eigenvalues and Eigenvectors
For square A, if Av=λv with v≠0, then v is an eigenvector with eigenvalue λ. The characteristic equation det(A-λI)=0 yields eigenvalues. Eigendecomposition A=QΛQâ»Â¹ diagonalizes A when eigenvectors are linearly independent.

### 3.4 Matrix Decompositions
- **SVD**: A=UΣVᵀ for any matrix, with orthogonal U,V and diagonal Σ of singular values
- **QR**: A=QR with orthogonal Q and upper triangular R
- **Cholesky**: A=LLᵀ for symmetric positive definite A

## 4. Calculus

### 4.1 Derivatives
The derivative f'(x)=lim_(h→0)(f(x+h)-f(x))/h measures instantaneous rate of change. Key rules include the power rule, product rule, quotient rule, and chain rule.

### 4.2 Multivariable Calculus
For f:â„â¿â†’â„, the gradient ∇f=(∂f/∂xâ‚,...,∂f/∂xₙ)ᵀ points in the direction of steepest increase. The Hessian Hᵢⱼ=∂²f/∂xᵢ∂xⱼ contains second derivatives.

### 4.3 Gradient Descent
θ(t+1)=θ(t)-η·∇L(θ(t)) iteratively minimizes loss L. The learning rate η controls step size. Convergence is guaranteed for convex functions with appropriate η.

## 5. Information Theory

### 5.1 Entropy
H(X)=-Σp(x)log₂p(x) measures average information content. Higher entropy means more uncertainty.

### 5.2 Cross-Entropy and KL Divergence
H(p,q)=-Σp(x)log q(x) measures coding efficiency. KL divergence D_KL(p||q)=Σp(x)log(p(x)/q(x))≥0 measures distribution difference, zero only when p=q.

### 5.3 Mutual Information
I(X;Y)=D_KL(p(x,y)||p(x)p(y))=H(X)-H(X|Y) measures dependence between variables.

## 6. Optimization Theory

### 6.1 Convex Optimization
A function f is convex if f(λx+(1-λ)y)≤λf(x)+(1-λ)f(y) for λ∈[0,1]. Convex functions have no local minima that are not global, making optimization tractable.

### 6.2 Stochastic Optimization
SGD uses mini-batches: θ(t+1)=θ(t)-η·(1/B)·Σ_{i∈batch}∇L_i(θ(t)). This adds noise that can help escape sharp minima.

### 6.3 Regularization Theory
Adding penalty Ω(θ) to loss: L_reg=L_data+λΩ(θ). L1 regularization Ω(θ)=||θ||â‚ promotes sparsity. L2 regularization Ω(θ)=||θ||₂² promotes small weights.

## 7. Statistical Learning Theory

### 7.1 Empirical Risk Minimization
True risk R(f)=E[L(f(X),Y)] is approximated by empirical risk R̂(f)=(1/n)ΣL(f(xᵢ),yᵢ). The gap between them is bounded by VC dimension or Rademacher complexity.

### 7.2 Bias-Variance Decomposition
E[(ŷ-y)²]=Bias[ŷ]²+Var[ŷ]+σ² where σ² is irreducible error. This decomposition guides model selection.

## 8. Conclusion
The mathematical foundations presented here are essential for understanding and implementing AI Safety and Alignment. Mastery enables better algorithm design, debugging, and innovation.
