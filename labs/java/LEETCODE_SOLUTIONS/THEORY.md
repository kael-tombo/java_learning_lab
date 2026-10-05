# THEORY — LeetCode Solutions Patterns

## Overview

This directory contains curated LeetCode solutions organized by algorithmic patterns. Each solution demonstrates optimal approaches with time/space complexity analysis.

---

## Core Patterns

### 1. Two Pointers

```java
// Opposite ends → center
int left = 0, right = arr.length - 1;
while (left < right) {
    if (arr[left] + arr[right] == target) return new int[]{left, right};
    else if (arr[left] + arr[right] < target) left++;
    else right--;
}

// Same direction (slow/fast)
int slow = 0, fast = 0;
while (fast < n) {
    if (condition) slow++;
    fast++;
}
```

**Use when**: Sorted arrays, palindrome, pairing, cycle detection
**Complexity**: O(n) time, O(1) space

---

### 2. Sliding Window

```java
// Fixed size
for (int i = k; i < n; i++) {
    window += arr[i] - arr[i - k];
    max = Math.max(max, window);
}

// Variable size
int left = 0;
for (int right = 0; right < n; right++) {
    window.add(arr[right]);
    while (!valid(window)) window.remove(arr[left++]);
    max = Math.max(max, right - left + 1);
}
```

**Use when**: Subarray/substring with constraints
**Complexity**: O(n) time, O(k) space

---

### 3. Prefix Sum

```java
int[] prefix = new int[n + 1];
for (int i = 0; i < n; i++) {
    prefix[i + 1] = prefix[i] + arr[i];
}

// Range sum [l, r]
int sum = prefix[r + 1] - prefix[l];
```

**Use when**: Range sum queries, subarray sum equals K
**Complexity**: O(n) preprocessing, O(1) query

---

### 4. Binary Search

```java
// Standard
int left = 0, right = n - 1;
while (left <= right) {
    int mid = left + (right - left) / 2;
    if (arr[mid] == target) return mid;
    else if (arr[mid] < target) left = mid + 1;
    else right = mid - 1;
}

// Search space (answer is in range)
int left = 1, right = maxPossible;
while (left < right) {
    int mid = left + (right - left) / 2;
    if (can(mid)) right = mid;
    else left = mid + 1;
}
return left;
```

**Use when**: Sorted data, search answer space
**Complexity**: O(log n) time

---

### 5. Depth-First Search (DFS)

```java
// Recursive
void dfs(int node) {
    visited[node] = true;
    for (int nei : graph[node]) {
        if (!visited[nei]) dfs(nei);
    }
}

// Iterative
Deque<Integer> stack = new ArrayDeque<>();
stack.push(start);
while (!stack.isEmpty()) {
    int node = stack.pop();
    if (!visited[node]) {
        visited[node] = true;
        for (int nei : graph[node]) stack.push(nei);
    }
}
```

**Use when**: Tree traversal, graph connectivity, backtracking
**Complexity**: O(V + E) time, O(V) space

---

### 6. Breadth-First Search (BFS)

```java
Queue<Integer> queue = new ArrayDeque<>();
queue.offer(start);
visited[start] = true;
while (!queue.isEmpty()) {
    int node = queue.poll();
    for (int nei : graph[node]) {
        if (!visited[nei]) {
            visited[nei] = true;
            queue.offer(nei);
        }
    }
}

// Level-order (tree)
Queue<TreeNode> q = new ArrayDeque<>();
q.offer(root);
while (!q.isEmpty()) {
    int size = q.size();
    for (int i = 0; i < size; i++) {
        TreeNode node = q.poll();
        // process
        if (node.left != null) q.offer(node.left);
        if (node.right != null) q.offer(node.right);
    }
}
```

**Use when**: Shortest path (unweighted), level-order, topological sort
**Complexity**: O(V + E) time, O(V) space

---

### 7. Dynamic Programming

#### 1D DP

```java
// Fibonacci
dp[i] = dp[i-1] + dp[i-2];

// House Robber
dp[i] = Math.max(dp[i-1], dp[i-2] + nums[i]);

// Coin Change
dp[0] = 0;
for (int i = 1; i <= amount; i++) {
    for (int coin : coins) {
        if (coin <= i) dp[i] = Math.min(dp[i], dp[i-coin] + 1);
    }
}
```

