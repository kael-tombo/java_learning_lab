# Visual Guide to LRU Cache

Capacity = 3

Initial: empty

1. put(1, A): [1:A] (head=tail=1:A)
2. put(2, B): [2:B] →” [1:A]
3. put(3, C): [3:C] →” [2:B] →” [1:A]
4. get(2):    [2:B] →” [3:C] →” [1:A]  (2 moved to head)
5. put(4, D): [4:D] →” [2:B] →” [3:C]  (1:A evicted - LRU)
6. get(1):    null (evicted)
7. put(2, X): [2:X] →” [4:D] →” [3:C]  (2 updated, moved to head)
