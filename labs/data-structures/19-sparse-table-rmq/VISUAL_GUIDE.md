# Visual Guide to Sparse Table Construction

## Array: [5, 2, 8, 1, 9, 3, 7, 4]

### Level 0 (length 1):
[5] [2] [8] [1] [9] [3] [7] [4]

### Level 1 (length 2):
[2] [2] [1] [1] [3] [3] [4]  → min of each pair

### Level 2 (length 4):
[1] [1] [1] [1] [3]  → min of each pair of level-1 results

### Level 3 (length 8):
[1]  → min of the two level-2 results

### Query min(2, 6):
length = 5, k = log2(5) = 2
Use level 2: st[2][2] = range [2,5] = min(8,1,9,3) = 1
            st[3][2] = range [3,6] = min(1,9,3,7) = 1
Result: min(1, 1) = 1
