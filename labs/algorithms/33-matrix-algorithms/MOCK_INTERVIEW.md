# Mock Interview: Matrix Algorithms
> Three questions on multiplying matrices honestly. Quote the exponent before optimizing.
## Q1: textbook O(n^3) product
Problem: multiply two fixed 3x3 matrices with the triple loop.
Key insight: C[i][j] is the dot product of row i of A with column j of B; ikj loop order reuses the row in cache.
Complexity: O(n^3) time, O(n^2) memory.
```java
public class L33Q1 {
    public static void main(String[] a){
        int[][] A = {{1,2,3},{4,5,6},{7,8,9}}, B = {{9,8,7},{6,5,4},{3,2,1}}, C = new int[3][3];
        for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++){ int s = 0; for (int k = 0; k < 3; k++) s += A[i][k]*B[k][j]; C[i][j] = s; }
        for (int[] row : C) System.out.println(java.util.Arrays.toString(row));
    }
}
```
Observed output:
```
[30, 24, 18]
[84, 69, 54]
[138, 114, 90]
```
Follow-up: why does switching to ikj or blocked order change wall time but not the bound?
## Q2: Strassen 2x2
Problem: multiply [[2,3],[4,5]] by [[6,7],[8,9]] with 7 products instead of 8.
Key insight: the 7 intermediates M1..M7 recombine into the four result entries, giving O(n^log2 7) ~ O(n^2.81); constants restrict the win to large n.
Complexity: O(n^2.81) time, extra temporaries per level.
```java
public class L33Q2 {
    public static void main(String[] a){
        int A=2,B=3,C=4,D=5,E=6,F=7,G=8,H=9;
        int m1=(A+D)*(E+H), m2=(C+D)*E, m3=A*(F-H), m4=D*(G-E), m5=(A+B)*H, m6=(C-A)*(E+F), m7=(B-D)*(G+H);
        System.out.println("strassen=[[" + (m1+m4-m5+m7) + "," + (m3+m5) + "],[" + (m2+m4) + "," + (m1-m2+m3+m6) + "]]");
        System.out.println("naive=[[" + (A*E+B*G) + "," + (A*F+B*H) + "],[" + (C*E+D*G) + "," + (C*F+D*H) + "]]");
    }
}
```
Observed output:
```
strassen=[[36,41],[64,73]]
naive=[[36,41],[64,73]]
```
Follow-up: why do libraries still prefer blocked O(n^3) at moderate sizes?
## Q3: Fibonacci by matrix power
Problem: raise [[1,1],[1,0]] to the 20th by binary exponentiation and read F(20) out of the matrix.
Key insight: M^n[0][1] = F(n), so exponentiation by squaring turns linear recurrence evaluation into O(log n) matrix multiplies.
Complexity: O(log n) multiplies, O(1) memory.
```java
public class L33Q3 {
    static long[][] mul(long[][] A, long[][] B){
        long[][] C = new long[2][2];
        for (int i=0;i<2;i++) for (int j=0;j<2;j++) C[i][j]=A[i][0]*B[0][j]+A[i][1]*B[1][j];
        return C;
    }
    public static void main(String[] a){
        long[][] r = {{1,0},{0,1}}, b = {{1,1},{1,0}};
        for (int n = 20; n > 0; n >>= 1){ if ((n & 1) == 1) r = mul(r,b); b = mul(b,b); }
        System.out.println("fib20=" + r[0][1]);
    }
}
```
Observed output:
```
fib20=6765
```
Follow-up: where else does fast exponentiation apply (modular powers, path counts)?
## Pass checklist
- [ ] Verify the Strassen product entry-by-entry against naive output.
- [ ] Explain the crossover: asymptotically faster is not faster at n = 64.
- [ ] Derive F(20) = 6765 from the powered matrix, not from memory.
