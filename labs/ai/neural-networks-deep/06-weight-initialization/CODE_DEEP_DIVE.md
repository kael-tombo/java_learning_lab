# Code Deep Dive: 06-weight-initialization
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn06A - Xavier/He formulas
fanIn=4, fanOut=3: variances and uniform bounds.
```java
public class Nn06A {
    public static void main(String[] args) {
        int fanIn=4, fanOut=3;
        System.out.printf("xavier_var=%.4f (1/fanIn)%n", 1.0/fanIn);
        System.out.printf("he_var=%.4f (2/fanIn)%n", 2.0/fanIn);
        System.out.printf("xavier_uniform_bound=+-%.4f%n", Math.sqrt(6.0/(fanIn+fanOut)));
        System.out.printf("he_uniform_bound=+-%.4f%n", Math.sqrt(6.0/fanIn));
    }
}
```
Observed output:
```
xavier_var=0.2500 (1/fanIn)
he_var=0.5000 (2/fanIn)
xavier_uniform_bound=+-0.9258
he_uniform_bound=+-1.2247
```
## Snippet 2: Nn06B - He sampling check
10000 Gaussian draws scaled by sqrt(2/fanIn), seed 42.
```java
public class Nn06B {
    public static void main(String[] args) {
        java.util.Random r=new java.util.Random(42);
        int n=10000, fanIn=100;
        double s=0,s2=0;
        for(int i=0;i<n;i++){double v=r.nextGaussian()*Math.sqrt(2.0/fanIn);s+=v;s2+=v*v;}
        System.out.printf("he_sample_mean=%.4f var=%.4f target=%.4f%n", s/n, s2/n, 2.0/fanIn);
    }
}
```
Observed output:
```
he_sample_mean=0.0011 var=0.0199 target=0.0200
```
## Checks
- Xavier var 0.25, He var 0.5; bounds +-0.9258 / +-1.2247 from sqrt(6/(in+out)) / sqrt(6/in).
- Sample var 0.0199 vs target 0.0200: law of large numbers in action.

