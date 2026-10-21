# Visual Guide to Persistent Structures

## Persistent List Add

`
list1 = empty() → add(1):
[1] → null

list2 = list1.add(2):
[2] → [1] → null
       →‘list1.head (shared!)

list3 = list2.add(3):
[3] → [2] → [1] → null
       →‘list2 (shared!)
              →‘list1 (shared!)
`

## Persistent BST Insert

Inserting 3 then 7 into tree initially containing 5:
`
Version 1:     [5]
               /  \
            null  null

Version 2:     [5]  (new root)
               /  \
            [3]   null  (new left, shared right)
            /   \
         null  null

Version 3:     [5]  (new root)
               /  \
            [3]   [7]  (shared left, new right)
            / \    / \
         null n n n
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: PersistentList.java

The persistent list uses a recursive structure where each node contains a value and a reference to the tail (rest of the list). The empty list is a sentinel.

## Key Design Decisions

1. Final fields: once created, the list never changes
2. Structural sharing: add() creates one new node pointing to this
3. Empty sentinel: singleton pattern for empty list
4. Immutable: no setters, no mutable state
5. Thread-safe: no synchronization needed (no shared mutable state)
