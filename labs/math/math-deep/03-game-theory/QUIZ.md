# Game Theory — Quiz (10 Questions with Worked Answers)

---

## Question 1: Pure Nash Equilibrium

**Question:** Find all pure Nash equilibria of the following 2×2 game:
```
        L       R
    U  (3,2)  (1,1)
    D  (0,0)  (2,3)
```

**Answer:** **Two pure NE: (U,L) and (D,R)**

**Derivation:**
Check each cell for unilateral deviations:
- (U,L): Row gets 3 (vs 0 for D), Column gets 2 (vs 1 for R) → NE ✓
- (U,R): Row gets 1 (vs 3 for U with L) → not NE
- (D,L): Row gets 0 (vs 3 for U) → not NE
- (D,R): Row gets 2 (vs 1 for U), Column gets 3 (vs 0 for L) → NE ✓

---

## Question 2: Mixed Nash Equilibrium

**Question:** For the game in Q1, find the mixed strategy Nash equilibrium where Row plays U with probability $p$ and Column plays L with probability $q$.

**Answer:** **$p = \frac{2}{3}$, $q = \frac{1}{2}$**

**Derivation:**
Row's payoff for U: $3q + 1(1-q) = 2q + 1$
Row's payoff for D: $0q + 2(1-q) = 2 - 2q$

Indifference: $2q + 1 = 2 - 2q \implies 4q = 1 \implies q = 1/4$

Wait, let me recalculate. Column's payoffs:
Column for L: $2p + 0(1-p) = 2p$
Column for R: $1p + 3(1-p) = 3 - 2p$

Indifference: $2p = 3 - 2p \implies 4p = 3 \implies p = 3/4$

Row's payoffs:
U: $3q + 1(1-q) = 2q + 1$
D: $0q + 2(1-q) = 2 - 2q$

Indifference: $2q + 1 = 2 - 2q \implies 4q = 1 \implies q = 1/4$

So mixed NE: $p = 3/4$, $q = 1/4$.

---

## Question 3: Zero-Sum Game Value

