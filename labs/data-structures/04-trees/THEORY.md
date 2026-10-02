# Theory: Trees

## Tree Terminology

A tree is a hierarchical data structure consisting of nodes connected by edges. It is an **acyclic, connected graph**.

- **Root**: the topmost node (no parent)
- **Parent**: a node with children
- **Child**: a node directly connected below another
- **Leaf**: a node with no children
- **Sibling**: nodes sharing the same parent
- **Subtree**: a node and all its descendants
- **Height**: number of edges on the longest path from node to leaf
- **Depth**: number of edges from root to node
- **Level**: set of nodes at the same depth

## Binary Tree

Each node has at most two children: left and right.

```java
class Node<E> {
    E data;
    Node<E> left;
    Node<E> right;
}
```

## Binary Search Tree (BST)

A binary tree where for every node:
- Left subtree contains values **less than** the node
- Right subtree contains values **greater than** the node
- Both subtrees are also BSTs

## Time Complexity

| Operation | Binary Tree | BST (balanced) | BST (degenerate) |
|-----------|------------|----------------|-------------------|
| Search    | O(n)       | O(log n)       | O(n)              |
| Insert    | O(1)*      | O(log n)       | O(n)              |
| Delete    | O(1)*      | O(log n)       | O(n)              |
| Traversal | O(n)       | O(n)           | O(n)              |

\*Insert at available position; search is O(n)

## Tree Traversals

### Depth-First (DFS)

| Traversal | Order | Use Case |
|-----------|-------|----------|
| Preorder  | root → left → right | Copy tree, prefix notation |
| Inorder   | left → root → right | Sorted output (BST) |
| Postorder | left → right → root | Delete tree, postfix notation |

### Breadth-First (BFS)

- **Level-order**: process nodes level by level, left to right
- Uses a queue

## Tree Balance

- **Perfect binary tree**: all internal nodes have 2 children, all leaves at same depth
- **Complete binary tree**: all levels filled except possibly last (filled left to right)
- **Full binary tree**: every node has 0 or 2 children
- **Balanced**: height is O(log n) — AVL, Red-Black trees achieve this
- **Degenerate**: each node has at most one child (effectively a linked list)

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "3.3 Balanced Search Trees" (Sedgewick & Wayne, Algorithms 4th ed. booksite; page last modified Mar 19, 2021) — https://algs4.cs.princeton.edu/33balanced — guarantees: red-black BST height ≤ 2·lg N, and search/insert/delete/min/max/floor/ceiling/rank/select all logarithmic worst-case — pins down the lab's "balanced O(log n) vs degenerate O(n)" table with a concrete constant.
- Same source, proof idea — 1-1 correspondence between left-leaning red-black BSTs and 2-3 trees (red links bind 3-nodes); balance follows because all null links stay the same distance from the root — complements the lab's AVL/Red-Black mention with a checkable invariant (no right-leaning red links, no node with two red links, equal black-height on all root-to-null paths).
- "Lecture 6: Binary Trees, Part 1 notes" (Demaine/Ku/Solomon), MIT OCW 6.006 Spring 2020 — https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec6/ — design rule used in the lab's traversal section: BST operations run in O(h) for root height h, so the entire game is maintaining h = O(log n); BST property (left ≤ node ≤ right) makes inorder traversal yield sorted order — verify against the lab's inorder exercise.
- Same Princeton source, average-case number — average root-to-node path in a red-black BST is ~1.00·lg N — candidate benchmark claim for the lab's tree-height measurement exercise; re-measure locally before citing.
