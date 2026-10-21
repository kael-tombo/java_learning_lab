# Debugging: Applied Linear Algebra Implementation

## Common Bugs

### Bug 1: Off-by-One Errors
**Fix**: Verify loop bounds and array indices (0-indexed).

### Bug 2: NaN Propagation
**Fix**: Check for division by zero, log of negative, sqrt of negative.

### Bug 3: Floating-Point Comparison
**Fix**: Use tolerance-based comparison: Math.abs(a - b) < epsilon.

### Bug 4: Integer Division
**Fix**: Cast to double: (double) a / b.

### Bug 5: Precision Loss
**Fix**: Identify subtractive cancellation, reformulate algorithm.

## Debugging Techniques

### Using Assertions
`java
assert Double.isFinite(result) : "Result must be finite";
`

### Print Debugging
`java
System.out.printf("DEBUG: x=%.6f, result=%.6f%n", x, result);
`

### Using a Debugger
1. Set breakpoints at key computation points
2. Step through with small test cases
3. Watch variables for unexpected values
