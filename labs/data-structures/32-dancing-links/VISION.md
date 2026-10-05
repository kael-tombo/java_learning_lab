# VISION — Dancing Links (32)

Vision: solve exact-cover by deleting/restoring nodes in O(1) pointer surgery.

## Mental models
- Model rows as linked lists over columns; each column header counts its cells.
- Algorithm X: pick smallest column, try its rows, cover columns, recurse, then uncover.
- Covering = unlink column + for each row unlink its cells; uncover is the exact inverse (LIFO restore).
- The O(1) cover/uncover (four pointer writes) is the trick — iterators make Sudoku/n-queens/polyominoes feasible.
- Search tree is pruned by MRV (minimum remaining values) column choice.

## Decision table
| Need | Use |
|---|---|
| Exact cover / Sudoku | Dancing links (Algorithm X) |
| Generic backtracking | Recursive scan with indices |
| Satisfiability | SAT solvers (CDCL) |
| Matching in general graphs | Hopcroft-Karp etc. |
| Latin squares, tiling | Dancing links with MRV |

## Career path
- Shows up in: puzzle solvers, linker/loader research, constraint tooling interviews.
- Interview angle: invariants of the cover/uncover symmetry; why MRV pruning matters.
- Pairs with Knuth's TAOCP coverage and exact-cover formulations in practice.

## Done when
- [ ] Hand-trace cover/uncover pointer writes for one row
- [ ] Solve 4x4 Sudoku via Algorithm X
- [ ] Mini + real-world projects shipped
