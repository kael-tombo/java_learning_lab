# Real-World Project: Image Compression with SVD

## Overview
Build an image compression tool using Singular Value Decomposition (SVD). This demonstrates how linear algebra powers real technologies like JPEG, recommender systems, and noise reduction.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- MIT OpenCourseWare 18.06 Linear Algebra: https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/
- Stanford EE263 (Introduction to Linear Dynamical Systems): https://see.stanford.edu/course/ee263

## Project Goals
1. Load and preprocess grayscale images
2. Compute SVD of image matrices
3. Compress images using truncated SVD
4. Measure compression ratio vs. quality tradeoff
5. Visualize singular value spectrum

## Mathematical Background

### SVD Recap
Any m×n matrix A decomposes as A = UΣV^T where:
- U: m×m orthogonal (left singular vectors)
- Σ: m×n diagonal (singular values σ₁ ≥ σ₂ ≥ ... ≥ 0)
- V^T: n×n orthogonal (right singular vectors)

### Low-Rank Approximation
Keep only the top k singular values and corresponding vectors:
A_k = Σ(i=1 to k) σ_i u_i v_i^T

**Eckart-Young Theorem:** A_k is the best rank-k approximation of A in both Frobenius and spectral norms.

### Compression Mechanics
- Original image: m×n pixels = mn values
- Rank-k approximation: k(m + n + 1) values (k singular values + k left + k right vectors)
- Compression ratio: mn / (k(m + n + 1))

### Quality Metrics
- **PSNR (Peak Signal-to-Noise Ratio):** 10·log₁₀(MAX²/MSE); higher is better
- **SSIM (Structural Similarity):** Perceptual quality measure

## Implementation Plan

### Phase 1: Image Loading
```python
import numpy as np
from PIL import Image

def load_image(path):
    """Load image as grayscale numpy array."""
    img = Image.open(path).convert('L')
    return np.array(img, dtype=float)
```

### Phase 2: SVD Compression
```python
def compress_image(img, k):
    """Compress image using rank-k SVD approximation."""
    U, S, Vt = np.linalg.svd(img, full_matrices=False)
    # Keep only top k components
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    Vt_k = Vt[:k, :]
    # Reconstruct
    compressed = U_k @ S_k @ Vt_k
    return compressed, U_k, S_k, Vt_k
```

### Phase 3: Quality Assessment
```python
def mse(original, compressed):
    return np.mean((original - compressed) ** 2)

def psnr(original, compressed):
    mse_val = mse(original, compressed)
    if mse_val == 0:
        return float('inf')
    max_pixel = 255.0
    return 10 * np.log10(max_pixel**2 / mse_val)
```

### Phase 4: Visualization
```python
import matplotlib.pyplot as plt

def plot_spectrum(S):
    """Plot singular value distribution."""
    plt.semilogy(S)
    plt.xlabel('Index')
    plt.ylabel('Singular Value')
    plt.title('Singular Value Spectrum')
    plt.show()

def compare_images(original, compressed_list):
    """Show original vs compressed versions."""
    fig, axes = plt.subplots(1, len(compressed_list) + 1, figsize=(15, 5))
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title('Original')
    for ax, (k, img) in zip(axes[1:], compressed_list):
        ax.imshow(img, cmap='gray')
        ax.set_title(f'Rank-{k}')
    plt.show()
```

### Phase 5: Compression Curve
Plot PSNR vs. compression ratio for k = 1, 2, 5, 10, 20, 50, 100.

## Validation
- Verify reconstruction quality matches theoretical bounds
- Compare with JPEG at similar file sizes
- Check that singular values decay rapidly for natural images

## Extensions
- Color image compression (apply SVD to each channel)
- Block-based SVD for better local adaptation
- Hybrid compression: SVD + quantization
- Recommender system using SVD (collaborative filtering)
- PCA for face recognition (Eigenfaces)

## Deliverables
- `svd_compression.py` — core compression library
- `compress.py` — CLI tool for compressing images
- `analyze.py` — quality metrics and visualization
- `README.md` — theory, usage, and results
