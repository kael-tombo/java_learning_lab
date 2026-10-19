# Code Deep Dive: 05-regularization
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn05A - L1/L2 penalties
w=[0.5,-1.5,0.2]: L1=2.2, L2=2.54; loss 1.0 + 0.1 penalty terms.
```java
public class Nn05A {
    public static void main(String[] args) {
        double[] w={0.5,-1.5,0.2};
        double l1=0,l2=0; for(double v:w){l1+=Math.abs(v);l2+=v*v;}
        System.out.printf("L1=%.4f L2=%.4f%n", l1, l2);
        System.out.printf("loss+0.1*L1=%.4f loss+0.1*L2=%.4f (base=1.0)%n", 1+0.1*l1, 1+0.1*l2/2);
    }
}
```
Observed output:
```
L1=2.2000 L2=2.5400
loss+0.1*L1=1.2200 loss+0.1*L2=1.1270 (base=1.0)
```
## Snippet 2: Nn05B - inverted dropout
Mask [1,0,1,0] at p=0.5 with 1/(1-p) rescaling.
```java
public class Nn05B {
    public static void main(String[] args) {
        double[] h={1.0,2.0,3.0,4.0};
        int[] mask={1,0,1,0};
        double p=0.5;
        StringBuilder sb=new StringBuilder();
        for(int i=0;i<4;i++){double v=mask[i]==1?h[i]/(1-p):0;sb.append(String.format("%.1f ",v));}
        System.out.printf("inverted_dropout=[%s]%n", sb.toString().trim());
        System.out.printf("train_scale=1/(1-p)=%.1f%n", 1/(1-p));
    }
}
```
Observed output:
```
inverted_dropout=[2.0 0.0 6.0 0.0]
train_scale=1/(1-p)=2.0
```
## Checks
- 1+0.1*2.2=1.22 vs 1+0.1*2.54/2=1.1270: L1 penalizes linearly, L2 quadratically (halved form).
- Dropout output [2.0 0.0 6.0 0.0] keeps expectation: E[mask*x]/(1-p) = x.

