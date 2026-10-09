# Debugging — Time Ordering

## Common Issues
1. **Non-monotonic clock**: Race condition, missing synchronization
2. **Causality violation**: receive() missing +1 or max()
3. **Incorrect concurrency**: Off-by-one in vector comparison

## Debugging Techniques
- Clock trace logging at each operation
- Generate DOT graphs of event causality
- Built-in health checks for monotonicity

## Diagnostic Tools
- Assertion framework for clock invariants
- Clock drift measurement relative to peers
- Post-mortem reconstruction from collected state
