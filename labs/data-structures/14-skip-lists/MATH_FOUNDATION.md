# Math Foundation of Skip Lists

## Expected Height

The probability that a node has level k is 1/2^k. The expected number of nodes at level k is n/2^k.

## Maximum Level

With MAX_LEVEL = ceil(log2(n)), the expected number of nodes at the top level is approximately 1.

## Expected Search Time

The search traverses down from the top level. At each level, the expected number of steps is O(1) due to the geometric distribution of nodes. The expected search time is O(log n).

## Probability of Degradation

The probability that a skip list with n elements has height > c*log(n) is O(1/n^(c-1)). For appropriately chosen MAX_LEVEL, the probability of poor performance is negligible.
