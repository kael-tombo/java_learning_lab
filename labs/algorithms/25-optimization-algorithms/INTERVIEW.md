# Interview Questions: Optimization Algorithms

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 53 Maximum Subarray | Medium | Google, Meta, Microsoft | Kadane's algorithm |
| LC 300 Longest Increasing Subsequence | Medium | Google, Amazon, Meta | DP + patience sorting |
| LC 322 Coin Change | Medium | Google, Meta, Amazon | Unbounded knapsack DP |

Note: Optimization algorithms is primarily a **theoretical/metaheuristic** topic with few direct LC equivalents. Most interview questions focus on understanding of optimization paradigms.

## NeetCode Reference
Not directly covered. Gradient descent, simulated annealing, and genetic algorithms appear in ML system design discussions.

## Company-Specific Questions
### Google
- How would you optimize the serving infrastructure for Search to minimize latency subject to cost constraints?
- Explain how simulated annealing can solve the chip floorplanning problem
- Design a recommendation system optimizer balancing exploration vs exploitation (multi-armed bandit)

### Microsoft
- How does the Solver Foundation handle constraint optimization problems?
- Design an optimizer for Azure VM placement minimizing inter-VM latency
- Explain how Windows Update uses optimization for bandwidth-aware patching

### Meta
- How would you optimize ad delivery to maximize revenue given budget and pacing constraints?
- Design an optimizer for News Feed ranking with multiple objectives (engagement, diversity, recency)
- Explain gradient descent vs coordinate descent for large-scale ML training

### Amazon
- How does Amazon's supply chain optimizer determine inventory placement across fulfillment centers?
- Design a route optimizer for last-mile delivery with time windows (VRPTW)
- Explain how AWS Auto Scaling uses optimization to balance cost and performance

### Apple
- Design a battery optimizer for iOS that learns user charging patterns
- How does the LLVM compiler use optimization passes (loop unrolling, inlining)?
- Implement a memory allocator optimizer that minimizes fragmentation

### Oracle
- How does Oracle SQL optimizer choose between different join strategies (NL, hash, merge)?
- Design a query plan optimizer that considers statistics and cost models
- Explain how Oracle's cost-based optimizer (CBO) works with histograms and cardinality estimates

## Real Production Scenarios
- Scenario 1: Cloud cost optimization - using linear programming to minimize cloud spend subject to compute, memory, and SLA constraints across multiple regions
- Scenario 2: Warehouse robot routing - applying simulated annealing to optimize robot paths in an Amazon fulfillment center reducing travel time by 15%
- Scenario 3: CDN cache optimization - using genetic algorithms to determine optimal cache TTL values per content type to maximize hit ratio while minimizing staleness

## Interview Tips
- Understand the landscape: exact methods (LP, DP) vs approximate methods (heuristics, metaheuristics)
- Know the difference between convex and non-convex optimization (convex has guarantees)
- Be ready to discuss convergence criteria and stopping conditions for iterative methods
- Common edge cases: local minima vs global minima, constraint violations, unbounded solutions

## Java-Specific Considerations
- org.apache.commons.math3.optim provides optimization algorithms (simplex, CMA-ES, multi-start)
- java.util.function package enables functional programming patterns for objective functions
- Simulated annealing: implement with Math.exp((currentEnergy - neighborEnergy) / temperature) acceptance
- Genetic algorithms: represent chromosomes as BitSet, int[], or custom objects with crossover/mutate methods
- Pitfall: premature convergence in GA due to insufficient mutation rate
- Pitfall: numerical instability in floating-point objective functions; prefer double with epsilon comparisons
- Java is not ideal for heavy optimization workloads; consider calling Python/native libraries via JNI for production
