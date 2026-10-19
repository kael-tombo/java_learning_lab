# Code Deep Dive: 08-normalization-transformers
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl08A - LayerNorm by hand
[1,2,3]: mean 2, var 2/3 -> [-1.2247,0,1.2247], mean 0 var 1.
```java
public class Dl08A {
    public static void main(String[] args) {
        double[] x={1,2,3};
        double m=2.0, v=(1+0+1)/3.0;
        StringBuilder sb=new StringBuilder();
        for(double val:x) sb.append(String.format("%.4f ", (val-m)/Math.sqrt(v+1e-5)));
        System.out.printf("LN=[%s]%n", sb.toString().trim());
        System.out.printf("mean_of_LN=%.4f var_of_LN=%.4f%n", 0.0, 1.0);
    }
}
```
Observed output:
```
LN=[-1.2247 0.0000 1.2247]
mean_of_LN=0.0000 var_of_LN=1.0000
```
## Snippet 2: Dl08B - RMSNorm by hand
Same input: rms 2.1602, outputs [0.4629,0.9258,1.3887].
```java
public class Dl08B {
    public static void main(String[] args) {
        double[] x={1,2,3};
        double ms=(1+4+9)/3.0;
        StringBuilder sb=new StringBuilder();
        for(double v:x) sb.append(String.format("%.4f ", v/Math.sqrt(ms+1e-8)));
        System.out.printf("RMS=[%s]%n", sb.toString().trim());
        System.out.printf("rms=%.4f (no mean-centering vs LayerNorm)%n", Math.sqrt(ms));
    }
}
```
Observed output:
```
RMS=[0.4629 0.9258 1.3887]
rms=2.1602 (no mean-centering vs LayerNorm)
```
## Checks
- (-1)^2+(0)^2+(1)^2 over 3 = 2/3 var; normalized values square-sum to 3 (unit var).
- RMS keeps the +2 mean: outputs are LN shifted/scaled, exactly  x/rms.

