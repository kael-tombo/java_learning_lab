# Code Deep Dive: 05-probability-distributions
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt05A - Gaussian pdf values
N(0,1) at -1/0/1 plus 68-95 rule constants.
```java
public class Mt05A {
    public static void main(String[] args) {
        double mu=0, sig=1;
        for(double x:new double[]{-1,0,1}){
            double p=Math.exp(-0.5*(x-mu)*(x-mu)/(sig*sig))/(sig*Math.sqrt(2*Math.PI));
            System.out.printf("N(%.0f)=%.4f%n", x, p);
        }
        System.out.printf("P(|Z|<1)=%.4f P(|Z|<2)=%.4f%n", 0.6827, 0.9545);
    }
}
```
Observed output:
```
N(-1)=0.2420
N(0)=0.3989
N(1)=0.2420
P(|Z|<1)=0.6827 P(|Z|<2)=0.9545
```
## Snippet 2: Mt05B - Bayes rule, base-rate example
Prior 0.01, sens 0.99, FPR 0.05: posterior 0.1667.
```java
public class Mt05B {
    public static void main(String[] args) {
        double prior=0.01, sens=0.99, fpr=0.05;
        double num=sens*prior, den=num+fpr*(1-prior);
        System.out.printf("P(D|+)=%.4f (num=%.4f den=%.4f)%n", num/den, num, den);
    }
}
```
Observed output:
```
P(D|+)=0.1667 (num=0.0099 den=0.0594)
```
## Checks
- N(0)=0.3989 = 1/sqrt(2 pi); N(+-1)=0.2420 by symmetry.
- 0.0099/0.0594 = 0.1667: most positives are healthy despite 99% sensitivity (base-rate fallacy demo).

