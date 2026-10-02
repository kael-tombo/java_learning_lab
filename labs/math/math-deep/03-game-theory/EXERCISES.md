# Game Theory — Exercises (5 Problems with Hints)

---

## Problem 1: Finding All Nash Equilibria (2×3 Game)

**Find all Nash equilibria (pure and mixed) of the following game:**
```
        L       M       R
    U  (2,1)  (0,0)  (1,2)
    D  (0,0)  (1,2)  (2,1)
```

### Requirements:
- Check all 6 cells for pure NE
- Find mixed NE where Row mixes (U with p, D with 1-p)
- Find mixed NE where Column mixes (support on L,M,R)
- Verify indifference conditions
- Check if any strategy is strictly dominated

### Hints:
1. **Pure NE:** Check each cell. (U,L): Row 2 vs 0 ✓, Col 1 vs 0 (for M) and 1 vs 2 (for R) — wait, Col at L gets 1, at M gets 0, at R gets 2. So Col prefers R. Not NE.
   Actually: (U,L): Row gets 2 (vs 0 for D) ✓; Column gets 1 (vs 0 for M, vs 2 for R) → prefers R. Not NE.
   (U,M): Row 0 (vs 1 for D) → not NE.
   (U,R): Row 1 (vs 2 for D) → not NE.
   (D,L): Row 0 (vs 2 for U) → not NE.
   (D,M): Row 1 (vs 0 for U) ✓; Col 2 (vs 0 for L, vs 1 for R) ✓ → **NE!**
   (D,R): Row 2 (vs 1 for U) ✓; Col 1 (vs 2 for M) → not NE.

   Pure NE: **(D,M)** with payoffs (1,2).

2. **Mixed with Column on {L,M,R}:** Let Column play (q_L, q_M, q_R).
   Row U: 2q_L + 0q_M + 1q_R = 2q_L + q_R
   Row D: 0q_L + 1q_M + 2q_R = q_M + 2q_R
   Indifference: 2q_L + q_R = q_M + 2q_R

3. **Mixed with Row on {U,D}:** Let Row play (p, 1-p).
   Column L: 1p + 0(1-p) = p
   Column M: 0p + 2(1-p) = 2-2p
   Column R: 2p + 1(1-p) = p+1
   For Column to mix on all three: p = 2-2p = p+1 → impossible.

   Column must mix on subset. Try {L,R}: p = p+1 impossible.
   Try {L,M}: p = 2-2p → 3p=2 → p=2/3. Then q_M = 1-q_L.
   Row indifference with Col on {L,M}: 2q_L = q_M = 1-q_L → 3q_L=1 → q_L=1/3, q_M=2/3.
   Check Col R payoff at p=2/3: 2/3+1 = 5/3. Col L/M payoff = 2/3. R gives more! So Col deviates.
   Try {M,R}: 2-2p = p+1 → 3p=1 → p=1/3. Then q_R = 1-q_M.
   Row: q_M + 2q_R = q_M + 2(1-q_M) = 2-q_M. U: q_R = 1-q_M.
   Indifference: 1-q_M = 2-q_M → 1=2 impossible.

   So no fully mixed NE. But there may be NE with Row pure, Column mixed or vice versa.

---

## Problem 2: Zero-Sum Game via Linear Programming

