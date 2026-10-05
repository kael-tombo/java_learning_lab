# Mini Project: Matrix Calculator Library

## Goal
Build a pure-Python matrix calculator (no NumPy) that supports core linear algebra operations, demonstrating understanding of the underlying algorithms.

## Requirements
1. Matrix creation from nested lists
2. Addition, subtraction, scalar multiplication
3. Matrix multiplication (naive and Strassen for large matrices)
4. Transpose and trace
5. Determinant (cofactor expansion and LU decomposition)
6. Inverse (Gauss-Jordan elimination)
7. Rank (row reduction)
8. Eigenvalues (power iteration for dominant eigenvalue)

## Architecture
```python
class Matrix:
    def __init__(self, data): ...
    def __add__(self, other): ...
    def __mul__(self, other): ...
    def transpose(self): ...
    def determinant(self): ...
    def inverse(self): ...
    def rank(self): ...
```

## Step 1: Basic Operations
```python
class Matrix:
    def __init__(self, data):
        self.data = [row[:] for row in data]
        self.rows = len(data)
        self.cols = len(data[0])

    def __add__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Dimension mismatch")
        return Matrix([[self.data[i][j] + other.data[i][j]
                        for j in range(self.cols)]
                       for i in range(self.rows)])

    def __mul__(self, other):
        if self.cols != other.rows:
            raise ValueError("Inner dimensions must match")
        result = [[sum(self.data[i][k] * other.data[k][j]
                       for k in range(self.cols))
                   for j in range(other.cols)]
                  for i in range(self.rows)]
        return Matrix(result)
```

## Step 2: Determinant via LU Decomposition
```python
def determinant(self):
    if self.rows != self.cols:
        raise ValueError("Matrix must be square")
    # LU decomposition with partial pivoting
    n = self.rows
    A = [row[:] for row in self.data]
    det = 1
    for i in range(n):
        # Partial pivoting
        max_row = max(range(i, n), key=lambda r: abs(A[r][i]))
        if max_row != i:
            A[i], A[max_row] = A[max_row], A[i]
            det *= -1
        if abs(A[i][i]) < 1e-10:
            return 0
        det *= A[i][i]
        for j in range(i+1, n):
            factor = A[j][i] / A[i][i]
            for k in range(i, n):
                A[j][k] -= factor * A[i][k]
    return det
```

## Step 3: Gauss-Jordan Inverse
```python
def inverse(self):
    n = self.rows
    # Augment with identity
    aug = [self.data[i] + [1 if i == j else 0 for j in range(n)]
           for i in range(n)]
    # Forward elimination
    for i in range(n):
        pivot = aug[i][i]
        if abs(pivot) < 1e-10:
            raise ValueError("Matrix is singular")
        aug[i] = [x / pivot for x in aug[i]]
        for j in range(n):
            if j != i:
                factor = aug[j][i]
                aug[j] = [aug[j][k] - factor * aug[i][k] for k in range(2*n)]
    return Matrix([row[n:] for row in aug])
```

## Step 4: Power Iteration for Eigenvalues
```python
def power_iteration(self, iterations=1000):
    """Find dominant eigenvalue and eigenvector."""
    import random
    b = [random.random() for _ in range(self.rows)]
    for _ in range(iterations):
        # Multiply Ab
        Ab = [sum(self.data[i][j] * b[j] for j in range(self.cols))
              for i in range(self.rows)]
        norm = sum(x**2 for x in Ab) ** 0.5
        b = [x / norm for x in Ab]
    # Rayleigh quotient for eigenvalue
    Ab = [sum(self.data[i][j] * b[j] for j in range(self.cols))
          for i in range(self.rows)]
    eigenvalue = sum(b[i] * Ab[i] for i in range(self.rows))
    return eigenvalue, b
```

## Testing
```python
A = Matrix([[4, 7], [2, 6]])
assert A.determinant() == 10
assert (A * A.inverse()).is_identity()
```

## Extensions
- Strassen multiplication for large matrices
- QR algorithm for all eigenvalues
- Sparse matrix support
- Symbolic computation with SymPy

## Deliverables
- `matrix.py` — Matrix class
- `test_matrix.py` — unit tests
- `README.md` — usage examples
