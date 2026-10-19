# Code Deep Dive: 01-vectors-spaces
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt01A - dot, norms, cross, cosine
a=[1,2,3], b=[4,-1,2]: full vector toolkit in one pass.
```java
public class Mt01A {
    public static void main(String[] args) {
        double[] a={1,2,3}, b={4,-1,2};
        double dot=a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
        double na=Math.sqrt(1+4+9), nb=Math.sqrt(16+1+4);
        double[] c={a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]};
        System.out.printf("dot=%.1f |a|=%.4f |b|=%.4f%n", dot, na, nb);
        System.out.printf("cross=[%.1f,%.1f,%.1f]%n", c[0],c[1],c[2]);
        System.out.printf("cos=%.4f%n", dot/(na*nb));
    }
}
```
Observed output:
```
dot=8.0 |a|=3.7417 |b|=4.5826
cross=[7.0,10.0,-9.0]
cos=0.4666
```
## Snippet 2: Mt01B - projection and orthogonality
Project [3,4] on [1,0]; residual dot check equals 0.
```java
public class Mt01B {
    public static void main(String[] args) {
        double[] a={3,4}, b={1,0};
        double s=(a[0]*b[0]+a[1]*b[1])/(b[0]*b[0]+b[1]*b[1]);
        System.out.printf("proj=[%.1f,%.1f]%n", s*b[0], s*b[1]);
        System.out.printf("perp=[%.1f,%.1f] check_dot=%.1f%n", a[0]-s*b[0], a[1]-s*b[1], (a[0]-s*b[0])*b[0]+(a[1]-s*b[1])*b[1]);
    }
}
```
Observed output:
```
proj=[3.0,0.0]
perp=[0.0,4.0] check_dot=0.0
```
## Checks
- dot=8, |a|=3.7417=sqrt(14), |b|=4.5826=sqrt(21); cross=[7,10,-9] verifiable by cofactor expansion.
- cos=0.4666; projection [3,0] with perp [0,4] exactly orthogonal (dot 0.0).

