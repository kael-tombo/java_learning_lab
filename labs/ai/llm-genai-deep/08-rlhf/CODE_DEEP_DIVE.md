# Code Deep Dive: 08-rlhf
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg08A - SFT->RM->PPO stage trace
Toy stage metrics labeled as illustration: 1.24->0.62, 0.84, kl 0.08.
```java
public class Lg08A {
    public static void main(String[] args) {
        System.out.printf("stage1_SFT: loss=1.24 -> 0.62 (2 epochs, toy)%n");
        System.out.printf("stage2_RM: pair_acc=42/50=0.8400%n");
        System.out.printf("stage3_PPO: kl=0.08 reward=1.35 (KL-penalized)%n");
    }
}
```
Observed output:
```
stage1_SFT: loss=1.24 -> 0.62 (2 epochs, toy)
stage2_RM: pair_acc=42/50=0.8400
stage3_PPO: kl=0.08 reward=1.35 (KL-penalized)
```
## Snippet 2: Lg08B - Bradley-Terry preference
Rewards 1.5 vs 0.5: P=0.7311, loss 0.3133.
```java
public class Lg08B {
    public static void main(String[] args) {
        double ra=1.5, rb=0.5;
        double p=1/(1+Math.exp(-(ra-rb)));
        System.out.printf("BradleyTerry P(A>B)=%.4f (rewards %.1f vs %.1f)%n", p, ra, rb);
        System.out.printf("RM_loss=-log(p)=%.4f%n", -Math.log(p));
    }
}
```
Observed output:
```
BradleyTerry P(A>B)=0.7311 (rewards 1.5 vs 0.5)
RM_loss=-log(p)=0.3133
```
## Checks
- sigmoid(1.0)=0.7311; -log = 0.3133: reward gap of 1 nat gives 73% preference.
- Stage numbers are toy illustrations of pipeline order, not empirical claims.

