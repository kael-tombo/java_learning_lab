# Code Deep Dive: 08-normalization-layers
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn08A - BatchNorm-style normalize
[1,3,5,7]: mean 4, var 5, gamma=2 beta=1 rescale.
```java
public class Nn08A {
    public static void main(String[] args) {
        double[] x={1,3,5,7};
        double m=(1+3+5+7)/4.0, v=(9+1+1+9)/4.0;
        System.out.printf("mean=%.1f var=%.1f%n", m, v);
        for(double val:x){double n=(val-m)/Math.sqrt(v+1e-5);System.out.printf("bn=%.4f%n", 2*n+1);}
    }
}
```
Observed output:
```
mean=4.0 var=5.0
bn=-1.6833
bn=0.1056
bn=1.8944
bn=3.6833
```
## Snippet 2: Nn08B - LayerNorm vs RMSNorm
[1,2,3]: centered LN vs scale-only RMS.
```java
public class Nn08B {
    public static void main(String[] args) {
        double[] x={1,2,3};
        double m=2.0, v=(1+0+1)/3.0;
        System.out.printf("layernorm_mean=%.1f var=%.4f%n", m, v);
        StringBuilder a=new StringBuilder(), b=new StringBuilder();
        for(double val:x){a.append(String.format("%.4f ",(val-m)/Math.sqrt(v+1e-5)));b.append(String.format("%.4f ",val/Math.sqrt((1+4+9)/3.0)));}
        System.out.printf("LN=[%s]%n", a.toString().trim());
        System.out.printf("RMS=[%s]%n", b.toString().trim());
    }
}
```
Observed output:
```
layernorm_mean=2.0 var=0.6667
LN=[-1.2247 0.0000 1.2247]
RMS=[0.4629 0.9258 1.3887]
```
## Checks
- Outputs [-1.6833, 0.1056, 1.8944, 3.6833]: zero-mean unit-var then y=2n+1.
- LN=[-1.2247 0 1.2247] (mean 2 removed); RMS=[0.4629 0.9258 1.3887] keeps the mean.

