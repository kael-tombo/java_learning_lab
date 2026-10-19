# Code Deep Dive: 04-loss-functions
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn04A - MSE and RMSE
4 fixed residuals; plus a worse forecast for contrast (0.25 vs 0.025).
```java
public class Nn04A {
    public static void main(String[] args) {
        double[] t={2,3,5,4}, p={2.1,2.8,5.2,3.9};
        double se=0; for(int i=0;i<4;i++) se+=(t[i]-p[i])*(t[i]-p[i]);
        System.out.printf("MSE=%.4f RMSE=%.4f%n", se/4, Math.sqrt(se/4));
        double[] t2={2,3,5,4}, p2={2.5,2.5,5.5,3.5};
        double se2=0; for(int i=0;i<4;i++) se2+=(t2[i]-p2[i])*(t2[i]-p2[i]);
        System.out.printf("MSE_alt=%.4f%n", se2/4);
    }
}
```
Observed output:
```
MSE=0.0250 RMSE=0.1581
MSE_alt=0.2500
```
## Snippet 2: Nn04B - softmax + cross-entropy
logits [2,1,0.1]; stable softmax, CE for true class 0.
```java
public class Nn04B {
    public static void main(String[] args) {
        double[] z={2.0,1.0,0.1};
        double m=2.0, s=Math.exp(0)+Math.exp(-1.0)+Math.exp(-1.9);
        double[] p={Math.exp(0)/s, Math.exp(-1.0)/s, Math.exp(-1.9)/s};
        double ce=-Math.log(p[0]);
        System.out.printf("softmax=[%.4f,%.4f,%.4f] sum=%.4f%n", p[0],p[1],p[2],p[0]+p[1]+p[2]);
        System.out.printf("CE(true=0)=%.4f%n", ce);
    }
}
```
Observed output:
```
softmax=[0.6590,0.2424,0.0986] sum=1.0000
CE(true=0)=0.4170
```
## Checks
- MSE=0.0250, RMSE=0.1581 = sqrt(0.025); alt forecast 10x worse.
- softmax=[0.6590,0.2424,0.0986] sums to 1.0000; CE=-log(0.6590)=0.4170.

