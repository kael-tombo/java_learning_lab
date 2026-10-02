# Flashcards — Breadth-First Search (BFS)

- Q: BFS time complexity (graph)? → A: O(V + E)
- Q: BFS space complexity? → A: O(V) worst case
- Q: BFS shortest path guarantee? → A: Explores all distance-k nodes before distance-(k+1) nodes
- Q: BFS frontier data structure? → A: Queue (FIFO)
- Q: Bidirectional BFS frontier expansion rule? → A: Always expand the smaller frontier
- Q: BFS vs DFS space on balanced tree depth d? → A: BFS O(b^d), DFS O(d)
- Q: When BFS over Dijkstra? → A: Unweighted graphs / equal edge weights
- Q: Why remove visited words in Word Ladder? → A: Prevents revisiting, ensures O(1) per word processing
- Q: Bidirectional BFS complexity? → A: O(b^(d/2)) vs standard O(b^d)
- Q: Handling disconnected components in BFS? → A: Run BFS from each unvisited vertex
- Q: BFS tree level property? → A: All nodes at level k have shortest distance k from source
- Q: When does BFS queue reach maximum size? → A: Star graph (all neighbors of source enqueued at once)
- Q: BFS vs DFS for shortest path? → A: BFS finds shortest in unweighted; DFS does not guarantee
- Q: What is a "level" in BFS? → A: Set of nodes at same distance from source
- Q: How to reconstruct BFS path? → A: Store parent pointers when enqueuing neighbors