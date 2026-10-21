# How Sparse Tables Work

## Preprocessing

Given array arr of length n:
`
k = floor(log2(n))
st[i][0] = arr[i] for i = 0..n-1
st[i][j] = min(st[i][j-1], st[i + 2^(j-1)][j-1])
for j = 1..k, i = 0..n-2^j
`

## Query Processing

For range [l, r]:
`
length = r - l + 1
k = floor(log2(length))
return min(st[l][k], st[r - 2^k + 1][k])
`

## Example

arr = [5, 2, 8, 1, 9, 3, 7, 4]

st[i][0] = [5, 2, 8, 1, 9, 3, 7, 4]
st[i][1] = [2, 2, 1, 1, 3, 3, 4, -]
st[i][2] = [1, 1, 1, 1, 3, -, -, -]
st[i][3] = [1, -, -, -, -, -, -, -]

Query min(2, 6):
length = 5, k = 2
min(st[2][2], st[6-4+1=3][2]) = min(1, 1) = 1
