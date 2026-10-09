# Visual Guide to Fenwick Tree

## Part 1: BIT Structure for n = 8

`
Index:  1   2   3   4   5   6   7   8
Arr:    1   2   3   4   5   6   7   8
BIT:    1   3   3  10   5  11   7  36

Range coverage:
bit[1]: [1]
bit[2]: [1,2]
bit[3]: [3]
bit[4]: [1,4]
bit[5]: [5]
bit[6]: [5,6]
bit[7]: [7]
bit[8]: [1,8]
`

## Part 2: Prefix Sum Query (sum 1..7)

`
i=7 (111) → sum += bit[7]=7 → i -= 1 → i=6 (110) → sum += bit[6]=11 → i -= 2 → i=4 (100) → sum += bit[4]=10 → i -= 4 → i=0 → stop

Sum = bit[7] + bit[6] + bit[4] = 7 + 11 + 10 = 28

Visual: [1..4] + [5..6] + [7..7] = 10 + 11 + 7 = 28
         ↑bit[4]    ↑bit[6]    ↑bit[7]
`

## Part 3: Point Update (add 5 to index 3)

`
i=3 (011) → bit[3] += 5 → i += 1 → i=4 (100) → bit[4] += 5 → i += 4 → i=8 (1000) → bit[8] += 5 → i += 8 → i=16 → stop

Updated: bit[3], bit[4], bit[8]

Visual:
bit[]: [1] [3] [3] [10] [5] [11] [7] [36]
After:  [1] [3] [8] [15] [5] [11] [7] [41]
`

## Part 4: 2D BIT Structure

For a 4×4 matrix, the 2D BIT is a BIT of BITs:
- Each row i has a BIT spanning columns
- Row BITs are aggregated into a BIT over rows
- Update (x,y): update row x BIT at column y, then update row BIT at position x
- Query (1..x, 1..y): sum rows 1..x, each contributing column BIT prefix sum to y
