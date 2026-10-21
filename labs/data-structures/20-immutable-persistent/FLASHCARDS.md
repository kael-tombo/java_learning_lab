## Front: What is an immutable data structure?
Back: A structure that cannot be modified after creation. Operations return new structures.

## Front: What is path copying?
Back: When modifying a persistent structure, only the nodes on the path from root to modification are copied.

## Front: What is structural sharing?
Back: Persistent structures share unchanged nodes between versions, making operations memory-efficient.

## Front: What are transients?
Back: Mutable versions of persistent structures for efficient batch operations.

## Front: How does a persistent BST insert work?
Back: Create new root, copy path to insertion point, share unchanged subtrees.
