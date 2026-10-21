# Quiz: Union-Find

## Multiple Choice

1. What is the amortized time complexity of Union-Find with both path compression and union by rank?
   a) O(log n)
   b) O(alpha(n)) [where alpha is the inverse Ackermann function]
   c) O(1)
   d) O(n)

2. What does the rank array store in union by rank?
   a) The exact height of the tree
   b) The number of elements in the set
   c) An upper bound on the tree height
   d) The depth of each node from the root

3. Which of the following is NOT a valid path compression strategy?
   a) Full path compression
   b) Path halving
   c) Path doubling
   d) Path splitting

4. What happens if you call find(x) on a root element?
   a) It returns the parent of x
   b) It returns x
   c) It returns null
   d) It throws an exception

5. In Kruskal's algorithm, DSU is used to:
   a) Sort the edges by weight
   b) Check if adding an edge creates a cycle
   c) Find the shortest path between vertices
   d) Store the adjacency matrix

## True or False

6. Path compression makes every Find operation modify the parent array.
7. Without any optimizations, DSU can have O(n) Find operations.
8. Union by rank guarantees that tree height never exceeds log n.
9. DSU can efficiently split a set back into two sets.
10. The inverse Ackermann function grows faster than log n.

## Short Answer

11. Explain why union by rank with path compression achieves O(alpha(n)) amortized time.
12. Describe a real-world application of DSU outside of graph theory.
13. Compare DSU with using BFS/DFS for dynamic connectivity.
14. How does union by size differ from union by rank? Which is better?
15. What modifications are needed to make DSU thread-safe?

## Coding Questions

16. Implement find() with path compression.
17. Implement union() with union by rank.
18. Use DSU to detect a cycle in an undirected graph.
19. Write a function that takes a list of edges and returns the connected components.
20. Implement Kruskal's algorithm using your DSU implementation.

## Answers

1. b, 2. c, 3. c, 4. b, 5. b, 6. True, 7. True, 8. True, 9. False, 10. False