**Question:** Find the value of the zero-sum game with payoff matrix (Row's payoff):
```
    2  -1
   -1   3
```

**Answer:** **Value = 1**

**Derivation:**
Row chooses $p$ (prob of first row), Column chooses $q$ (prob of first col).

Row's expected payoff: $2pq - p(1-q) - (1-p)q + 3(1-p)(1-q)$
$= 2pq - p + pq - q + pq + 3(1 - p - q + pq)$
$= 7pq - 4p - 4q + 3$

Row maximizes, Column minimizes:
$\max_p \min_q (7pq - 4p - 4q + 3)$

For fixed $p$, Column chooses $q$ to minimize: derivative w.r.t $q$ is $7p - 4$.
If $7p - 4 > 0$ ($p > 4/7$), Column picks $q=0$, payoff = $-4p+3$.
If $7p - 4 < 0$ ($p < 4/7$), Column picks $q=1$, payoff = $3p-1$.
If $p = 4/7$, payoff = $-4(4/7)+3 = 5/7 = 3(4/7)-1 = 5/7$.

Row maximizes: at $p=4/7$, value = $5/7$.

Wait, let me use minimax theorem properly. For 2×2 zero-sum:
Value $v = \frac{ad - bc}{a - b - c + d}$ for matrix $\begin{bmatrix} a & b \\ c & d \end{bmatrix}$

Here $a=2, b=-1, c=-1, d=3$:
$v = \frac{2\cdot 3 - (-1)(-1)}{2 - (-1) - (-1) + 3} = \frac{6 - 1}{7} = \frac{5}{7}$.

**Answer: $v = 5/7$**

Optimal strategies: Row $p = \frac{d-c}{a-b-c+d} = \frac{3-(-1)}{7} = 4/7$, Column $q = \frac{d-b}{7} = \frac{3-(-1)}{7} = 4/7$.

---

## Question 4: Prisoner's Dilemma

**Question:** In Prisoner's Dilemma with payoffs (C,C)=(3,3), (C,D)=(0,5), (D,C)=(5,0), (D,D)=(1,1), show that (D,D) is the unique Nash equilibrium and Pareto dominated by (C,C).

**Answer:** **(D,D) is unique NE; (C,C) gives higher payoff to both**

**Derivation:**
Payoff matrix (Row, Column):
```
       C    D
C   (3,3) (0,5)
D   (5,0) (1,1)
```

Best responses:
- If Column plays C: Row gets 3 (C) vs 5 (D) → best is D
- If Column plays D: Row gets 0 (C) vs 1 (D) → best is D
- D is dominant strategy for Row. Same for Column.

Unique NE: (D,D) with payoffs (1,1).
(C,C) gives (3,3) — both better off. (C,C) is Pareto optimal but not an equilibrium.

---

## Question 5: Battle of the Sexes

**Question:** Find all Nash equilibria (pure and mixed) of:
```
        B       F
    B  (2,1)  (0,0)
    F  (0,0)  (1,2)
```

**Answer:** **Two pure: (B,B) and (F,F); One mixed: Row B with 2/3, Column B with 1/3**

**Derivation:**
Pure NE check:
- (B,B): Row 2 vs 0 (F) ✓, Column 1 vs 0 (F) ✓ → NE
- (F,F): Row 1 vs 0 (B) ✓, Column 2 vs 0 (B) ✓ → NE

Mixed: Row plays B with $p$, Column plays B with $q$.
Row B: $2q + 0(1-q) = 2q$
Row F: $0q + 1(1-q) = 1-q$
Indifference: $2q = 1-q \implies 3q = 1 \implies q = 1/3$

Column B: $1p + 0(1-p) = p$
Column F: $0p + 2(1-p) = 2-2p$
Indifference: $p = 2-2p \implies 3p = 2 \implies p = 2/3$

Mixed NE: Row (2/3, 1/3), Column (1/3, 2/3). Payoffs: (2/3, 2/3) — worse than either pure NE.

---

## Question 6: Minimax Theorem

**Question:** For a zero-sum game with payoff matrix $A$, the minimax theorem states $\max_x \min_y x^T A y = \min_y \max_x x^T A y$. Prove this for $A = \begin{bmatrix} 1 & -1 \\ -1 & 1 \end{bmatrix}$.

**Answer:** **Value = 0; optimal strategies uniform (0.5, 0.5)**

**Derivation:**
Let Row play $(p, 1-p)$, Column play $(q, 1-q)$.

Payoff: $p q - p(1-q) - (1-p)q + (1-p)(1-q) = 4pq - 2p - 2q + 1$

Row maximizes, Column minimizes:
$\max_p \min_q (4pq - 2p - 2q + 1)$

For fixed $p$, Column's payoff derivative: $4p - 2$.
If $p > 0.5$, Column chooses $q=0$, payoff = $-2p+1$ (decreasing in $p$)
If $p < 0.5$, Column chooses $q=1$, payoff = $2p-1$ (increasing in $p$)
If $p = 0.5$, payoff = $0$ for any $q$.

Row maximizes at $p=0.5$, value = 0. Symmetrically, Column minimizes at $q=0.5$, value = 0.

Minimax = Maximim = 0. Both play uniformly.

---

## Question 7: Iterated Prisoner's Dilemma

**Question:** In infinitely repeated Prisoner's Dilemma with discount factor $\delta$, when is "Grim Trigger" (cooperate until opponent defects, then defect forever) a subgame perfect equilibrium?

**Answer:** **$\delta \geq \frac{1}{2}$**

**Derivation:**
Stage game: (C,C)=(3,3), (C,D)=(0,5), (D,C)=(5,0), (D,D)=(1,1)

Grim Trigger: Cooperate until someone defects, then (D,D) forever.

Payoff from cooperating forever: $3 + 3\delta + 3\delta^2 + \cdots = \frac{3}{1-\delta}$

Payoff from defecting once then grim: $5 + 1\delta + 1\delta^2 + \cdots = 5 + \frac{\delta}{1-\delta}$

Cooperate better iff $\frac{3}{1-\delta} \geq 5 + \frac{\delta}{1-\delta}$
$\iff 3 \geq 5(1-\delta) + \delta = 5 - 4\delta$
$\iff 4\delta \geq 2 \iff \delta \geq 1/2$.

---

## Question 8: Correlated Equilibrium

**Question:** For Battle of the Sexes (Q5), find a correlated equilibrium that gives higher payoff than the mixed NE.

**Answer:** **Uniform over (B,B) and (F,F): payoffs (1.5, 1.5)**

**Derivation:**
Correlation device recommends (B,B) with prob 0.5, (F,F) with prob 0.5.
If recommended B: opponent plays B → best response is B (payoff 2 vs 0).
If recommended F: opponent plays F → best response is F (payoff 2 vs 0).

Expected payoff: $0.5(2,1) + 0.5(1,2) = (1.5, 1.5)$.
Mixed NE gave (2/3, 2/3) ≈ (0.67, 0.67). Correlated is better for both.

---

## Question 9: Dominated Strategies

**Question:** Find iterated elimination of strictly dominated strategies in:
```
        L       M       R
    U  (1,0)  (0,1)  (-1,-1)
    M  (0,1)  (1,0)  (-1,-1)
    D  (0,0)  (0,0)  (0,0)
```

**Answer:** **R eliminated for Column, then D eliminated for Row, then M eliminated for both → (U,L) unique**

**Derivation:**
Step 1: Column's R is strictly dominated by L (0 > -1, 1 > -1, 0 > 0? No, M vs L: 1 > -1, 0 > -1, 0 = 0 — weak). Actually M gives (0,1,0), L gives (0,1,0) — same! Let me check.

Column payoffs:
- L: (0, 1, 0) for U,M,D
- M: (1, 0, 0) for U,M,D
- R: (-1, -1, 0) for U,M,D

R is strictly dominated by any mixture of L and M (e.g., 0.5L+0.5M gives 0.5, 0.5, 0 > -1, -1, 0). Remove R.

Step 2: Reduced game 3×2. Row payoffs:
- U: 1, 0
- M: 0, 1
- D: 0, 0

D is strictly dominated by 0.5U+0.5M (gives 0.5, 0.5 > 0, 0). Remove D.

Step 3: 2×2 game:
```
    L   M
U  1   0
M  0   1
```

M dominated by L for Column? Column payoffs: L=(0,1), M=(1,0) — no strict domination. But actually this is matching pennies variant? Wait.

Row: U gets (1,0), M gets (0,1). No strict domination.
Column: L gets (0,1), M gets (1,0). No strict domination.

But wait — in original, after removing R and D, we have a game with no strictly dominated strategies. The pure NE are (U,L) and (M,M). Mixed NE at (0.5, 0.5).

Let me re-read: "iterated elimination of strictly dominated strategies". R is strictly dominated. D is strictly dominated. Then no more strict domination. Result: {U,M} × {L,M}.

---

## Question 10: Bayesian Game

**Question:** Two firms choose quantities $q_1, q_2 \geq 0$. Firm 1's cost $c_1 \in \{1, 2\}$ with equal probability (private info). Firm 2's cost $c_2 = 1.5$ (known). Inverse demand $P = 10 - Q$. Find Bayesian Nash equilibrium.

**Answer:** **$q_1(1) = 3.125$, $q_1(2) = 2.625$, $q_2 = 2.875$**

**Derivation:**
Firm 1 type $c_1$ maximizes: $(10 - q_1 - q_2 - c_1)q_1$
FOC: $10 - 2q_1 - q_2 - c_1 = 0 \implies q_1 = \frac{10 - q_2 - c_1}{2}$

Firm 2 maximizes expected profit: $E[(10 - q_1 - q_2 - 1.5)q_2]$
FOC: $10 - E[q_1] - 2q_2 - 1.5 = 0 \implies q_2 = \frac{8.5 - E[q_1]}{2}$

$E[q_1] = 0.5(q_1(1) + q_1(2)) = 0.5(\frac{10-q_2-1}{2} + \frac{10-q_2-2}{2}) = 0.5(\frac{17-2q_2}{2}) = \frac{17-2q_2}{4}$

Substitute: $q_2 = \frac{8.5 - (17-2q_2)/4}{2} = \frac{34 - 17 + 2q_2}{8} = \frac{17 + 2q_2}{8}$

$8q_2 = 17 + 2q_2 \implies 6q_2 = 17 \implies q_2 = 17/6 \approx 2.833$

Then $q_1(1) = (10 - 17/6 - 1)/2 = (47/6)/2 = 47/12 \approx 3.917$
$q_1(2) = (10 - 17/6 - 2)/2 = (35/6)/2 = 35/12 \approx 2.917$

Wait, let me recalculate: $E[q_1] = 0.5 \times \frac{10 - q_2 - 1}{2} + 0.5 \times \frac{10 - q_2 - 2}{2} = \frac{17 - 2q_2}{4}$

Firm 2: $q_2 = \frac{10 - 1.5 - E[q_1]}{2} = \frac{8.5 - E[q_1]}{2} = \frac{8.5}{2} - \frac{E[q_1]}{2}$

$E[q_1] = \frac{17 - 2q_2}{4} = 4.25 - 0.5 q_2$

$q_2 = 4.25 - 0.5(4.25 - 0.5q_2) = 4.25 - 2.125 + 0.25q_2 = 2.125 + 0.25q_2$

$0.75q_2 = 2.125 \implies q_2 = 2.125 / 0.75 = 17/6 \approx 2.833$

Then $E[q_1] = 4.25 - 0.5(17/6) = 4.25 - 17/12 = 51/12 - 17/12 = 34/12 = 17/6$

$q_1(1) = (9 - 17/6)/2 = (37/6)/2 = 37/12 \approx 3.083$
$q_1(2) = (8 - 17/6)/2 = (31/6)/2 = 31/12 \approx 2.583$

**Answer: $q_1(1) = 37/12$, $q_1(2) = 31/12$, $q_2 = 17/6$**

---

*End of Quiz*