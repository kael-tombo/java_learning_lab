# Debugging Guide: Linear Algebra

## Common Issues and Solutions

### 1. Numerical Instability
**Symptoms:** Results diverge or oscillate; small input changes cause large output changes.
**Solutions:**
- Use higher precision (double, BigDecimal)
- Reformulate the algorithm for numerical stability
- Add regularization or normalization
- Check condition numbers

### 2. Non-Convergence
**Symptoms:** Iterative algorithms don't converge or take too long.
**Solutions:**
- Increase iteration limit
- Adjust learning rate or step size
- Check initial conditions
- Verify the problem is well-posed
- Use line search or adaptive step sizes

### 3. Incorrect Results
**Symptoms:** Output differs from expected values.
**Solutions:**
- Verify against simple test cases
- Check boundary conditions
- Validate input assumptions
- Review index arithmetic
- Print intermediate values

### 4. Performance Issues
**Symptoms:** Algorithms run too slowly.
**Solutions:**
- Profile to find bottlenecks
- Use more efficient algorithms
- Cache intermediate results
- Parallelize independent computations
- Reduce memory allocations

## Debugging Workflow

1. **Reproduce:** Create minimal failing test case
2. **Isolate:** Determine which component fails
3. **Inspect:** Check inputs, intermediate values, outputs
4. **Hypothesize:** What could cause the observed behavior?
5. **Fix:** Implement the correction
6. **Verify:** Ensure the fix works and doesn't break other tests

## Tools

- IDE debugger (breakpoints, watch variables, step through)
- Unit tests with assertions
- Logging framework for tracing
- Profile for performance analysis
- Visualization tools for data inspection

## Preventive Measures

- Write tests before implementing (TDD)
- Use assertions to verify invariants
- Document numerical assumptions and limitations
- Validate inputs at API boundaries
- Use immutable data structures where possible
- Implement sanity checks for results