**Solve the zero-sum game with payoff matrix (Row's payoff):**
$$A = \begin{bmatrix} 3 & -2 & 1 \\ -1 & 4 & 0 \\ 2 & -3 & 5 \end{bmatrix}$$
**Formulate and solve as a linear program to find the value and optimal strategies.**

### Requirements:
- Formulate Row's maximin problem as LP
- Formulate Column's minimax problem as LP
- Solve using simplex or any LP solver
- Verify value and strategies satisfy minimax theorem
- Implement in Java (simplex or use existing library)

### Hints:
1. **Row's LP (maximin):**
   Variables: $p_1, p_2, p_3 \geq 0$, $v$ (value)
   Maximize $v$
   Subject to:
   $3p_1 - p_2 + 2p_3 \geq v$
   $-2p_1 + 4p_2 - 3p_3 \geq v$
   $p_1 + 0p_2 + 5p_3 \geq v$
   $p_1 + p_2 + p_3 = 1$

2. **Standard form:** Convert to $\max v$ s.t. $Ap - v\mathbf{1} \geq 0$, $\mathbf{1}^T p = 1$.
   Can eliminate $v$ by setting $x_i = p_i/v$ (for $v>0$): maximize $\sum x_i$ s.t. $Ax \geq \mathbf{1}, x \geq 0$. Then $v = 1/\sum x_i$, $p = vx$.

3. **Column's LP (minimax):**
   Minimize $v$
   Subject to:
   $3q_1 - 2q_2 + q_3 \leq v$
   $-q_1 + 4q_2 + 0q_3 \leq v$
   $2q_1 - 3q_2 + 5q_3 \leq v$
   $q_1+q_2+q_3=1, q_i \geq 0$

4. **Duality:** Row's LP and Column's LP are duals. Optimal values equal.

5. **Expected solution:** Value around 1.5-2. Use simplex or graphical method for 3×3.

### Extension:
- Implement simplex method for general m×n zero-sum games.
- Add constraint that strategies must be in simplex.

---

## Problem 3: Iterated Prisoner's Dilemma Tournament

**Implement a tournament for Iterated Prisoner's Dilemma with the following strategies:**
1. **Always Cooperate (ALLC)**
2. **Always Defect (ALLD)**
3. **Tit-for-Tat (TFT)**: Cooperate first, then copy opponent's last move
4. **Grim Trigger (GRIM)**: Cooperate until opponent defects, then defect forever
5. **Pavlov (Win-Stay Lose-Shift)**: Repeat move if payoff ≥ 3, else switch

**Run round-robin with 200 rounds per pair, discount factor $\delta=0.99$. Report average scores and identify evolutionary stable strategies.**

### Requirements:
- Payoffs: (C,C)=3, (C,D)=0, (D,C)=5, (D,D)=1
- Discounted total: $\sum_{t=0}^{199} \delta^t r_t$
- Output: payoff matrix (5×5), average score per strategy
- Simulate evolutionary dynamics: replicator equation on strategy frequencies

### Hints:
1. **Strategy implementations:**
   - ALLC: always return C
   - ALLD: always return D
   - TFT: if round=0 return C, else return opponent_last_move
   - GRIM: track if opponent ever defected; if yes, D forever
   - Pavlov: if round=0 return C; if last payoff ≥ 3 repeat, else switch

2. **Pairwise interactions:**
   - TFT vs TFT: always (C,C) → 3 each round
   - TFT vs ALLD: round 0: (C,D) TFT gets 0; then (D,D) forever → 1 each
   - GRIM vs ALLD: same as TFT
   - ALLC vs ALLD: ALLC gets 0, ALLD gets 5 first round, then (D,D) or (C,D) depending...

3. **Discounted sum:** For 200 rounds with $\delta=0.99$, geometric series factor $\approx 1/(1-\delta) = 100$.

4. **Expected ranking:** ALLD exploits cooperators but does poorly against itself. TFT/GRIM do well against each other and resist exploitation.

### Extension:
- Add noise: with probability $\epsilon$, action flips.
- Test longer horizons, different $\delta$.
- Add more strategies: Generous TFT, 2TFT, etc.

---

## Problem 4: Bayesian Nash Equilibrium in First-Price Auction

**Two bidders in a first-price sealed-bid auction. Values $v_i \sim U[0,1]$ i.i.d. private. Find the symmetric Bayesian Nash equilibrium bidding function $\beta(v)$.**

### Requirements:
- Derive BNE bidding function analytically
- Implement simulation: draw values, compute bids, determine winner and payment
- Verify that truth-telling is not equilibrium (unlike second-price)
- Compute expected revenue and compare to second-price auction

### Hints:
1. **Symmetric equilibrium:** Assume $\beta(v)$ strictly increasing, differentiable.
2. **Bidder with value $v$ bidding $b$:** Wins if $\beta(v_j) < b \iff v_j < \beta^{-1}(b)$.
   Probability of winning: $G(\beta^{-1}(b)) = \beta^{-1}(b)$ (since $U[0,1]$).
   Expected payoff: $(v - b) \beta^{-1}(b)$.
3. **FOC at $b = \beta(v)$:**
   $\frac{d}{db}[(v-b)\beta^{-1}(b)]|_{b=\beta(v)} = 0$
   $-\beta^{-1}(b) + (v-b)\frac{1}{\beta'(\beta^{-1}(b))} = 0$
   At $b=\beta(v)$: $-v + (v-\beta(v))\frac{1}{\beta'(v)} = 0$
   $\beta'(v) = 1 - \frac{\beta(v)}{v}$
4. **Solve ODE:** $\beta'(v) + \frac{\beta(v)}{v} = 1$
   Integrating factor: $v$. $(v\beta(v))' = v \implies v\beta(v) = \frac{v^2}{2} + C$
   Boundary: $\beta(0)=0 \implies C=0$.
   **Solution: $\beta(v) = v/2$**.

5. **Expected revenue:** $E[\max(\beta(v_1), \beta(v_2))] = \frac{1}{2}E[\max(v_1,v_2)] = \frac{1}{2}\cdot\frac{2}{3} = \frac{1}{3}$.
   Second-price revenue: $E[\min(v_1,v_2)] = \frac{1}{3}$. Revenue equivalence!

### Extension:
- Generalize to $n$ bidders: $\beta(v) = \frac{n-1}{n}v$.
- Add risk aversion or asymmetric distributions.
- Compare with all-pay auction.

---

## Problem 5: Correlated Equilibrium via Linear Programming

**Find the correlated equilibrium that maximizes the sum of payoffs (social welfare) for the following game:**
```
        L       R
    U  (4,4)  (0,5)
    D  (5,0)  (1,1)
```

### Requirements:
- Formulate CE as linear program with variables $\mu_{UL}, \mu_{UR}, \mu_{DL}, \mu_{DR}$
- Constraints: incentive compatibility for each player and each deviation
- Objective: maximize $\sum \mu(s) (u_1(s) + u_2(s))$
- Solve LP and report $\mu^*$ and expected payoffs
- Compare with Nash equilibria (pure and mixed)

### Hints:
1. **Variables:** $\mu_{UL}, \mu_{UR}, \mu_{DL}, \mu_{DR} \geq 0$, sum = 1.
2. **Row's IC constraints:**
   - If recommended U: $4\mu_{UL} + 0\mu_{UR} \geq 5\mu_{UL} + 1\mu_{UR}$ → $-\mu_{UL} - \mu_{UR} \geq 0$ → $\mu_{UL}=\mu_{UR}=0$? Wait.
   
   Actually: conditional on recommended U, prob of L is $\mu_{UL}/(\mu_{UL}+\mu_{UR})$, prob of R is $\mu_{UR}/(\mu_{UL}+\mu_{UR})$.
   Expected payoff for U: $4\frac{\mu_{UL}}{\mu_U} + 0\frac{\mu_{UR}}{\mu_U} = \frac{4\mu_{UL}}{\mu_U}$
   Deviation to D: $5\frac{\mu_{UL}}{\mu_U} + 1\frac{\mu_{UR}}{\mu_U} = \frac{5\mu_{UL}+\mu_{UR}}{\mu_U}$
   IC: $4\mu_{UL} \geq 5\mu_{UL} + \mu_{UR} \implies -\mu_{UL} - \mu_{UR} \geq 0 \implies \mu_{UL}=\mu_{UR}=0$.
   
   Wait, this can't be right. Let me recheck payoffs.
   Row U: (4,4) vs L, (0,5) vs R
   Row D: (5,0) vs L, (1,1) vs R
   
   If recommended U (meaning Column plays according to $\mu_{UL},\mu_{UR}$):
   Row's payoff for U: $4 \cdot \frac{\mu_{UL}}{\mu_U} + 0 \cdot \frac{\mu_{UR}}{\mu_U}$
   Row's payoff for D: $5 \cdot \frac{\mu_{UL}}{\mu_U} + 1 \cdot \frac{\mu_{UR}}{\mu_U}$
   IC: $4\mu_{UL} \geq 5\mu_{UL} + \mu_{UR} \implies 0 \geq \mu_{UL} + \mu_{UR} \implies \mu_{UL}=\mu_{UR}=0$.
   
   So Row can never be recommended U in a CE! Similarly, if recommended D:
   Payoff D: $5\frac{\mu_{DL}}{\mu_D} + 1\frac{\mu_{DR}}{\mu_D}$
   Payoff U: $4\frac{\mu_{DL}}{\mu_D} + 0\frac{\mu_{DR}}{\mu_D}$
   IC: $5\mu_{DL} + \mu_{DR} \geq 4\mu_{DL} \implies \mu_{DL} + \mu_{DR} \geq 0$ (always true).
   
   Column's IC: If recommended L:
   Col L: $4\frac{\mu_{UL}}{\mu_L} + 0\frac{\mu_{DL}}{\mu_L} = 0$ (since $\mu_{UL}=0$)
   Col R: $5\frac{\mu_{UL}}{\mu_L} + 1\frac{\mu_{DL}}{\mu_L} = \frac{\mu_{DL}}{\mu_L}$
   IC: $0 \geq \mu_{DL} \implies \mu_{DL}=0$.
   
   If recommended R:
   Col R: $5\frac{\mu_{UR}}{\mu_R} + 1\frac{\mu_{DR}}{\mu_R} = \frac{\mu_{DR}}{\mu_R}$ (since $\mu_{UR}=0$)
   Col L: $4\frac{\mu_{UR}}{\mu_R} + 0\frac{\mu_{DR}}{\mu_R} = 0$
   IC: $\mu_{DR} \geq 0$ (always true).
   
   So only $\mu_{DR}=1$ is a CE? That's the pure NE (D,R) with payoffs (1,1).
   
   But wait — this game is a Prisoner's Dilemma variant! (U,L)=(4,4) is efficient but not NE.
   In standard PD, only correlated equilibrium is the NE (D,D). Let me verify.
   
   Actually, for CE, the correlation device can recommend *action profiles*, not just own action.
   The constraints I wrote are correct for standard CE definition.
   For this game, the only CE is the NE (D,R). But let's double-check.
   
   Hmm, in Battle of Sexes there are CEs that aren't NEs. This game is different.
   Let me try a different game for the exercise — one with interesting CEs.

**Revised Problem 5: Correlated Equilibrium in Battle of the Sexes**
```
        B       F
    B  (2,1)  (0,0)
    F  (0,0)  (1,2)
```
Find CE maximizing social welfare.

### Hints (Revised):
1. **Variables:** $\mu_{BB}, \mu_{BF}, \mu_{FB}, \mu_{FF} \geq 0$, sum = 1.
2. **Row IC if recommended B:**
   Payoff B: $2\mu_{BB} + 0\mu_{BF} = 2\mu_{BB}$
   Payoff F: $0\mu_{BB} + 1\mu_{BF} = \mu_{BF}$
   IC: $2\mu_{BB} \geq \mu_{BF}$

3. **Row IC if recommended F:**
   Payoff F: $0\mu_{FB} + 2\mu_{FF} = 2\mu_{FF}$
   Payoff B: $2\mu_{FB} + 1\mu_{FF}$? Wait: Row B gets 2 vs B, 0 vs F. Row F gets 0 vs B, 1 vs F.
   If recommended F (meaning Column plays B with prob $\mu_{FB}/\mu_F$, F with $\mu_{FF}/\mu_F$):
   Row F payoff: $0\frac{\mu_{FB}}{\mu_F} + 1\frac{\mu_{FF}}{\mu_F} = \frac{\mu_{FF}}{\mu_F}$
   Row B payoff: $2\frac{\mu_{FB}}{\mu_F} + 0\frac{\mu_{FF}}{\mu_F} = \frac{2\mu_{FB}}{\mu_F}$
   IC: $\mu_{FF} \geq 2\mu_{FB}$

4. **Column IC if recommended B:**
   Col B payoff: $1\frac{\mu_{BB}}{\mu_B} + 0\frac{\mu_{FB}}{\mu_B} = \frac{\mu_{BB}}{\mu_B}$
   Col F payoff: $0\frac{\mu_{BB}}{\mu_B} + 2\frac{\mu_{FB}}{\mu_B} = \frac{2\mu_{FB}}{\mu_B}$
   IC: $\mu_{BB} \geq 2\mu_{FB}$

5. **Column IC if recommended F:**
   Col F payoff: $0\frac{\mu_{BF}}{\mu_F} + 2\frac{\mu_{FF}}{\mu_F} = \frac{2\mu_{FF}}{\mu_F}$
   Col B payoff: $1\frac{\mu_{BF}}{\mu_F} + 0\frac{\mu_{FF}}{\mu_F} = \frac{\mu_{BF}}{\mu_F}$
   IC: $2\mu_{FF} \geq \mu_{BF}$

6. **Objective:** Maximize $2\mu_{BB} + 0 + 0 + 2\mu_{FF} + 1\mu_{BB} + 0 + 0 + 1\mu_{FF} = 3(\mu_{BB}+\mu_{FF})$

7. **Solution:** Put weight on (B,B) and (F,F). Let $\mu_{BF}=\mu_{FB}=0$.
   Then constraints: $2\mu_{BB} \geq 0$, $\mu_{FF} \geq 0$, $\mu_{BB} \geq 0$, $2\mu_{FF} \geq 0$ — all satisfied.
   Max $\mu_{BB}+\mu_{FF}$ subject to $\mu_{BB}+\mu_{FF}=1$.
   Optimal: any distribution on (B,B) and (F,F). E.g., $\mu_{BB}=0.5, \mu_{FF}=0.5$.
   Payoffs: $(0.5(2,1) + 0.5(1,2)) = (1.5, 1.5)$.

---

*End of Exercises*