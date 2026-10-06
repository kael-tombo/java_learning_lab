# Linear Algebra for ML - MINI PROJECT

## Project: Matrix Library Implementation

Build a comprehensive matrix library in Java with operations essential for ML.

### Implementation

```java
public class Matrix {
    private double[][] data;
    private int rows, cols;
    
    public Matrix(double[][] data) {
        this.data = data;
        this.rows = data.length;
        this.cols = data[0].length;
    }
    
    public Matrix multiply(Matrix other) {
        if (this.cols != other.rows) 
            throw new IllegalArgumentException("Incompatible dimensions");
        double[][] result = new double[this.rows][other.cols];
        for (int i = 0; i < this.rows; i++)
            for (int j = 0; j < other.cols; j++)
                for (int k = 0; k < this.cols; k++)
                    result[i][j] += this.data[i][k] * other.data[k][j];
        return new Matrix(result);
    }
    
    public Matrix transpose() {
        double[][] result = new double[cols][rows];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                result[j][i] = data[i][j];
        return new Matrix(result);
    }
    
    public double determinant() {
        if (rows != cols) throw new IllegalArgumentException("Must be square");
        if (rows == 1) return data[0][0];
        if (rows == 2) return data[0][0]*data[1][1] - data[0][1]*data[1][0];
        double det = 0;
        for (int j = 0; j < cols; j++)
            det += Math.pow(-1, j) * data[0][j] * minor(0, j).determinant();
        return det;
    }
    
    public Matrix inverse() {
        double det = determinant();
        if (Math.abs(det) < 1e-10) throw new ArithmeticException("Singular matrix");
        double[][] inv = new double[rows][cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                inv[j][i] = Math.pow(-1, i+j) * minor(i, j).determinant() / det;
        return new Matrix(inv);
    }
    
    private Matrix minor(int row, int col) {
        double[][] m = new double[rows-1][cols-1];
        for (int i = 0, mi = 0; i < rows; i++) {
            if (i == row) continue;
            for (int j = 0, mj = 0; j < cols; j++) {
                if (j == col) continue;
                m[mi][mj++] = data[i][j];
            }
            mi++;
        }
        return new Matrix(m);
    }
}
```

### Test It

```java
@Test
public void testMatrixOperations() {
    Matrix A = new Matrix(new double[][]{{1,2},{3,4}});
    Matrix B = new Matrix(new double[][]{{5,6},{7,8}});
    Matrix C = A.multiply(B);
    assertEquals(19, C.get(0,0), 0.001);
    assertEquals(22, C.get(0,1), 0.001);
}
```

## Deliverables

- [ ] Matrix multiplication and transpose
- [ ] Determinant and inverse computation
- [ ] Eigenvalue computation (power iteration)
- [ ] SVD decomposition
- [ ] Unit tests for all operations
