# Game Theory — Flashcards

---

## Basic Concepts

### Game Representation
**Q:** Normal-form game?
**A:** Tuple $(N, S_i, u_i)$: players $N$, strategies $S_i$, payoffs $u_i: S \to \mathbb{R}$.

**Q:** Pure strategy?
**A:** Deterministic choice of action.

**Q:** Mixed strategy?
**A:** Probability distribution over pure strategies: $\sigma_i \in \Delta(S_i)$.

**Q:** Expected payoff?
**A:** $u_i(\sigma) = \sum_{s \in S} (\prod_j \sigma_j(s_j)) u_i(s)$.

---

### Best Response & Nash Equilibrium
**Q:** Best response $BR_i(\sigma_{-i})$?
**A:** $\arg\max_{\sigma_i \in \Delta(S_i)} u_i(\sigma_i, \sigma_{-i})$.

**Q:** Pure Nash Equilibrium?
**A:** $s^*$ where $\forall i: s_i^* \in BR_i(s_{-i}^*)$ — no player benefits from unilateral deviation.

**Q:** Mixed Nash Equilibrium?
**A:** $\sigma^*$ where $\forall i: \sigma_i^* \in BR_i(\sigma_{-i}^*)$.

**Q:** Nash's Existence Theorem?
**A:** Every finite game has at least one mixed Nash equilibrium.

**Q:** Indifference principle?
**A:** In mixed NE, all pure strategies in support yield equal expected payoff (and no outside strategy yields more).

---

### Finding Nash Equilibria
**Q:** 2×2 pure NE?
**A:** Check each cell: is it a mutual best response?

**Q:** 2×2 mixed NE?
**A:** Row indifference: $q a + (1-q)b = q c + (1-q)d$ for Row's payoffs. Solve for $q$. Similarly for Column.

**Q:** Support enumeration?
**A:** Guess support sets, solve indifference equations, check if valid probabilities and no profitable deviations.

**Q:** Lemke-Howson algorithm?
**A:** Path-following algorithm for 2-player NE; finds one equilibrium.

---

## Zero-Sum Games

### Definition
**Q:** Zero-sum game?
**A:** $u_1(s) + u_2(s) = 0$ for all $s$; one player's gain = other's loss.

**Q:** Value of zero-sum game?
**A:** $v = \max_{\sigma_1} \min_{\sigma_2} u_1(\sigma_1, \sigma_2) = \min_{\sigma_2} \max_{\sigma_1} u_1(\sigma_1, \sigma_2)$ (Minimax Theorem).

**Q:** Minimax Theorem (von Neumann)?
**A:** Every finite zero-sum game has a value $v$ and optimal mixed strategies achieving it.

---

### Solving Zero-Sum Games
**Q:** 2×2 formula for value?
**A:** Matrix $\begin{bmatrix} a & b \\ c & d \end{bmatrix}$.
Value: $v = \frac{ad - bc}{a - b - c + d}$.
Optimal $p = \frac{d-c}{a-b-c+d}$, $q = \frac{d-b}{a-b-c+d}$.

**Q:** Linear programming formulation?
**A:** Row: $\max v$ s.t. $\sum_i p_i a_{ij} \geq v$, $\sum p_i = 1, p_i \geq 0$.
Column: $\min v$ s.t. $\sum_j a_{ij} q_j \leq v$, $\sum q_j = 1, q_j \geq 0$.

**Q:** Saddle point?
**A:** Pure strategy pair $(i^*, j^*)$ where $a_{i^*j} \leq a_{i^*j^*} \leq a_{ij^*}$ for all $i,j$. Value = $a_{i^*j^*}$.

---

## Classic Games

### Prisoner's Dilemma
**Q:** Payoffs?
**A:** (C,C) = (R,R), (C,D) = (S,T), (D,C) = (T,S), (D,D) = (P,P) with T > R > P > S and 2R > T+S.

**Q:** Dominant strategy?
**A:** Defect (D) strictly dominates Cooperate (C).

**Q:** Nash equilibrium?
**A:** (D,D) unique NE; Pareto dominated by (C,C).

**Q:** Iterated PD?
**A:** With discount factor $\delta$, Grim Trigger is SPNE iff $\delta \geq \frac{T-R}{T-P}$.

---

### Battle of the Sexes
**Q:** Payoffs?
**A:** Two pure NE with different payoffs; coordination game with conflict of interest.

**Q:** Pure NE?
**A:** (B,B) and (F,F) — both better than mismatch.

**Q:** Mixed NE?
**A:** Exists but payoffs lower than either pure NE.

---

### Matching Pennies
**Q:** Payoffs?
**A:** Zero-sum: Row wants match, Column wants mismatch. No pure NE.

**Q:** Mixed NE?
**A:** Both play (0.5, 0.5); value = 0.

---

### Chicken / Hawk-Dove
**Q:** Payoffs?
**A:** Two players; each can Swerve or Straight. (S,S) safe; (Straight, Swerve) wins; (Straight, Straight) disaster.

