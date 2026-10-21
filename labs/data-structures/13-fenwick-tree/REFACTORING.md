# Refactoring Fenwick Tree

## 1. Generic BIT for Different Types

`java
public class FenwickTree<T> {
    private final T[] bit;
    private final BinaryOperator<T> adder;
    private final T zero;
    
    public FenwickTree(int n, BinaryOperator<T> adder, T zero) {
        this.bit = (T[]) new Object[n + 1];
        this.adder = adder;
        this.zero = zero;
    }
}
`

## 2. Long BIT for Large Values

`java
public class LongFenwickTree {
    private final long[] bit;
    // same logic but with long type
}
`

## 3. Range Update + Range Query Encapsulation

`java
public class RangeFenwickTree {
    private FenwickTree b1, b2;
    
    public void rangeAdd(int l, int r, int val) {
        b1.add(l, val);
        b1.add(r + 1, -val);
        b2.add(l, val * (l - 1));
        b2.add(r + 1, -val * r);
    }
    
    public int prefixSum(int i) {
        return b1.sum(i) * i - b2.sum(i);
    }
}
`

## 4. 2D BIT Abstraction

`java
public class FenwickTree2D {
    private final int[][] bit;
    private final int rows, cols;
    
    public void add(int x, int y, int val) {
        for (int i = x + 1; i <= rows; i += i & -i)
            for (int j = y + 1; j <= cols; j += j & -j)
                bit[i][j] += val;
    }
}
`

## 5. Thread-Safe BIT

`java
public class ConcurrentFenwickTree {
    private final AtomicIntegerArray bit;
    
    public void add(int idx, int delta) {
        int i = idx + 1;
        while (i <= n) {
            bit.addAndGet(i, delta);
            i += Integer.lowestOneBit(i);
        }
    }
}
`

## 6. Persistent BIT

Support versioning by storing change history for undo operations.
