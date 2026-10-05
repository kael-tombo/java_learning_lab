# Feature Engineering - Mathematical Foundations

## Probability Theory

### Basic Probability
The foundation of Feature Engineering rests on probability theory. For events A and B:
- P(A union B) = P(A) + P(B) - P(A intersect B)
- P(A|B) = P(A intersect B) / P(B) (Conditional probability)

### Bayes' Theorem
P(A|B) = P(B|A) x P(A) / P(B)

This is fundamental for updating beliefs with new evidence, central to many feature creation, transformation, selection techniques.

## Descriptive Statistics

### Measures of Central Tendency
- **Mean**: mu = (sum of x_i) / n
- **Median**: Middle value of ordered data
- **Mode**: Most frequent value

### Measures of Dispersion
- **Variance**: sigma^2 = sum of (x_i - mu)^2 / n
- **Standard Deviation**: sigma = sqrt(sigma^2)
- **IQR**: Q3 - Q1 (Interquartile Range)

## Linear Algebra

### Vectors and Matrices
Feature spaces are represented as vectors. Operations include:
- Dot product: a.b = sum of a_i * b_i
- Matrix multiplication: C[i,j] = sum of A[i,k] * B[k,j]
- Transpose: A^T where A^T[i,j] = A[j,i]

### Eigenvalues and Eigenvectors
Av = lambda * v

Critical for dimensionality reduction techniques like PCA, which identify directions of maximum variance.

## Calculus

### Derivatives
Used in optimization algorithms:
- Gradient: grad(f) points in direction of steepest ascent
- Partial derivatives: df/dx_i for multivariate functions

### Chain Rule
df/dx = df/dg * dg/dx

Essential for backpropagation in neural networks and gradient-based optimization.

## Optimization

### Gradient Descent
theta_next = theta - alpha * grad(J(theta))

Where alpha is the learning rate. This iterative approach minimizes loss functions in model training.

### Convexity
A function is convex if f(lambda*x + (1-lambda)*y) <= lambda*f(x) + (1-lambda)*f(y). Convex problems have unique global minima.

## Information Theory

### Entropy
H(X) = -sum of p(x) * log(p(x))

Measures uncertainty in a random variable, foundational for decision trees and feature selection.

### Mutual Information
I(X;Y) = H(X) - H(X|Y)

Quantifies the information gained about one variable through another.

## Summary
These mathematical foundations enable rigorous understanding of Feature Engineering algorithms and their behavior under various conditions.
