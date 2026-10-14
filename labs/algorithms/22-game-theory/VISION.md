# Vision: Game Theory

## Direction

This lab covers finite deterministic games: minimax for zero-sum
perfect-information trees, alpha-beta pruning for cutting dead subtrees, and
the Nash equilibrium concept for simultaneous-move games. The practical skill
is computing exact game values on small trees and stating what pruning does
and does not change about the result.

## What to learn

- Minimax recursion: alternating max and min levels down to leaf payoffs.
- Alpha-beta bounds: identical value to minimax with fewer node visits.
- Ordering effect: best-first move order drives pruning toward its bound.
- Nash equilibrium: mutual best response; check by unilateral deviation.
- Equilibrium versus optimum: equilibrium payoffs can trail joint optima.

## Non-coverage

- This lab does not cover mixed strategies or equilibrium existence proofs.
- It does not cover Monte Carlo tree search or heuristic evaluation design.
- It does not cover stochastic games, auctions, or mechanism design.
- It does not cover retrograde analysis or endgame tablebase construction.
- All trees here are tiny and fully enumerated; no real game engine is built.

## How to use this lab

Implement minimax from MOCK_INTERVIEW Q1, add the alpha-beta counters from
Q2, then run the Nash best-response check from Q3 on two payoff matrices of
your own. Finish with MINI_PROJECT's tic-tac-toe solver.

## Pitfalls

- Assuming alpha-beta changes the game value; it only skips visits.
- Ordering moves worst-first and wondering why nothing prunes.
- Calling a jointly good cell an equilibrium without checking deviations.

## Done when

- You can hand-evaluate a depth-3 tree and state the minimax value.
- You can explain why alpha-beta returns the same value with fewer visits.
- You can test any 2x2 cell for equilibrium by checking deviations.
- You can state the O(b^d) bound and the ordering caveat from memory.
