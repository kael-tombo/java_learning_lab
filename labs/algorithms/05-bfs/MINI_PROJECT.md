# MINI_PROJECT — BFS: Frontier Visualizer + Shootout
> Implement + benchmark + visualize. ~3 hours.

## Goal
Animate BFS frontiers on a grid maze, reconstruct shortest path, and benchmark BFS vs
DFS path length + bidirectional BFS speedup.

## Build Steps
1. `Maze.java`: grid with walls; BFS with parent[] + level lists.
2. Visualize: ASCII per level (`S` source, `·` frontier, `#` wall, `*` path).
3. Path: back-chain prev[] from T; assert length == dist[T].
4. Benchmark: open 100×100 (10⁴ nodes) BFS vs DFS path length + ms.
5. Bidirectional: implement meet-in-middle; report speedup on long corridor.

## Benchmark Table (fill)
| maze | BFS len/ms | DFS len/ms | bi-BFS ms | speedup |
|------|------------|------------|-----------|---------|
| open 100² | / | / | | |
| corridor | / | / | | ≥3× |

## Visualize
```
S··#....
***#..T  (* = reconstructed path)
```

## Acceptance
- [ ] Level animation (≥5 frames) + path overlay.
- [ ] BFS length ≤ DFS length (assert) on all mazes.
- [ ] Disconnected target stays −1 (test).

## Extensions
- 0-1 BFS on weighted grid (preview Dijkstra).
