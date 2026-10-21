# Math Foundation for Testing

## Combinatorics in Parameterized Tests

Understanding test combinatorics helps design efficient test suites.

### Number of Test Cases

For a method with 
 parameters each having _i possible values, exhaustive testing requires product(v_i) tests. This grows exponentially:

`java
// Method with 3 boolean parameters = 2^3 = 8 tests
void process(boolean a, boolean b, boolean c) { ... }
`

### Combinatorial (Pairwise) Testing

Instead of testing all combinations, pairwise testing tests every pair of parameter values. For most systems, pairwise catches 90%+ of bugs at a fraction of the cost.

### Boundary Value Analysis

For numeric inputs, test at boundaries:
- Minimum value: int min = Integer.MIN_VALUE
- Just above minimum: int nearMin = Integer.MIN_VALUE + 1
- Nominal: int mid = 0
- Just below maximum: int nearMax = Integer.MAX_VALUE - 1
- Maximum: int max = Integer.MAX_VALUE

For each boundary, test both the value and its immediate neighbors.

### Equivalence Partitioning

Divide inputs into partitions where all values in a partition are treated identically by the code:
- Valid partition: values the method should handle (e.g., positive integers for sqrt)
- Invalid partition: values the method should reject (e.g., negative numbers for sqrt)

One test per partition is usually sufficient.

## Code Coverage Mathematics

### Line Coverage

`
line coverage = (lines executed / total executable lines) x 100%
`

### Branch Coverage

Each if/else creates two branches. For nested conditions, branches multiply:
`
branch coverage = (branches taken / total branches) x 100%
`

### Cyclomatic Complexity

M = E - N + 2P where:
- E = number of edges in control flow graph
- N = number of nodes
- P = number of connected components

Higher complexity means more paths to test. Aim for M < 10 per method.

## Mutation Testing

Mutation testing introduces small syntactic changes (mutants):
- Replace + with -
- Invert condition > to <=
- Delete method call

A test suite's quality = percentage of mutants "killed" (caught by tests). Higher is better.
