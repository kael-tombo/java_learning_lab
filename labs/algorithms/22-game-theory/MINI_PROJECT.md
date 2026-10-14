# Mini-Project: Tic-Tac-Toe Minimax Solver

## Goal

Write a minimax solver for tic-tac-toe that returns the game value of any
legal board for the player to move, with alpha-beta counting node visits.

## Inputs

- Hard-coded test boards below; X is the max player, O the min player.
- Board A (empty), Board B: X to move and win in one, Board C: drawn full.

## Steps

1. Represent the board as a 9-char array with X, O, and blank cells.
2. Write win detection for rows, columns, and both diagonals.
3. Write move generation listing every blank cell index.
4. Implement minimax returning +1 (X wins), -1 (O wins), 0 (draw).
5. Wrap with alpha-beta and a shared visit counter; compare values.
6. Evaluate boards A, B, and C; print value plus visits for each.
7. Print the winning move index found on board B.

## Acceptance criteria

1. Empty board evaluates to 0 (draw under optimal play).
2. Board B evaluates to +1 and the printed move wins immediately.
3. Full drawn board evaluates to 0 with zero moves generated.
4. Alpha-beta values match plain minimax on all three boards.
5. Visit counts printed for both methods on each board.
6. Win detection covers all 8 lines, verified by unit-style asserts.
7. All output uses plain ASCII characters.

## Grading note

- Board values 0, +1, 0 with the winning move index all required.
- Alpha-beta must agree with minimax on every board tested.
- Visit counts printed for both methods on each board.

## Stretch

- Add move ordering (center first) and report the visit-count change.
- Print the principal variation: the move sequence of optimal play.
