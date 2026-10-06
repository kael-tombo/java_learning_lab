# Linear Algebra for ML - REAL WORLD PROJECT

## Project: Image Compression using SVD

Build an image compression system using Singular Value Decomposition.

### Architecture

```
Image → Grayscale Matrix → SVD → Truncate → Reconstruct → Compressed Image
```

### Implementation

```java
public class ImageCompressor {
    private Matrix imageMatrix;
    private Matrix U, S, V;
    
    public void compress(String imagePath, int rank) throws IOException {
        BufferedImage img = ImageIO.read(new File(imagePath));
        imageMatrix = toMatrix(img);
        
        // Perform SVD
        SingularValueDecomposition svd = new SingularValueDecomposition(imageMatrix);
        U = svd.getU();
        S = svd.getS();
        V = svd.getV();
        
        // Truncate to rank k
        Matrix Uk = U.getSubMatrix(0, U.rows-1, 0, rank-1);
        Matrix Sk = S.getSubMatrix(0, rank-1, 0, rank-1);
        Matrix Vk = V.getSubMatrix(0, V.rows-1, 0, rank-1);
        
        // Reconstruct
        Matrix compressed = Uk.multiply(Sk).multiply(Vk.transpose());
        saveImage(compressed, "compressed.png");
    }
    
    public double compressionRatio(int originalSize, int rank) {
        return (double) originalSize / (rank * (U.rows + V.rows + 1));
    }
    
    public double psnr(Matrix original, Matrix reconstructed) {
        double mse = 0;
        for (int i = 0; i < original.rows; i++)
            for (int j = 0; j < original.cols; j++)
                mse += Math.pow(original.get(i,j) - reconstructed.get(i,j), 2);
        mse /= (original.rows * original.cols);
        return 10 * Math.log10(255*255 / mse);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- SVD is the foundation of many dimensionality reduction techniques used in production ML systems.
- Reference: https://en.wikipedia.org/wiki/Singular_value_decomposition
- Reference: https://www.mathworks.com/help/matlab/ref/svd.html

## Deliverables

- [x] Image loading and matrix conversion
- [x] SVD decomposition implementation
- [x] Rank-k approximation
- [x] Compression ratio and PSNR calculation
- [x] Visualization of compressed images
