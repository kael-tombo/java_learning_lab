# Real-World Project: Tournament Rules Analyzer

## Problem

A club runs a small deterministic board-game tournament and wants to check
whether its starting positions and payoff table favor one side. Build an
analyzer that evaluates game trees under optimal play and checks payoff
matrices for pure equilibria.

## Inputs

- `tree.txt`: leaf payoffs left to right plus depth, e.g. `depth 3` then 8 ints.
- `payoffs.csv`: rows `row_move,col_move,row_payoff,col_payoff` for a 2x2 game.
- A flag selecting analysis: `minimax`, `nash`, or `both`.

## Steps

1. Parse the tree file; validate leaf count equals 2^depth.
2. Evaluate the minimax value with max to move at the root.
3. Re-evaluate with alpha-beta; record node visits for both runs.
4. Parse the payoff matrix; validate exactly four cells present.
5. Test each cell for mutual best response; list equilibria found.
6. Emit `analysis.txt` with the game value, visit counts, and equilibria.
7. Print which side the tree favors and by how many payoff points.
8. Write a two-paragraph rules note: fair or biased, with numbers cited.

## Acceptance criteria

1. Minimax and alpha-beta values agree on every accepted tree file.
2. Alpha-beta visit count is less than or equal to the full node count.
3. Analyzer lists (1,1) as the equilibrium for the dilemma matrix in Q3.
4. Malformed input (wrong leaf count, missing cell) exits with a message.
5. `analysis.txt` contains value, both visit counts, and equilibrium list.
6. Rules note cites the computed value and at least one equilibrium.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; single-threaded deterministic run.
- Depth capped at 12 to keep full enumeration feasible.
- No heuristic evaluation; leaves are exact payoffs only.
