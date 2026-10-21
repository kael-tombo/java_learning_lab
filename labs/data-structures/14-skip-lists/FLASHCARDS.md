# Flashcards: Skip Lists

## Front: What is a skip list?
Back: A probabilistic data structure with multiple linked list levels for O(log n) expected search/insert/delete.

## Front: How is node level determined?
Back: Start at 1, while random() < 0.5 and level < MAX_LEVEL, increment. Geometric distribution.

## Front: What is MAX_LEVEL?
Back: Maximum allowed level for any node. Typically ceil(log2(n)) or a fixed constant like 32.

## Front: How does search work?
Back: Start at top level, go right until next key >= target, drop one level, repeat. At level 0, the next node is the target or not found.

## Front: What is the update array?
Back: During insert/delete, stores the node at each level whose forward pointer needs updating.
