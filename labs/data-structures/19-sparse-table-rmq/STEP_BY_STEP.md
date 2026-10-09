# Step-by-Step: Building a Sparse Table

1. Allocate 2D array of size n × (log2(n) + 1)
2. Fill level 0 with original array values
3. For j = 1 to log(n):
   For i = 0 to n - 2^j:
     st[i][j] = combine(st[i][j-1], st[i + 2^(j-1)][j-1])
4. Precompute log table
5. Implement query using log table
6. Test with random data against brute force
