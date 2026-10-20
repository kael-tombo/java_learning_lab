# Architecture

Persistent data structures are foundational for:
- Functional programming languages
- Event sourcing systems
- Version control systems
- Undo/redo implementations
- Concurrent data sharing

## Integration

`
Application
  → Service (pure functions)
    → PersistentStore
      → PersistentList (audit log)
      → PersistentMap (configuration)
      → PersistentTree (index)
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Exercises

## Beginner
1. Implement immutable Pair class
2. Implement persistent singly linked list
3. Verify structural sharing

## Intermediate
4. Implement persistent stack
5. Implement persistent binary search tree
6. Add contains/findMin to persistent BST
7. Implement functional map using persistent BST

## Advanced
8. Implement persistent vector (RRB tree)
9. Implement HAMT for persistent hash map
10. Implement transient for batch operations
11. Benchmark persistent vs mutable for different workloads
12. Implement persistent queue using two lists
