# Code Deep Dive: 03-svm-theory
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml03A - margin width and support distances
For w=[2,0], b=-4: width = 2/||w||; signed value f and |f|/||w|| for 3 points.
```java
public class Cml03A {
    public static void main(String[] args) {
        double[] w={2.0,0.0}; double b=-4.0;
        double norm=Math.sqrt(w[0]*w[0]+w[1]*w[1]);
        System.out.printf("margin_width=%.4f%n", 2.0/norm);
        double[][] pts={{1,0},{3,1},{2,2}};
        for(double[] p:pts){double f=w[0]*p[0]+w[1]*p[1]+b;System.out.printf("pt(%.0f,%.0f) f=%.1f dist=%.4f%n",p[0],p[1],f,Math.abs(f)/norm);}
    }
}
```
Observed output:
```
margin_width=1.0000
pt(1,0) f=-2.0 dist=1.0000
pt(3,1) f=2.0 dist=1.0000
pt(2,2) f=0.0 dist=0.0000
```
## Snippet 2: Cml03B - hinge subgradient descent
Primal objective 0.5 lambda ||w||^2 + max(0, 1 - y f); 50 passes, lr=0.1, lambda=0.01.
```java
public class Cml03B {
    public static void main(String[] args) {
        double[][] X={{1,1},{2,0},{0,2},{3,3}}; int[] y={-1,-1,1,1};
        double[] w={0,0}; double b=0, lr=0.1;
        for(int e=0;e<50;e++) for(int i=0;i<4;i++){
            double m=y[i]*(w[0]*X[i][0]+w[1]*X[i][1]+b);
            if(m<1){w[0]+=lr*(y[i]*X[i][0]-0.01*w[0]);w[1]+=lr*(y[i]*X[i][1]-0.01*w[1]);b+=lr*y[i];}
            else{w[0]-=lr*0.01*w[0];w[1]-=lr*0.01*w[1];}
        }
        System.out.printf("w=[%.4f,%.4f] b=%.4f%n", w[0],w[1],b);
        int ok=0; for(int i=0;i<4;i++){int pr=(w[0]*X[i][0]+w[1]*X[i][1]+b)>=0?1:-1; if(pr==y[i])ok++;}
        System.out.printf("train_acc=%d/4%n", ok);
    }
}
```
Observed output:
```
w=[-0.5060,1.7273] b=-2.3000
train_acc=4/4
```
## Checks
- Margin width = 1.0; points (1,0) and (3,1) sit at distance exactly 1.0 (support vectors), (2,2) on the plane.
- Hinge trainer reaches 4/4 train accuracy; w=[-0.5060,1.7273], b=-2.3.

