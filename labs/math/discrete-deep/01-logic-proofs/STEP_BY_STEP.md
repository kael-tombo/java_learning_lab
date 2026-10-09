# Step by Step: Logic and Proofs

## Worked Example: Prove that √2 is Irrational

We prove that √2 cannot be expressed as a ratio of two integers, using proof by contradiction.

### Step 1: Assume the Opposite

Assume √2 is rational. Then there exist integers a and b (b ≠ 0) with no common factors such that:

√2 = a / b

### Step 2: Square Both Sides

2 = a² / b²

Multiply both sides by b²:

2b² = a²

### Step 3: Analyze Parity

Since a² = 2b², a² is even. A square is even only if its root is even (if a were odd, a² would be odd). So a is even.

Write a = 2k for some integer k.

### Step 4: Substitute Back

2b² = (2k)² = 4k²

Divide by 2:

b² = 2k²

### Step 5: Conclude b is Even

Since b² = 2k², b² is even, so b is even (by the same argument as Step 3).

### Step 6: Derive the Contradiction

Both a and b are even, so they share a common factor of 2. This contradicts our assumption that a and b have no common factors.

### Step 7: Conclude

The assumption that √2 is rational leads to a contradiction. Therefore, √2 is irrational. ∎

---

## Worked Example: Prove "If n² is even, then n is even" by Contrapositive

### Step 1: State the Contrapositive

Original: If n² is even, then n is even.
Contrapositive: If n is odd, then n² is odd.

### Step 2: Assume n is Odd

Let n = 2k + 1 for some integer k.

### Step 3: Compute n²

n² = (2k + 1)² = 4k² + 4k + 1 = 2(2k² + 2k) + 1

### Step 4: Conclude

n² = 2m + 1 where m = 2k² + 2k, so n² is odd. Since the contrapositive is true, the original implication is true. ∎
