# Mini Project: Group Theory Explorer

## Goal
Build an interactive tool that explores finite groups: generates Cayley tables, finds subgroups, checks properties, and visualizes group structure.

## Requirements
1. Define groups by their Cayley table or by generators
2. Verify group axioms (closure, associativity, identity, inverses)
3. Compute the order of each element
4. Find all subgroups
5. Check if the group is abelian, cyclic, or simple
6. Generate Cayley graphs (visualization)

## Architecture
```python
class FiniteGroup:
    def __init__(self, elements, cayley_table): ...
    def verify_axioms(self): ...
    def element_order(self, g): ...
    def find_subgroups(self): ...
    def is_abelian(self): ...
    def is_cyclic(self): ...
    def cayley_graph(self): ...
```

## Step 1: Group Definition
```python
class FiniteGroup:
    def __init__(self, elements, table):
        self.elements = list(elements)
        self.table = table  # table[i][j] = index of elements[i] * elements[j]
        self.index = {e: i for i, e in enumerate(self.elements)}

    def multiply(self, a, b):
        return self.elements[self.table[self.index[a]][self.index[b]]]
```

## Step 2: Axiom Verification
```python
def verify_axioms(self):
    n = len(self.elements)
    # Closure: table entries are valid indices
    for i in range(n):
        for j in range(n):
            if self.table[i][j] >= n:
                return False, "Closure failed"
    # Identity: find e such that e*a = a for all a
    identity = None
    for e in range(n):
        if all(self.table[e][j] == j for j in range(n)):
            identity = e
            break
    if identity is None:
        return False, "No identity"
    # Inverses: for each a, exists b with a*b = e
    for a in range(n):
        if not any(self.table[a][b] == identity for b in range(n)):
            return False, f"No inverse for {self.elements[a]}"
    # Associativity: (a*b)*c = a*(b*c)
    for a in range(n):
        for b in range(n):
            for c in range(n):
                ab_c = self.table[self.table[a][b]][c]
                a_bc = self.table[a][self.table[b][c]]
                if ab_c != a_bc:
                    return False, "Associativity failed"
    return True, "Valid group"
```

## Step 3: Element Orders
```python
def element_order(self, g):
    """Find smallest n > 0 such that g^n = e."""
    current = g
    order = 1
    while current != self.elements[self.identity_index]:
        current = self.multiply(current, g)
        order += 1
        if order > len(self.elements):
            return None  # Should not happen in finite group
    return order
```

## Step 4: Subgroup Finding
```python
def find_subgroups(self):
    """Find all subgroups by checking all subsets (brute force for small groups)."""
    from itertools import combinations
    n = len(self.elements)
    subgroups = []
    for size in range(1, n + 1):
        for subset in combinations(range(n), size):
            if self.is_subgroup(set(subset)):
                subgroups.append([self.elements[i] for i in subset])
    return subgroups

def is_subgroup(self, subset):
    """Check if subset is closed under multiplication and inverses."""
    e = self.identity_index
    if e not in subset:
        return False
    for a in subset:
        for b in subset:
            if self.table[a][b] not in subset:
                return False
    return True
```

## Step 5: Cayley Graph
```python
def cayley_graph(self, generators):
    """Generate adjacency list for Cayley graph."""
    graph = {e: [] for e in self.elements}
    for g in self.elements:
        for gen in generators:
            graph[g].append(self.multiply(g, gen))
    return graph
```

## Testing
```python
# S_3: symmetric group on 3 elements (order 6)
# Z/4Z: cyclic group of order 4
# Klein four-group: Z/2Z × Z/2Z
```

## Extensions
- Compute conjugacy classes
- Find normal subgroups
- Compute quotient groups
- Visualize with networkx or graphviz
- Character table computation

## Deliverables
- `group_explorer.py` — main module
- `test_groups.py` — unit tests
- `README.md` — usage examples
