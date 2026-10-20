# Reinforcement Learning — Quiz

Answers are stated after each question; none are trick questions.

**Q1. What does `V^pi(s)` represent?**
A: The expected discounted return when starting in state `s` and following policy `pi`
thereafter.

**Q2. Which equation links a state's value to its successors' values?**
A: The Bellman expectation equation: `V^pi(s) = sum_a pi(a|s) * sum_{s'} P(s'|s,a) [r + gamma V^pi(s')]`.

**Q3. Why can value iteration converge?**
A: The Bellman optimality operator contracts in the sup norm whenever `gamma < 1`, so
iterating toward the unique fixed point is guaranteed geometrically.

**Q4. Is Q-learning on-policy or off-policy, and why?**
A: Off-policy: its target maximizes over successor actions `max_a Q(s',a)` regardless of
the action the behavior policy actually executed.

**Q5. In our grid world, why is `V(s3) = 0` while `V(s1) = 1.0`?**
A: `s3` is terminal and values of terminal states stay zero; `s1` collects the entry
reward 1.0 immediately, and its discounted successor contributes nothing.

**Q6. What does `gamma` control, formally?**
A: How strongly future rewards count; with `gamma < 1`, returns stay bounded by
`r_max / (1 - gamma)` and the Bellman operator contracts.

**Q7. Epsilon-greedy: what happens as `epsilon -> 0` with an optimistic initialization?**
A: It becomes purely greedy, but optimism still forces early exploration because untried
arms carry above-possible estimates.

**Q8. Name the two classic dynamic-programming methods and the difference.**
A: Policy iteration (evaluate then improve policies) and value iteration (apply the
optimality operator directly); both reach `V*` with known `P` and `r`.

**Q9. Write the temporal-difference error definition.**
A: `delta = r + gamma * V(s') - V(s)` for a sampled transition; TD targets update values
along this residual.

**Q10. What does an optimistic initialization trade away?**
A: Guaranteed early exploration of every arm, paid for with slower settling once the
inflated estimates are spent — the direction our optimism exercise observes.

**Q11. What do the DP methods require that Q-learning does not?**
A: A full model `P` and reward table up front; Q-learning works from transition samples
without ever seeing the MDP's matrix.
