# Real-World Project: A/B Testing with Bayesian Inference

## Overview
Build a complete A/B testing framework using Bayesian methods. Unlike traditional frequentist approaches, Bayesian A/B testing provides interpretable results: "there's an 87% probability that variant B is better than A."

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Bayesian Methods for Hackers (Cameron Davidson-Pilon): https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers
- Google Optimize / Bayesian A/B Testing: https://vwo.com/blog/bayesian-ab-testing/

## Project Goals
1. Implement Bayesian conversion rate comparison
2. Compute credible intervals (not confidence intervals)
3. Determine probability of superiority
4. Calculate expected loss (when to stop testing)
5. Visualize posterior distributions over time

## Mathematical Background

### Bayesian Framework
- **Prior:** Initial belief about conversion rate: θ ~ Beta(α, β)
- **Likelihood:** Data (conversions) ~ Binomial(n, θ)
- **Posterior:** Updated belief: θ|data ~ Beta(α + conversions, β + non-conversions)

**Conjugate prior:** Beta prior + Binomial likelihood → Beta posterior. No numerical integration needed.

### Key Quantities
- **P(B > A):** Probability variant B converts better than A
- **Credible interval:** Range containing θ with probability (e.g., 95%)
- **Expected loss:** E[max(θ_A - θ_B, 0)] — expected conversion loss if you pick wrong variant

### Advantages over Frequentist
- Results are interpretable ("87% chance B is better")
- No fixed sample size required (peeking is OK)
- Incorporates prior knowledge
- Natural decision framework via expected loss

## Implementation Plan

### Phase 1: Posterior Computation
```python
from scipy import stats
import numpy as np

class BayesianABTest:
    def __init__(self, alpha=1, beta=1):
        """Initialize with uniform prior Beta(1, 1)."""
        self.alpha = alpha
        self.beta = beta

    def update(self, conversions, trials):
        """Update posterior with observed data."""
        self.alpha += conversions
        self.beta += (trials - conversions)
        return self.alpha, self.beta

    def posterior(self):
        """Return posterior distribution."""
        return stats.beta(self.alpha, self.beta)

    def sample_posterior(self, n=10000):
        """Draw samples from posterior."""
        return np.random.beta(self.alpha, self.beta, n)
```

### Phase 2: Comparison Metrics
```python
    def probability_better_than(self, other):
        """Compute P(self > other) via Monte Carlo."""
        samples_self = self.sample_posterior(100000)
        samples_other = other.sample_posterior(100000)
        return np.mean(samples_self > samples_other)

    def expected_loss(self, other):
        """Compute expected loss if we choose self over other."""
        samples_self = self.sample_posterior(100000)
        samples_other = other.sample_posterior(100000)
        return np.mean(np.maximum(samples_other - samples_self, 0))

    def credible_interval(self, level=0.95):
        """Compute credible interval."""
        dist = self.posterior()
        return dist.ppf((1 - level) / 2), dist.ppf(1 - (1 - level) / 2)
```

### Phase 3: Visualization
```python
import matplotlib.pyplot as plt

def plot_posteriors(test_a, test_b):
    """Plot posterior distributions for both variants."""
    x = np.linspace(0, max(test_a.alpha/(test_a.alpha+test_a.beta) * 3,
                           test_b.alpha/(test_b.alpha+test_b.beta) * 3), 1000)
    plt.plot(x, test_a.posterior().pdf(x), label='Variant A')
    plt.plot(x, test_b.posterior().pdf(x), label='Variant B')
    plt.xlabel('Conversion Rate')
    plt.ylabel('Density')
    plt.title('Posterior Distributions')
    plt.legend()
    plt.show()

def plot_probability_over_time(prob_history):
    """Plot P(B > A) as data accumulates."""
    plt.plot(prob_history)
    plt.axhline(0.95, color='r', linestyle='--', label='95% threshold')
    plt.xlabel('Sample size')
    plt.ylabel('P(B > A)')
    plt.title('Probability of Superiority Over Time')
    plt.legend()
    plt.show()
```

### Phase 4: Decision Engine
```python
def should_stop(test_a, test_b, threshold=0.95, max_loss=0.001):
    """Decide whether to stop the test."""
    p_better = test_b.probability_better_than(test_a)
    if p_better > threshold:
        return True, 'B is better'
    if p_better < 1 - threshold:
        return True, 'A is better'
    if test_b.expected_loss(test_a) < max_loss:
        return True, 'Practical equivalence'
    return False, 'Continue testing'
```

### Phase 5: Simulation
```python
def simulate_ab_test(true_rate_a, true_rate_b, n_per_day=1000, max_days=30):
    """Simulate a full A/B test."""
    test_a = BayesianABTest()
    test_b = BayesianABTest()
    history = []

    for day in range(max_days):
        # Simulate daily data
        conv_a = np.random.binomial(n_per_day, true_rate_a)
        conv_b = np.random.binomial(n_per_day, true_rate_b)
        test_a.update(conv_a, n_per_day)
        test_b.update(conv_b, n_per_day)

        p_better = test_b.probability_better_than(test_a)
        history.append(p_better)

        stop, reason = should_stop(test_a, test_b)
        if stop:
            print(f"Stopped on day {day+1}: {reason}")
            print(f"P(B > A) = {p_better:.3f}")
            break

    return test_a, test_b, history
```

## Validation
- Verify posterior matches analytical Beta update
- Compare with frequentist p-values for large samples
- Test decision engine on known scenarios
- Check that expected loss decreases as sample size grows

## Extensions
- Multi-armed bandit (Thompson sampling)
- Hierarchical Bayesian models
- Regression-based A/B testing (CUPED)
- Sequential testing with early stopping
- Bayesian hypothesis testing for continuous metrics

## Deliverables
- `bayesian_ab.py` — core Bayesian testing library
- `simulation.py` — A/B test simulator
- `visualize.py` — posterior and decision visualization
- `decision.py` — stopping rules and expected loss
- `README.md` — theory, usage, and interpretation guide
