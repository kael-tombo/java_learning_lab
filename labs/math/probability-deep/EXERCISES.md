# Probability Exercises

## Basic Probability (Problems 1-4)

**1.** A fair die is rolled. What is P(even or prime)?
*Hint: Even = {2,4,6}, Prime = {2,3,5}. Use inclusion-exclusion.*

**2.** Two cards are drawn from a standard deck without replacement. What is P(both aces)?

**3.** Prove: P(A ∪ B) = P(A) + P(B) - P(A ∩ B).

**4.** If P(A) = 0.3, P(B) = 0.4, and A, B independent, find P(A ∪ B) and P(A|B).

## Conditional Probability and Bayes (Problems 5-7)

**5.** A disease affects 1% of the population. A test is 99% accurate (both sensitivity and specificity). If someone tests positive, what's the probability they have the disease?
*Hint: Bayes' theorem.*

**6.** Three boxes: Box 1 has 2 gold coins, Box 2 has 1 gold and 1 silver, Box 3 has 2 silver. A box is chosen at random and a coin drawn is gold. What's the probability it came from Box 1?

**7.** Prove Bayes' Theorem: P(A|B) = P(B|A)P(A)/P(B).

## Discrete Random Variables (Problems 8-11)

**8.** A fair coin is flipped 10 times. What is P(exactly 6 heads)?

**9.** Calls arrive at a call center at 3 per minute (Poisson). What is P(exactly 5 calls in 2 minutes)?

**10.** Find E[X] and Var(X) for X ~ Binomial(n=20, p=0.3).

**11.** A fair die is rolled until a 6 appears. What is the expected number of rolls?

## Continuous Random Variables (Problems 12-15)

**12.** X ~ Uniform(0, 10). Find P(2 < X < 7) and E[X].

**13.** X ~ Exponential(λ=2). Find P(X > 1) and E[X].

**14.** X ~ N(100, 15²). Find P(X > 130).
*Hint: Standardize and use Z-table; Z = (130-100)/15 = 2.*

**15.** Prove: For X ~ Exponential(λ), Var(X) = 1/λ².

## Joint Distributions (Problems 16-18)

**16.** X, Y independent with E[X]=2, E[Y]=3, Var(X)=4, Var(Y)=5. Find E[XY] and Var(X+Y).

**17.** If Cov(X,Y) = 3, Var(X) = 4, Var(Y) = 9, find the correlation ρ.

**18.** Prove: If X, Y independent, then E[XY] = E[X]E[Y].

## Limit Theorems (Problems 19-21)

**19.** A fair coin is flipped 1000 times. Approximate P(480 ≤ heads ≤ 520) using CLT.
*Hint: μ = 500, σ = √(1000·0.25) ≈ 15.8.*

**20.** State the Law of Large Numbers and explain its significance.

**21.** The sum of 100 i.i.d. random variables has mean 500 and variance 400. Approximate P(sum > 520).

## Markov Chains (Problems 22-25)

**22.** A Markov chain has transition matrix P = [[0.7, 0.3], [0.4, 0.6]]. Find the stationary distribution.

**23.** In the chain from Problem 22, if you start in state 1, what's the probability of being in state 2 after 2 steps?

**24.** Prove: For an ergodic Markov chain, the stationary distribution is unique.

**25.** A random walk on {0, 1, 2, 3} has absorbing barriers at 0 and 3. From state 1, you move to 0 or 2 with equal probability. From state 2, you move to 1 or 3 with equal probability. What is the probability of absorption at 3 starting from state 1?
