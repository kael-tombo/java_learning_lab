# Code Deep Dive: 10-anomaly-detection
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml10A - z-score flags
x=[10,11,12,11,10,11,30]: mean/std, |z|>2 rule.
```java
public class Cml10A {
    public static void main(String[] args) {
        double[] x={10,11,12,11,10,11,30};
        double m=0; for(double v:x)m+=v; m/=x.length;
        double s=0; for(double v:x)s+=(v-m)*(v-m); s=Math.sqrt(s/x.length);
        System.out.printf("mean=%.4f std=%.4f%n", m, s);
        for(double v:x){double z=(v-m)/s;System.out.printf("x=%.0f z=%.2f %s%n", v, z, Math.abs(z)>2?"FLAG":"ok");}
    }
}
```
Observed output:
```
mean=13.5714 std=6.7370
x=10 z=-0.53 ok
x=11 z=-0.38 ok
x=12 z=-0.23 ok
x=11 z=-0.38 ok
x=10 z=-0.53 ok
x=11 z=-0.38 ok
x=30 z=2.44 FLAG
```
## Snippet 2: Cml10B - IQR rule
Sorted data quartiles, upper fence Q3+1.5 IQR.
```java
public class Cml10B {
    public static void main(String[] args) {
        double[] x={10,10,11,11,12,12,30};
        java.util.Arrays.sort(x);
        double q1=x[1], q3=x[5], iqr=q3-q1;
        System.out.printf("Q1=%.1f Q3=%.1f IQR=%.1f upper=%.1f%n", q1,q3,iqr,q3+1.5*iqr);
        for(double v:x) System.out.printf("x=%.0f %s%n", v, v>q3+1.5*iqr?"FLAG":"ok");
    }
}
```
Observed output:
```
Q1=10.0 Q3=12.0 IQR=2.0 upper=15.0
x=10 ok
x=10 ok
x=11 ok
x=11 ok
x=12 ok
x=12 ok
x=30 FLAG
```
## Checks
- Mean 13.5714, std 6.7370; only 30 exceeds |z|>2 (z=2.44).
- Q1=10, Q3=12, fence 15.0: only 30 flagged; agrees with z-score here.

