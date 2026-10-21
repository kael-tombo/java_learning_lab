# How Persistent Data Structures Work

## Persistent Singly Linked List

`
list1 = [] → add(1) → [1]
list2 = list1.add(2) → [2] → [1]  (shares [1])
list3 = list2.add(3) → [3] → [2] → [1] (shares [2]→[1])

Structural sharing: list1.tail == list2.tail.tail
`

## Persistent Binary Search Tree

`
tree1 = empty → insert(5)
tree2 = tree1.insert(3)
tree3 = tree2.insert(7)

Each insert copies the path from root to insertion point.
Unchanged subtrees are shared across versions.
`

## Path Copying

When inserting into a persistent BST:
1. Create new root node
2. If going left, point to new left subtree (created recursively)
3. Point right pointer to existing right subtree (shared)
4. Return new root