**Q:** Pure NE?
**A:** (Swerve, Straight) and (Straight, Swerve).

**Q:** Mixed NE?
**A:** Both randomize with probability depending on payoff ratios.

---

## Solution Concepts Beyond NE

### Subgame Perfect Equilibrium (SPE)
**Q:** Definition?
**A:** NE that induces NE in every subgame (backward induction in finite games).

**Q:** One-shot deviation principle?
**A:** Strategy profile is SPE iff no player can gain by a single deviation at any history.

**Q:** Centipede game?
**A:** Finite horizon → unique SPE is immediate defection by backward induction.

---

### Correlated Equilibrium
**Q:** Definition?
**A:** Distribution $\mu$ over $S$ such that for all $i$, $s_i$ with $\mu(s_i) > 0$:
$\sum_{s_{-i}} \mu(s_i, s_{-i}) u_i(s_i, s_{-i}) \geq \sum_{s_{-i}} \mu(s_i, s_{-i}) u_i(s_i', s_{-i})$.

**Q:** Relation to NE?
**A:** Every NE is a correlated equilibrium (product distribution); CE set is convex polytope containing NE.

**Q:** Example benefit?
**A:** Battle of Sexes: uniform on {(B,B), (F,F)} gives (1.5, 1.5) > mixed NE (0.67, 0.67).

---

### Evolutionary Game Theory
**Q:** Evolutionarily Stable Strategy (ESS)?
**A:** $\sigma^*$ such that $\forall \sigma \neq \sigma^*$: either $u(\sigma^*, \sigma^*) > u(\sigma, \sigma^*)$ or [$u(\sigma^*, \sigma^*) = u(\sigma, \sigma^*)$ and $u(\sigma^*, \sigma) > u(\sigma, \sigma)$].

**Q:** Replicator dynamics?
**A:** $\dot{x}_i = x_i (u_i(x) - \bar{u}(x))$ where $\bar{u} = \sum x_j u_j(x)$.

**Q:** ESS ↔ NE?
**A:** ESS ⇒ symmetric NE; strict NE ⇒ ESS.

---

## Bayesian Games

### Incomplete Information
**Q:** Bayesian game?
**A:** Players have private types $\theta_i \in \Theta_i$ drawn from common prior; payoffs $u_i(a, \theta)$.

**Q:** Strategy?
**A:** $\sigma_i: \Theta_i \to \Delta(A_i)$ — action depends on own type.

**Q:** Bayesian Nash Equilibrium (BNE)?
**A:** $\sigma^*$ where $\forall i, \theta_i$: $\sigma_i^*(\theta_i) \in \arg\max_{\sigma_i} E_{\theta_{-i}}[u_i(\sigma_i, \sigma_{-i}^*(\theta_{-i}), (\theta_i, \theta_{-i}))]$.

**Q:** Interim vs. Ex-ante?
**A:** Interim: optimize given own type; Ex-ante: optimize before type realized. Equivalent for BNE.

---

## Mechanism Design

### Incentive Compatibility
**Q:** Direct mechanism?
**A:** Players report types; mechanism chooses outcome: $\mathcal{M} = (\Theta, X, f, t)$.

**Q:** Incentive Compatible (IC)?
**A:** Truth-telling is BNE: $\forall \theta_i, \theta_i'$: $E[u_i(f(\theta_i, \theta_{-i}), \theta_i) - t_i(\theta_i, \theta_{-i})] \geq E[u_i(f(\theta_i', \theta_{-i}), \theta_i) - t_i(\theta_i', \theta_{-i})]$.

**Q:** Individual Rationality (IR)?
**A:** Expected utility $\geq$ outside option (usually 0).

**Q:** Revenue Equivalence Theorem?
**A:** For independent private values, any IC/IR mechanism with same allocation gives same expected revenue.

**Q:** VCG Mechanism?
**A:** Efficient allocation (max welfare); payments = externality imposed on others. IC, IR, efficient.

---

## Computational Game Theory

### Complexity
**Q:** Finding one NE?
**A:** PPAD-complete (even for 2-player); no known polynomial algorithm.

**Q:** Zero-sum NE?
**A:** Polynomial time via linear programming.

**Q:** Correlated equilibrium?
**A:** Polynomial time via linear programming (ellipsoid/interior point).

**Q:** Pure NE existence?
**A:** NP-complete to decide (Party Affiliation game).

---

### Algorithms
**Q:** Fictitious Play?
**A:** Each player best-responds to empirical frequency of opponent's play. Converges in zero-sum, potential games.

**Q:** Regret Matching?
**A:** Play proportional to positive regret; converges to correlated equilibrium.

**Q:** Counterfactual Regret Minimization (CFR)?
**A:** For extensive-form games; decomposes regret by infoset; used in poker AI.

**Q:** Double Oracle?
**A:** Iteratively add best responses to restricted game; column/row generation for NE.

---

*End of Flashcards*