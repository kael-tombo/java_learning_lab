# Window Functions — Math Foundation

## Why math shows up here
Window Functions decisions (indexes, sharding, caching) are quantitative: latency, cardinality, and probability all matter.

## Cardinality estimation
- Distinct-count estimates drive plan choices; error compounds ~exponentially with join count.
- Use HyperLogLog-style estimates: HLL with m registers has relative error ~1.04/sqrt(m).

## Cost model basics
- Cost ≈ pages_read * seq_page_cost + rows * cpu_tuple_cost.
- Selectivity = matching_rows / total_rows; aim for selectivity < 0.1 before an index pays off.

Worked example 1: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 2: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 3: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 4: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 5: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 6: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 7: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

Worked example 8: given N rows, selectivity s, and page size p, estimate pages touched and choose seq scan vs index for window functions.

- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
- Rule: a 10x estimation error on cardinality often flips the plan.