#### 2D DP

```java
// LCS / Edit Distance
for (int i = 1; i <= m; i++) {
    for (int j = 1; j <= n; j++) {
        if (s1[i-1] == s2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;
        else dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
    }
}
```

**Use when**: Optimal substructure, overlapping subproblems
**Complexity**: O(n) or O(n²) time/space

---

### 8. Union Find (Disjoint Set)

```java
class UnionFind {
    int[] parent, rank;
    
    UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
    }
    
    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }
    
    boolean union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rank[px] < rank[py]) parent[px] = py;
        else if (rank[px] > rank[py]) parent[py] = px;
        else { parent[py] = px; rank[px]++; }
        return true;
    }
}
```

**Use when**: Connected components, cycle detection, Kruskal's MST
**Complexity**: O(α(n)) amortized

---

### 9. Heap / Priority Queue

```java
// Min heap
PriorityQueue<Integer> minHeap = new PriorityQueue<>();

// Max heap
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());

// Custom comparator
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);

// K largest elements
for (int num : nums) {
    minHeap.offer(num);
    if (minHeap.size() > k) minHeap.poll();
}
```

**Use when**: Top K, median, scheduling, Dijkstra
**Complexity**: O(log n) per operation

---

### 10. Monotonic Stack

```java
// Next greater element
Deque<Integer> stack = new ArrayDeque<>();
for (int i = n - 1; i >= 0; i--) {
    while (!stack.isEmpty() && arr[stack.peek()] <= arr[i]) {
        stack.pop();
    }
    nextGreater[i] = stack.isEmpty() ? -1 : arr[stack.peek()];
    stack.push(i);
}

// Largest rectangle in histogram
Deque<Integer> stack = new ArrayDeque<>();
for (int i = 0; i <= n; i++) {
    int h = (i == n) ? 0 : heights[i];
    while (!stack.isEmpty() && heights[stack.peek()] > h) {
        int height = heights[stack.pop()];
        int width = stack.isEmpty() ? i : i - stack.peek() - 1;
        max = Math.max(max, height * width);
    }
    stack.push(i);
}
```

**Use when**: Next greater/smaller, histogram, trapping rain water
**Complexity**: O(n) time, O(n) space

---

### 11. Bit Manipulation

```java
// Check bit
(x >> i) & 1

// Set bit
x | (1 << i)

// Clear bit
x & ~(1 << i)

// Toggle bit
x ^ (1 << i)

// Lowest set bit
x & -x

// Count bits
Integer.bitCount(x)

// Power of two
(x & (x - 1)) == 0
```

**Use when**: Subset generation, XOR problems, bit counting
**Complexity**: O(1) per operation

---

### 12. Backtracking

```java
void backtrack(int index, List<Integer> current) {
    if (index == n) {
        result.add(new ArrayList<>(current));
        return;
    }
    
    // Include
    current.add(nums[index]);
    backtrack(index + 1, current);
    current.remove(current.size() - 1);
    
    // Exclude
    backtrack(index + 1, current);
}

// With pruning
if (currentSum > target) return;  // Prune
```

**Use when**: Permutations, combinations, subsets, N-Queens
**Complexity**: Exponential (pruning helps)

---

### 13. Trie (Prefix Tree)

```java
class TrieNode {
    TrieNode[] children = new TrieNode[26];
    boolean isEnd = false;
}

class Trie {
    TrieNode root = new TrieNode();
    
    void insert(String word) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            int i = c - 'a';
            if (node.children[i] == null) node.children[i] = new TrieNode();
            node = node.children[i];
        }
        node.isEnd = true;
    }
    
    boolean search(String word) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            int i = c - 'a';
            if (node.children[i] == null) return false;
            node = node.children[i];
        }
        return node.isEnd;
    }
}
```

**Use when**: Prefix search, autocomplete, word dictionary
**Complexity**: O(L) per operation (L = word length)

---

### 14. Segment Tree

