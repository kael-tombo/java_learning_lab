# Mini Project: Probability Distribution Explorer

## Goal
Build an interactive tool that visualizes, samples from, and computes properties of probability distributions. Users can compare distributions, overlay PDFs/PMFs, and explore how parameters affect shape.

## Requirements
1. Support 10+ distributions (Binomial, Poisson, Normal, Exponential, Uniform, Gamma, Beta, Geometric, Hypergeometric, Chi-squared)
2. Plot PDF/PMF and CDF side by side
3. Compute and display: mean, variance, skewness, kurtosis
4. Generate random samples and overlay histogram on theoretical curve
5. Interactive parameter sliders
6. Compare two distributions overlayed

## Architecture
```python
class Distribution:
    def __init__(self, name, params): ...
    def pdf(self, x): ...
    def cdf(self, x): ...
    def sample(self, n): ...
    def mean(self): ...
    def variance(self): ...
    def skewness(self): ...
    def kurtosis(self): ...
```

## Step 1: Distribution Base Class
```python
from scipy import stats
import numpy as np

class Distribution:
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.dist = getattr(stats, name)(**params)

    def pdf(self, x):
        return self.dist.pdf(x)

    def cdf(self, x):
        return self.dist.cdf(x)

    def sample(self, n):
        return self.dist.rvs(n)

    def mean(self):
        return self.dist.mean()

    def variance(self):
        return self.dist.var()

    def skewness(self):
        return self.dist.stats(moments='s')

    def kurtosis(self):
        return self.dist.stats(moments='k')
```

## Step 2: Visualization
```python
import matplotlib.pyplot as plt

class DistributionExplorer:
    def __init__(self, dist1, dist2=None):
        self.dist1 = dist1
        self.dist2 = dist2

    def plot_pdf(self, x_range=(-5, 5)):
        x = np.linspace(x_range[0], x_range[1], 1000)
        plt.plot(x, self.dist1.pdf(x), label=self.dist1.name)
        if self.dist2:
            plt.plot(x, self.dist2.pdf(x), label=self.dist2.name)
        plt.legend()
        plt.title('Probability Density/Mass Function')
        plt.show()

    def plot_cdf(self, x_range=(-5, 5)):
        x = np.linspace(x_range[0], x_range[1], 1000)
        plt.plot(x, self.dist1.cdf(x), label=self.dist1.name)
        if self.dist2:
            plt.plot(x, self.dist2.cdf(x), label=self.dist2.name)
        plt.legend()
        plt.title('Cumulative Distribution Function')
        plt.show()

    def plot_sample(self, n=1000):
        samples = self.dist1.sample(n)
        plt.hist(samples, bins=50, density=True, alpha=0.6, label='Sample')
        x = np.linspace(min(samples), max(samples), 1000)
        plt.plot(x, self.dist1.pdf(x), 'r-', label='Theoretical')
        plt.legend()
        plt.title(f'Sample Histogram (n={n})')
        plt.show()
```

## Step 3: Property Comparison
```python
def compare_properties(dist1, dist2):
    props = ['Mean', 'Variance', 'Skewness', 'Kurtosis']
    vals1 = [dist1.mean(), dist1.variance(), dist1.skewness(), dist1.kurtosis()]
    vals2 = [dist2.mean(), dist2.variance(), dist2.skewness(), dist2.kurtosis()]
    for p, v1, v2 in zip(props, vals1, vals2):
        print(f"{p:12s}: {v1:10.4f} vs {v2:10.4f}")
```

## Step 4: Interactive Mode
```python
# Example usage
normal = Distribution('norm', {'loc': 0, 'scale': 1})
exponential = Distribution('expon', {'scale': 1})

explorer = DistributionExplorer(normal, exponential)
explorer.plot_pdf()
explorer.plot_cdf()
explorer.plot_sample(n=5000)
```

## Testing
```python
# Verify properties match theoretical values
norm = Distribution('norm', {'loc': 10, 'scale': 2})
assert abs(norm.mean() - 10) < 0.01
assert abs(norm.variance() - 4) < 0.01
```

## Extensions
- Add multivariate distributions (bivariate normal)
- Hypothesis testing visualization
- Interactive widgets with ipywidgets
- Export plots and statistics to PDF
- Fit distribution to data (MLE)

## Deliverables
- `distributions.py` — distribution classes
- `explorer.py` — visualization engine
- `test_distributions.py` — unit tests
- `README.md` — usage examples
