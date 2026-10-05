# Probability Code Deep Dive (Python)

## 1. Basic Probability
```python
import random
import math

def probability_of_event(trials, event_func, experiment_func):
    """Estimate probability via Monte Carlo."""
    successes = sum(1 for _ in range(trials) if event_func(experiment_func()))
    return successes / trials

# Example: P(sum of two dice = 7)
def roll_two_dice():
    return random.randint(1, 6) + random.randint(1, 6)

p = probability_of_event(100000, lambda s: s == 7, roll_two_dice)
print(p)  # ≈ 0.1667
```

## 2. Discrete Distributions
```python
from math import comb, exp, factorial

def binomial_pmf(n, p, k):
    return comb(n, k) * p**k * (1-p)**(n-k)

def poisson_pmf(lam, k):
    return lam**k * exp(-lam) / factorial(k)

def geometric_pmf(p, k):
    return (1-p)**(k-1) * p

print(binomial_pmf(10, 0.5, 6))   # 0.205078125
print(poisson_pmf(3, 5))            # 0.10081881344492458
```

## 3. Continuous Distributions
```python
import numpy as np
from scipy import stats

# Normal distribution
print(stats.norm.cdf(1.96, loc=0, scale=1))   # 0.975
print(stats.norm.ppf(0.975, loc=0, scale=1))  # 1.96

# Exponential distribution
print(stats.expon.sf(1, scale=1/2))  # P(X > 1) = e^(-2)

# Sampling
samples = np.random.normal(100, 15, 10000)
print(np.mean(samples), np.std(samples))
```

## 4. Monte Carlo Integration
```python
def monte_carlo_integral(f, a, b, n=100000):
    """Estimate ∫[a,b] f(x)dx via Monte Carlo."""
    x = np.random.uniform(a, b, n)
    return (b - a) * np.mean(f(x))

# Estimate π: ∫[0,1] 4/(1+x²) dx = π
pi_estimate = monte_carlo_integral(lambda x: 4/(1+x**2), 0, 1)
print(pi_estimate)  # ≈ 3.14159
```

## 5. Markov Chain Simulation
```python
import numpy as np

def simulate_markov_chain(P, initial, steps):
    """Simulate a Markov chain."""
    states = [initial]
    current = initial
    for _ in range(steps):
        current = np.random.choice(len(P), p=P[current])
        states.append(current)
    return states

P = np.array([[0.7, 0.3], [0.4, 0.6]])
trajectory = simulate_markov_chain(P, 0, 1000)

# Estimate stationary distribution
stational = np.bincount(trajectory) / len(trajection)
print(stationatal)  # ≈ [0.571, 0.429]
```

## 6. Bayesian Inference
```python
def bayes_update(prior, likelihood, evidence):
    """Update P(H|E) = P(E|H)P(H) / P(E)."""
    return likelihood * prior / evidence

# Disease testing example
prior = 0.01          # P(disease)
sensitivity = 0.99    # P(positive | disease)
specificity = 0.99    # P(negative | no disease)

# P(positive) = P(positive|disease)P(disease) + P(positive|no disease)P(no disease)
p_positive = sensitivity * prior + (1 - specificity) * (1 - prior)
posterior = bayes_update(prior, sensitivity, p_positive)
print(posterior)  # ≈ 0.5
```

## 7. CLT Demonstration
```python
import matplotlib.pyplot as plt

def demonstrate_clt(n_samples=10000, sample_size=30):
    """Show that sample means are approximately normal."""
    means = [np.mean(np.random.exponential(1, sample_size))
             for _ in range(n_samples)]
    plt.hist(means, bins=50, density=True, alpha=0.7)
    # Overlay theoretical normal
    x = np.linspace(min(means), max(means), 100)
    plt.plot(x, stats.norm.pdf(x, loc=1, scale=1/np.sqrt(sample_size)))
    plt.show()
```

## 8. Performance Tips
- Use `numpy.random` for vectorized sampling (much faster than loops)
- `scipy.stats` has pre-computed CDFs, PPFs, and samplers
- Use `numba.jit` for tight simulation loops
- Vectorize probability calculations with numpy broadcasting
- For large Markov chains, use sparse matrix operations
