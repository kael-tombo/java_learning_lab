# Challenge: 2D Range Queries

Implement a 2D BIT supporting:
1. Point update at (x, y) with value v
2. Sum query over rectangle [(x1,y1), (x2,y2)]
3. Handle coordinates up to 10^6 (coordinate compression needed)

## Complexity
- Update: O(log^2 n)
- Query: O(log^2 n)
