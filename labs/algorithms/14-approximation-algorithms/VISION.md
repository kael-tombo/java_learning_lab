# Vision: Approximation Algorithms
> Provable near-optimality for problems where exact solutions cost too much.

## Where this leads
- Coping with NP-hard optimization in routing, covering, and scheduling tasks.
- Reading a ratio guarantee (2-approx, log-factor) as an engineering contract.
- The habit of pairing every heuristic with a brute-force check on small inputs.
## What mastering it unlocks
- Prove the greedy vertex-cover factor of 2 from the disjoint-edges argument.
- Run greedy set cover and state its logarithmic ratio in terms of the largest set.
- Compare LPT makespan against brute-force optimum on instances small enough to check.
- Explain why a ratio proof needs both an upper bound on the algorithm and a lower bound on optimum.
- Decide when an approximation is acceptable and when exact search is still required.
## What it does not cover
- Exact exponential methods (branch and bound, meet-in-the-middle live in other labs).
- PTAS constructions and hardness-of-approximation theory in full generality.
- Heuristics with no guarantee (simulated annealing, genetic search) as anything but baselines.
## Core questions you will answer
- Why does taking both endpoints of an uncovered edge give factor 2 and not worse?
- What charging argument makes greedy set cover logarithmic?
- Why must the optimum lower bound hold for every instance, not just the tested ones?
- For which inputs does LPT meet the optimum, and which input shape stresses it?
## How to judge progress
- Prove one ratio from scratch on a whiteboard without notes.
- Build the brute-force verifier for any new heuristic before trusting it.
- Name the ratio and the proof idea for each algorithm in this lab.
## Common misuse
- Quoting a ratio measured on tests as if it were a proven worst-case bound.
- Applying a minimization guarantee to a maximization problem without rechecking the math.
## After this lab
- 11-branch-and-bound for exact search that prunes with bounds.
- 25-optimization-algorithms for exact and heuristic optimization side by side.
One-line self-test: Prove the vertex-cover 2-approximation in four sentences or fewer.
