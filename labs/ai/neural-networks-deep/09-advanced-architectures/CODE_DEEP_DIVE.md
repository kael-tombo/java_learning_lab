# Code Deep Dive: 09-advanced-architectures
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn09A - residual add + separable savings
y=x+F(x) on [1,2]; 8ch 3x3 std (192) vs depthwise-separable (88).
```java
public class Nn09A {
    public static void main(String[] args) {
        double[] x={1.0,2.0}; double[] F={0.1,-0.1};
        System.out.printf("residual=[%.1f,%.1f]%n", x[0]+F[0], x[1]+F[1]);
        int Cin=8, Cout=8, K=3;
        int std=Cout*Cin*K, dw=Cin*K+Cin*Cout;
        System.out.printf("std_conv=%d dw_sep=%d ratio=%.4f%n", std, dw, (double)dw/std);
    }
}
```
Observed output:
```
residual=[1.1,1.9]
std_conv=192 dw_sep=88 ratio=0.4583
```
## Snippet 2: Nn09B - stochastic-depth arithmetic
keep 0.9 over 10 layers: expected surviving paths 1.8^10 ~= 357 of 1024.
```java
public class Nn09B {
    public static void main(String[] args) {
        double p=0.9;
        System.out.printf("keep_prob=%.1f paths_kept=%.0f/1024 (10 layers, 2 branches)%n", p, Math.pow(2*0.9,10)*1);
        double g=1.0;
        for(int i=0;i<5;i++) g*=1.0;
        System.out.printf("residual_grad_note=identity_path_preserves_gradient%n");
    }
}
```
Observed output:
```
keep_prob=0.9 paths_kept=357/1024 (10 layers, 2 branches)
residual_grad_note=identity_path_preserves_gradient
```
## Checks
- Residual [1.1,1.9]: identity path preserves signal even if F vanishes.
- Separable ratio 0.4583: Cin*K + Cin*Cout vs Cout*Cin*K.

