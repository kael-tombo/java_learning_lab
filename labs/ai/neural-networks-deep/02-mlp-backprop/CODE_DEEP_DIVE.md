# Code Deep Dive: 02-mlp-backprop
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn02A - 2-2-1 forward pass
Fixed W1, b1, W2: sigmoid hidden, linear out; hand-checkable arithmetic.
```java
public class Nn02A {
    public static void main(String[] args) {
        double[] x={0.5,-0.5};
        double[][] W1={{0.4,-0.2},{0.1,0.3}}; double[] b1={0.1,-0.1};
        double[] h=new double[2];
        for(int j=0;j<2;j++){double s=b1[j]+W1[0][j]*x[0]+W1[1][j]*x[1];h[j]=1/(1+Math.exp(-s));}
        double[] W2={0.6,-0.4}; double b2=0.0;
        double o=b2+W2[0]*h[0]+W2[1]*h[1];
        System.out.printf("h=[%.4f,%.4f]%n", h[0],h[1]);
        System.out.printf("out=%.4f%n", o);
    }
}
```
Observed output:
```
h=[0.5622,0.4134]
out=0.1720
```
## Snippet 2: Nn02B - one sigmoid-CE gradient step
p=0.5498 at w=0.4; analytic dL/dw, dL/db then lr=0.5 step.
```java
public class Nn02B {
    public static void main(String[] args) {
        double x=0.5, t=1.0;
        double w=0.4, b=0.0;
        double z=w*x+b, p=1/(1+Math.exp(-z));
        double loss=-(t*Math.log(p)+(1-t)*Math.log(1-p));
        double dzdw=(p-t)*x, dzdb=(p-t);
        System.out.printf("p=%.4f loss=%.4f dL/dw=%.4f dL/db=%.4f%n", p, loss, dzdw, dzdb);
        w-=0.5*dzdw;
        System.out.printf("w_new=%.4f%n", w);
    }
}
```
Observed output:
```
p=0.5498 loss=0.5981 dL/dw=-0.2251 dL/db=-0.4502
w_new=0.5125
```
## Checks
- h=[0.5622,0.4134], out=0.1720: recompute z1=0.25 -> sigmoid 0.5622 by hand.
- Gradients (-0.2251,-0.4502) equal (p-t)x,(p-t); w moves 0.4 -> 0.5125.

