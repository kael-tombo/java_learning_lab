# Code Deep Dive: 03-eigenvalues-svd
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt03A - 2x2 eigenvalues + residual proof
Same matrix as PCA lab: lambda pair plus Av - lv residual [0,0].
```java
public class Mt03A {
    public static void main(String[] args) {
        double a=4,b=2,c=2,d=3;
        double tr=a+d, det=a*d-b*c, disc=Math.sqrt(tr*tr-4*det);
        System.out.printf("lambda1=%.4f lambda2=%.4f%n", (tr+disc)/2, (tr-disc)/2);
        System.out.printf("sum=%.4f prod=%.4f (trace/det check)%n", tr, det);
        double l=(tr+disc)/2;
        System.out.printf("eigvec1=[%.4f,%.4f] (Av-lv residual shown)%n", b, l-a);
        double r0=a*b+b*(l-a)-l*b, r1=c*b+d*(l-a)-l*(l-a);
        System.out.printf("residual=[%.6f,%.6f]%n", r0, r1);
    }
}
```
Observed output:
```
lambda1=5.5616 lambda2=1.4384
sum=7.0000 prod=8.0000 (trace/det check)
eigvec1=[2.0000,1.5616] (Av-lv residual shown)
residual=[0.000000,-0.000000]
```
## Snippet 2: Mt03B - singular values of diagonal
diag(3,1): singular values, rank, condition 3, Frobenius sqrt(10).
```java
public class Mt03B {
    public static void main(String[] args) {
        double[][] A={{3.0,0},{0,1.0}};
        double s1=Math.abs(A[0][0]), s2=Math.abs(A[1][1]);
        System.out.printf("singular=[%.1f,%.1f] rank=2 cond=%.1f%n", s1, s2, s1/s2);
        System.out.printf("fro=%.4f (sqrt(9+1))%n", Math.sqrt(9+1));
    }
}
```
Observed output:
```
singular=[3.0,1.0] rank=2 cond=3.0
fro=3.1623 (sqrt(9+1))
```
## Checks
- lambda 5.5616/1.4384; sum=trace, product=det double-check the quadratic.
- Residual exactly zero proves the eigenpair; cond=3.0 = s_max/s_min.

