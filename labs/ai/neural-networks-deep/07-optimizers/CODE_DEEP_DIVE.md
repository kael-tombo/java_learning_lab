# Code Deep Dive: 07-optimizers
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn07A - SGD with momentum
g=0.4 constant, lr=0.1, mu=0.9, 3 steps from w=1.
```java
public class Nn07A {
    public static void main(String[] args) {
        double w=1.0, g=0.4, v=0, lr=0.1, mu=0.9;
        for(int t=1;t<=3;t++){v=mu*v+g; w-=lr*v; System.out.printf("t%d v=%.4f w=%.4f%n", t, v, w);}
    }
}
```
Observed output:
```
t1 v=0.4000 w=0.9600
t2 v=0.7600 w=0.8840
t3 v=1.0840 w=0.7756
```
## Snippet 2: Nn07B - Adam two steps
grads [0.4,0.3], bias-corrected m/v updates.
```java
public class Nn07B {
    public static void main(String[] args) {
        double w=1.0, m=0, v=0, lr=0.1, b1=0.9, b2=0.999, e=1e-8;
        double[] grads={0.4,0.3};
        for(int t=1;t<=2;t++){double g=grads[t-1];m=b1*m+(1-b1)*g;v=b2*v+(1-b2)*g*g;
            double mh=m/(1-Math.pow(b1,t)), vh=v/(1-Math.pow(b2,t));
            w-=lr*mh/(Math.sqrt(vh)+e);
            System.out.printf("t%d mhat=%.4f vhat=%.4f w=%.4f%n", t, mh, vh, w);}
    }
}
```
Observed output:
```
t1 mhat=0.4000 vhat=0.1600 w=0.9000
t2 mhat=0.3474 vhat=0.1250 w=0.8017
```
## Checks
- Momentum velocity accumulates 0.4->0.76->1.084; w: 0.96->0.884->0.7756.
- Adam t1: mhat=0.4, vhat=0.16, w=0.9; t2 w=0.8017 (adaptive shrink on smaller grad).

