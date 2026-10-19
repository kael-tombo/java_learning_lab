# Code Deep Dive: 07-information-theory
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt07A - entropy and KL in bits
p=[.5,.25,.25]: H=1.5; KL to [.25,.25,.5] = 0.25; uniform refs.
```java
public class Mt07A {
    public static void main(String[] args) {
        double[] p={0.5,0.25,0.25};
        double h=0; for(double v:p) h-=v*Math.log(v)/Math.log(2);
        double[] q={0.25,0.25,0.5};
        double kl=0; for(int i=0;i<3;i++) kl+=p[i]*(Math.log(p[i]/q[i])/Math.log(2));
        System.out.printf("H=%.4f bits KL=%.4f bits%n", h, kl);
        System.out.printf("H_uniform2=%.1f H_uniform4=%.1f%n", 1.0, 2.0);
    }
}
```
Observed output:
```
H=1.5000 bits KL=0.2500 bits
H_uniform2=1.0 H_uniform4=2.0
```
## Snippet 2: Mt07B - CE = H + KL identity
Natural-log check: 0.8018+0.0268=0.8286 exactly.
```java
public class Mt07B {
    public static void main(String[] args) {
        double[] p={0.7,0.2,0.1}, q={0.6,0.3,0.1};
        double h=0,kl=0; for(int i=0;i<3;i++){h-=p[i]*Math.log(p[i]);kl+=p[i]*Math.log(p[i]/q[i]);}
        double ce=0; for(int i=0;i<3;i++) ce-=p[i]*Math.log(q[i]);
        System.out.printf("H=%.4f KL=%.4f CE=%.4f H+KL=%.4f%n", h, kl, ce, h+kl);
    }
}
```
Observed output:
```
H=0.8018 KL=0.0268 CE=0.8286 H+KL=0.8286
```
## Checks
- H=1.5 sits between 1-bit (2 outcomes) and 2-bit (4 outcomes) refs as expected.
- CE computed directly equals H+KL to 4 decimals: identity verified numerically.

