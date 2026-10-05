# Discrete Mathematics Code Deep Dive (Python)

## 1. Set Operations
```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

print(A | B)   # Union: {1, 2, 3, 4, 5, 6}
print(A & B)   # Intersection: {3, 4}
print(A - B)   # Difference: {1, 2}
print(A ^ B)   # Symmetric difference: {1, 2, 5, 6}

# Power set
from itertools import combinations
def power_set(s):
    return [set(c) for r in range(len(s)+1) for c in combinations(s, r)]
```

## 2. Permutations and Combinations
```python
from itertools import permutations, combinations
from math import factorial, comb

print(list(permutations([1,2,3])))     # All orderings
print(list(combinations([1,2,3,4], 2))) # Unordered pairs
print(comb(10, 3))  # 120
print(factorial(5))  # 120
```

## 3. Euclidean Algorithm
```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """Returns (g, x, y) where g = gcd(a,b) = ax + by."""
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

print(gcd(48, 18))           # 6
print(extended_gcd(48, 18))  # (6, -1, 3)
```

## 4. Sieve of Eratosthenes
```python
def sieve(n):
    """Find all primes up to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i, p in enumerate(is_prime) if p]

print(sieve(50))  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

## 5. Graph Representation and BFS
```python
from collections import deque, defaultdict

class Graph:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)

    def bfs(self, start):
        visited = set()
        queue = deque([start])
        order = []
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                order.append(node)
                queue.extend(self.adj[node])
        return order

g = Graph()
g.add_edge(0, 1); g.add_edge(0, 2); g.add_edge(1, 3)
print(g.bfs(0))  # [0, 1, 2, 3]
```

## 6. Dynamic Programming — Fibonacci
```python
def fib_dp(n):
    """O(n) time, O(1) space Fibonacci."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

print(fib_dp(50))  # 12586269025
```

## 7. Modular Exponentiation
```python
def mod_exp(base, exp, mod):
    """Fast modular exponentiation: O(log exp)."""
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

print(mod_exp(7, 100, 13))  # 9
```

## 8. Recurrence Solver
```python
from sympy import Function, rsolve, symbols

n = symbols('n')
a = Function('a')
# Solve a_n = 2*a_{n-1}, a_0 = 3
eq = a(n) - 2*a(n-1)
sol = rsolve(eq, a(n), {a(0): 3})
print(sol)  # 3*2**n
```
