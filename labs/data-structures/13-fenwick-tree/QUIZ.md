# Quiz: Fenwick Tree

## Multiple Choice

1. What is the size of the BIT array for n elements?
   a) n
   b) n+1
   c) 2n
   d) 4n

2. What does i & -i compute?
   a) The highest set bit
   b) The lowest set bit
   c) The number of set bits
   d) The parity of i

3. Which direction does the update operation traverse?
   a) Downward (i -= lsb(i))
   b) Upward (i += lsb(i))
   c) Both directions
   d) Random access

4. What is the time complexity of prefix sum in BIT?
   a) O(1)
   b) O(log n)
   c) O(n)
   d) O(n log n)

5. How many BITs are needed for range update + range query?
   a) 1
   b) 2
   c) 3
   d) Depends on n

## True or False

6. BIT supports range minimum queries.
7. BIT is also known as Binary Indexed Tree.
8. BIT uses 0-indexed arrays internally.
9. The space complexity of BIT is O(n).
10. BIT can be extended to 2D matrices.

## Short Answer

11. Explain the relationship between BIT and binary representation of integers.
12. How would you implement range update + range query using two BITs?
13. Compare BIT with segment trees.
14. How does inversion counting work using BIT?
15. What modifications are needed for 2D BIT?

## Answers

1. b, 2. b, 3. b, 4. b, 5. b, 6. False, 7. True, 8. False, 9. True, 10. True
