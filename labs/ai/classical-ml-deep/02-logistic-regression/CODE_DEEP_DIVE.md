# Code Deep Dive: 02-logistic-regression
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml02A - sigmoid and cross-entropy
sigmoid(z)=1/(1+e^-z); binary CE = -[y log p + (1-y) log(1-p)] on 3 fixed predictions.
```java
public class Cml02A {
    static double sig(double z){return 1.0/(1.0+Math.exp(-z));}
    public static void main(String[] args) {
        double[] zs={-2,-0.5,0,0.5,2};
        for(double z:zs) System.out.printf("sigmoid(%.1f)=%.4f%n", z, sig(z));
        double[] p={0.9,0.2,0.8}; int[] t={1,0,1};
        double ce=0; for(int i=0;i<3;i++) ce-=t[i]*Math.log(p[i])+(1-t[i])*Math.log(1-p[i]);
        System.out.printf("CE=%.4f avg=%.4f%n", ce, ce/3);
    }
}
```
Observed output:
```
sigmoid(-2.0)=0.1192
sigmoid(-0.5)=0.3775
sigmoid(0.0)=0.5000
sigmoid(0.5)=0.6225
sigmoid(2.0)=0.8808
CE=0.5516 avg=0.1839
```
## Snippet 2: Cml02B - logistic GD on separable 1D data
x=[-2,-1,1,2], y=[0,0,1,1]; 200 GD steps, lr=0.5.
```java
public class Cml02B {
    public static void main(String[] args) {
        double[] x={-2,-1,1,2}; int[] y={0,0,1,1};
        double w=0,b=0,lr=0.5;
        for(int e=0;e<200;e++){double gw=0,gb=0;for(int i=0;i<4;i++){double p=1/(1+Math.exp(-(w*x[i]+b)));double err=p-y[i];gw+=err*x[i];gb+=err;}w-=lr*gw/4;b-=lr*gb/4;}
        System.out.printf("w=%.4f b=%.4f%n", w, b);
        for(double v:new double[]{-1.5,0,1.5}) System.out.printf("x=%.1f p=%.4f%n", v, 1/(1+Math.exp(-(w*v+b))));
    }
}
```
Observed output:
```
w=4.0066 b=0.0000
x=-1.5 p=0.0024
x=0.0 p=0.5000
x=1.5 p=0.9976
```
## Checks
- sigmoid(0)=0.5, sigmoid(2)=0.8808, symmetric: sigmoid(-z)=1-sigmoid(z).
- CE total 0.5516 (avg 0.1839) recomputed term by term.
- Learned w=4.0066, b=0: p(-1.5)=0.0024, p(1.5)=0.9976, clean separation.

