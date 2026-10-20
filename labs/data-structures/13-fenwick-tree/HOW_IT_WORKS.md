# How Fenwick Tree Works

## Core Mechanism

The Fenwick tree works by distributing prefix sums across an array in a specific pattern based on the binary representation of indices.

## The BIT Array

For an array arr[1..n] (1-indexed), BIT stores an array bit[1..n] where:
`
bit[i] = sum of arr[i - lsb(i) + 1 ... i]
`

This means:
- bit[1] = arr[1] (lsb(1)=1, range[1,1])
- bit[2] = arr[1] + arr[2] (lsb(2)=2, range[1,2])
- bit[3] = arr[3] (lsb(3)=1, range[3,3])
- bit[4] = arr[1] + arr[2] + arr[3] + arr[4] (lsb(4)=4, range[1,4])

## Update Operation

To add val to arr[i]:

`
function add(i, val):
    while i <= n:
        bit[i] += val
        i += i & -i
`

Traversal for add(3, 5) in BIT of size 8:
- Start at i = 3 (011)
- bit[3] += 5, i += 1 → i = 4 (100)
- bit[4] += 5, i += 4 → i = 8 (1000)
- bit[8] += 5, i += 8 → i = 16 (stop, > 8)

Updated indices: 3, 4, 8.

## Prefix Sum Query

To get sum of arr[1..i]:

`
function prefixSum(i):
    sum = 0
    while i > 0:
        sum += bit[i]
        i -= i & -i
    return sum
`

Traversal for prefixSum(7):
- Start at i = 7 (111)
- sum += bit[7], i -= 1 → i = 6 (110)
- sum += bit[6], i -= 2 → i = 4 (100)
- sum += bit[4], i -= 4 → i = 0 (stop)
- Result = bit[7] + bit[6] + bit[4]

## Range Sum Query

To get sum of arr[l..r]:
`
return prefixSum(r) - prefixSum(l - 1)
`

## Building BIT

Initialize bit array to zeros, then for each index i:
`
bit[i] = 0
for i = 1 to n:
    add(i, arr[i])
`
Time: O(n log n)

Better: O(n) construction:
`
bit[i] = arr[i]
for i = 1 to n:
    j = i + lsb(i)
    if j <= n:
        bit[j] += bit[i]
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Internals of Fenwick Tree

## Memory Layout

BIT uses a single array of size n+1 (1-indexed):
`
bit[0] = 0 (unused)
bit[1..n] = partial sums
`

Total memory: (n+1) * 4 bytes for int, or (n+1) * 8 bytes for long.

## Understanding the LSB Function

The LSB function (also called lowbit or isolate lowest set bit) is:
`java
int lsb(int i) {
    return i & -i;
}
`

In two's complement, -i = ~i + 1. So i & -i isolates the lowest set bit.

Examples:
- 6 & -6 = 2 (110 & 010) 
- 8 & -8 = 8 (1000 & 1000)
- 7 & -7 = 1 (111 & 001)

## BIT Index Navigation

### Update Path (Upward)
From index i, the next index is i + lsb(i):
`
1 → 2 → 4 → 8 → 16 → ...
2 → 4 → 8 → 16 → ...
3 → 4 → 8 → 16 → ...
5 → 6 → 8 → 16 → ...
6 → 8 → 16 → ...
7 → 8 → 16 → ...
`

### Query Path (Downward)
From index i, the next index is i - lsb(i):
`
15 → 14 → 12 → 8 → 0
14 → 12 → 8 → 0
13 → 12 → 8 → 0
12 → 8 → 0
11 → 10 → 8 → 0
10 → 8 → 0
9 → 8 → 0
`

## Internal State Example

BIT for arr[1..8] = [1, 2, 3, 4, 5, 6, 7, 8]:

`
bit[1] = arr[1] = 1
bit[2] = arr[1] + arr[2] = 3
bit[3] = arr[3] = 3
bit[4] = arr[1..4] = 10
bit[5] = arr[5] = 5
bit[6] = arr[5] + arr[6] = 11
bit[7] = arr[7] = 7
bit[8] = arr[1..8] = 36
`

## Thread Safety

Standard BIT is not thread-safe. For concurrent access:
- Use synchronized methods
- Use AtomicIntegerArray for lock-free updates
- Use read-write locks for query-heavy workloads

## Internal Consistency

BIT maintains the invariant that for any valid update sequence:
`
prefixSum(i) = sum of arr[1..i]
`

This invariant holds because:
1. add(i, val) updates all positions whose ranges include i
2. prefixSum(i) collects exactly the positions that cover [1..i]
3. The sets of positions are exactly complementary due to binary index properties
