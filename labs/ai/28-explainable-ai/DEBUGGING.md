# Debugging: Explainable AI

## 1. Debugging Principles
- Reproduce the issue reliably
- Isolate the root cause
- Fix the underlying problem, not symptoms
- Add regression tests after fixing

## 2. Common Issues

### 2.1 Numerical Issues
- NaN: Division by zero, log(0), overflow
- Infinity: Extreme values without gradient clipping
- Loss not decreasing: Learning rate issues, wrong initialization

### 2.2 Training Issues
- Overfitting: Validation loss increases while training decreases
- Underfitting: Both losses are high
- Oscillating loss: Learning rate too high

### 2.3 Implementation Bugs
- Off-by-one errors in indexing
- Wrong loss function implementation
- Incorrect gradient computation

## 3. Debugging Tools
- Logging gradient statistics (mean, min, max)
- Monitoring activation distributions
- Plotting learning curves
- Gradient checking (numerical vs analytical)

## 4. Step-by-Step
1. Reproduce the issue with minimal example
2. Formulate hypotheses about root cause
3. Design experiments to test each hypothesis
4. Isolate the bug with binary search
5. Implement and verify the fix
6. Add regression tests