```java
class SegmentTree {
    int[] tree;
    int n;
    
    SegmentTree(int[] arr) {
        n = arr.length;
        tree = new int[4 * n];
        build(arr, 1, 0, n - 1);
    }
    
    void build(int[] arr, int node, int l, int r) {
        if (l == r) { tree[node] = arr[l]; return; }
        int mid = (l + r) / 2;
        build(arr, 2*node, l, mid);
        build(arr, 2*node+1, mid+1, r);
        tree[node] = tree[2*node] + tree[2*node+1];
    }
    
    int query(int node, int l, int r, int ql, int qr) {
        if (ql > r || qr < l) return 0;
        if (ql <= l && r <= qr) return tree[node];
        int mid = (l + r) / 2;
        return query(2*node, l, mid, ql, qr) + query(2*node+1, mid+1, r, ql, qr);
    }
}
```

**Use when**: Range queries with updates
**Complexity**: O(log n) query/update

---

### 15. Topological Sort

```java
// Kahn's algorithm (BFS)
int[] indegree = new int[n];
for (int u = 0; u < n; u++)
    for (int v : graph[u]) indegree[v]++;

Queue<Integer> q = new ArrayDeque<>();
for (int i = 0; i < n; i++) if (indegree[i] == 0) q.offer(i);

List<Integer> order = new ArrayList<>();
while (!q.isEmpty()) {
    int u = q.poll();
    order.add(u);
    for (int v : graph[u]) {
        if (--indegree[v] == 0) q.offer(v);
    }
}
if (order.size() != n) throw new IllegalStateException("Cycle detected");
```

**Use when**: Task scheduling, course prerequisites, build order
**Complexity**: O(V + E) time, O(V) space

---

## Problem Categories

| Category | Key Patterns |
|----------|--------------|
| Array/String | Two Pointers, Sliding Window, Prefix Sum |
| Linked List | Two Pointers, Reverse, Merge |
| Tree | DFS, BFS, Recursion |
| Graph | BFS, DFS, Union Find, Topological Sort, Dijkstra |
| DP | 1D/2D DP, Knapsack, LCS, Edit Distance |
| Heap | Top K, Median, Scheduling |
| Stack/Queue | Monotonic Stack, Parentheses, Histogram |
| Bit | XOR, Subsets, Bit Counting |
| Trie | Prefix, Word Search |
| Math | GCD, Modular Arithmetic, Combinatorics |

---

## Complexity Quick Reference

| Algorithm | Time | Space |
|-----------|------|-------|
| Sort | O(n log n) | O(1) or O(n) |
| Binary Search | O(log n) | O(1) |
| BFS/DFS | O(V + E) | O(V) |
| Dijkstra | O(E log V) | O(V) |
| Union Find | O(α(n)) | O(n) |
| Heap ops | O(log n) | O(n) |
| Segment Tree | O(log n) | O(n) |

---

## Java-Specific Tips

```java
// Fast I/O
FastScanner fs = new FastScanner(System.in);
int n = fs.nextInt();
String s = fs.next();

// Avoid boxing in hot loops
int[] arr = new int[n];  // Not Integer[]

// Use ArrayDeque over Stack/LinkedList
Deque<Integer> stack = new ArrayDeque<>();
Queue<Integer> queue = new ArrayDeque<>();

// StringBuilder for concatenation
StringBuilder sb = new StringBuilder();
for (...) sb.append(x);

// Arrays utility
Arrays.sort(arr);
Arrays.fill(arr, val);
Arrays.copyOf(arr, newLen);
Arrays.binarySearch(arr, key);
```

---

## Solution Structure

Each solution includes:
1. **Problem statement** (summary)
2. **Approach explanation** (pattern used)
3. **Algorithm steps**
4. **Correctness proof sketch**
5. **Complexity analysis**
6. **Clean Java code** with comments
7. **Test cases** (edge cases covered)

---

## Directory Structure

```
leetcode-solutions/
├── arrays/
├── strings/
├── linked-lists/
├── trees/
├── graphs/
├── dynamic-programming/
├── heap/
├── stack-queue/
├── bit-manipulation/
├── backtracking/
├── trie/
├── segment-tree/
├── math/
└── design/
```

Each problem: `ProblemName.java` with `Solution` class and `main` for testing.