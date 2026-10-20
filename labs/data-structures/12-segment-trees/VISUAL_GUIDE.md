# Visual Guide to Segment Trees

## Part 1: Building the Tree

For array [1, 3, 5, 7, 9, 11]:

`
          [0-5]
        /        \
    [0-2]        [3-5]
    /    \       /    \
 [0-1]   [2]  [3-4]   [5]
 /   \    |    /   \    |
[0] [1]  [2] [3] [4]  [5]
 1   3    5   7   9   11
`

## Part 2: Range Query [2, 5]

`
          [0-5] â”€â”€â”€ partial
        /        \
    [0-2] â”€â”€â•®  [3-5] â”€â”€ full âœ“ return 27
    /    \   â”‚
 [0-1] â•­â”„â”„ [2] â”„â”„ full âœ“ return 5
 /   \  â•°â”„â”„ range [2,5]
[0] [1]
`

Result = 5 + 27 = 32

## Part 3: Point Update at index 2 → 6

`
          36 → 37
         /       \
       9→10     27
      /    \    / \
     4    5→6 16  11
    / \    |   / \  |
   1  3    6  7  9 11
`

## Part 4: Lazy Propagation

Adding 2 to range [1, 4]:

`
         36 â”€â”€ lazy[0,5] = 0
        /        \
    9→[0,2]=9  27→[3,5]=27
    /         \
 [0,1]       [2]=5→[2]=7 (lazy)
 /     \     
[0]=1  [1]=3→[1]=5 (lazy)
`

Lazy values are pushed down only when queries need to traverse through the node.
