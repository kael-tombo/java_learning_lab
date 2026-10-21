# Interview Questions: Advanced String Algorithms

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 1044 Longest Duplicate Substring | Hard | Google, Amazon | Suffix array / rolling hash |
| LC 1923 Longest Common Subpath | Hard | Google | Suffix array / rolling hash |
| LC 1960 Maximum Product of the Length of Two Palindromic Substrings | Hard | Google | Manacher's algorithm |

## NeetCode Reference
Not covered in NeetCode 150. These are highly advanced string algorithm problems for Google hard interviews.

## Company-Specific Questions
### Google
- Implement Manacher's algorithm for O(n) longest palindromic substring
- Design an algorithm for substring search in O(|S|) using suffix automaton
- How would you implement the Burrows-Wheeler Transform for compression?
- Find the longest common substring of two strings in O(n+m) using suffix automaton
- How does Google's PageRank use suffix arrays for duplicate content detection?

### Microsoft
- How does Bing process large-scale text for search indexing?
- Design a plagiarism detection system using advanced string matching
- Implement Z-algorithm for pattern matching
- How does Windows file search handle substring matching?

### Meta
- Content deduplication using advanced string algorithms
- How would you detect near-duplicate posts at Facebook scale?
- Longest common subpath for detecting coordinated sharing patterns
- Manacher's algorithm for text formatting and rendering

### Amazon
- Product description deduplication using longest common substring
- How would you implement document fingerprinting at scale?
- BWT for product catalog compression in DynamoDB
- Suffix array for efficient search in product databases

### Apple
- On-device search (Spotlight) implementation using suffix structures
- Memory-efficient string algorithms for mobile
- How would you implement a substring search in Pages/Numbers?
- BWT-based compression for iCloud storage optimization

### Oracle
- How does Oracle Text implement full-text search?
- Design a string indexing structure for large VARCHAR2 columns
- Explain Oracle's CONTAINS and CATSEARCH implementation
- How does Oracle handle pattern matching in JSON documents?

## Real Production Scenarios
- Scenario 1: Document similarity detection - using suffix automaton to find the longest common substring between submitted documents and a database of 10M copyrighted works at a plagiarism detection service
- Scenario 2: Genome compression - applying BWT + move-to-front + Huffman coding pipeline (bzip2) to compress 3GB human genome FASTA files to under 800MB for efficient storage and transfer
- Scenario 3: Real-time search - debugging a Z-algorithm implementation that produces incorrect prefix matches when the concatenated string contains delimiter characters that also appear in the input text

## Interview Tips
- Manacher's O(n) algorithm uses mirror property of palindromes and maintains center/right boundary
- Z-algorithm: Z-array gives longest prefix match starting at each position; used for pattern matching via concatenation
- Suffix automaton: O(n) size, accepts all substrings; can compute longest common substring in O(n+m)
- Common edge cases: empty strings, single character strings, strings with all identical characters, very long strings

## Java-Specific Considerations
- Manacher's: transform string with separators (e.g., "#a#b#c#") for uniform odd/even handling
- Z-algorithm: `int[] z = new int[n]`; main loop maintains `[l, r]` interval for mirror computation
- Suffix automaton: `class State { int len, link; Map<Character, Integer> next; }`; `ArrayList<State>`
- BWT: compute suffix array, then `bwt[i] = s.charAt((sa[i] + n - 1) % n)`
- Pitfall: O(n^2) naive palindrome expansion instead of Manacher that fails for long strings
- Pitfall: not using `char[]` for performance in tight loops (String.charAt() overhead)
- Pitfall: recursion depth in suffix automaton traversal; use iterative approach for long strings
