# Benchmark — Test Performance

## Objective
Measure and optimize the execution time of your test suite.

## Instructions
1. Use @TestMethodOrder(MethodOrderer.OrderAnnotation.class) to run tests in a specific order
2. Measure total suite time
3. Identify the 3 slowest tests
4. Optimize them (mock more, reduce setup, parallelize)
5. Document before/after timings

## Expected Outcome
At least 50% reduction in total test suite execution time.
