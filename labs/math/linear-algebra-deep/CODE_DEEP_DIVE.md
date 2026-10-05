# Linear Algebra Code Deep Dive (Python + NumPy)

## 1. Basic Matrix Operations
```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(A + B)        # Element-wise addition
print(A @ B)        # Matrix multiplication
print(A.T)          # Transpose
print(np.linalg.inv(A))   # Inverse
print(np.linalg.det(A))   # Determinant
print(np.linalg.matrix_rank(A))  # Rank
```

## 2. Solving Linear Systems
```python
# Solve Ax = b
A = np.array([[2, 1], [1, -1]])
b = np.array([5, 1])
x = np.linalg.solve(A, b)
print(x)  # [2. 1.]

# Least squares for overdetermined systems
A = np.array([[1, 1], [1, 2], [1, 3]])
b = np.array([2, 3, 5])
x, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)
```

## 3. Eigenvalues and Eigenvectors
```python
A = np.array([[2, 1], [1, 2]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print(eigenvalues)   # [3. 1.]
print(eigenvectors)  # Columns are eigenvectors

# Verify: Av = λv
v = eigenvectors[:, 0]
print(A @ v)                    # [1.414..., 1.414...]
print(eigenvalues[0] * v)       # Same
```

## 4. SVD and Low-Rank Approximation
```python
A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
U, S, Vt = np.linalg.svd(A)
print(S)  # Singular values

# Rank-2 approximation
k = 2
A_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
print(np.linalg.norm(A - A_k, 'fro'))  # Approximation error
```

## 5. Gram-Schmidt Process
```python
def gram_schmidt(vectors):
    """Orthonormalize a set of vectors."""
    basis = []
    for v in vectors:
        w = v.copy().astype(float)
        for b in basis:
            w -= np.dot(v, b) * b
        norm = np.linalg.norm(w)
        if norm > 1e-10:
            basis.append(w / norm)
    return basis

vectors = [np.array([1, 1, 0]), np.array([1, 0, 1]), np.array([0, 1, 1])]
ortho_basis = gram_schmidt(vectors)
```

## 6. QR Decomposition
```python
A = np.array([[1, 1], [1, 0], [0, 1]])
Q, R = np.linalg.qr(A)
print(Q.T @ Q)  # Identity (orthogonal)
print(Q @ R)    # Original A
```

## 7. PCA Implementation
```python
def pca(X, n_components):
    """Principal Component Analysis."""
    # Center the data
    X_centered = X - X.mean(axis=0)
    # SVD
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    # Project onto top components
    X_pca = U[:, :n_components] * S[:n_components]
    # Explained variance ratio
    explained_var = S**2 / np.sum(S**2)
    return X_pca, explained_var[:n_components]
```

## 8. Performance Tips
- Use `np.linalg.solve` instead of computing inverses explicitly
- `scipy.linalg` offers faster routines for large sparse matrices
- Use `np.einsum` for complex tensor contractions
- BLAS/LAPACK backends (OpenBLAS, MKL) dramatically speed up operations
- For huge matrices, consider `scipy.sparse` iterative methods
