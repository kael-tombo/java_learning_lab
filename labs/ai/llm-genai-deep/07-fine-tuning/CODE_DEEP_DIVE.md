# Code Deep Dive: 07-fine-tuning
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg07A - LoRA param ratio
d=k=64, r=4: 512 vs 4096 = 0.125; frozen base + BA.
```java
public class Lg07A {
    public static void main(String[] args) {
        long d=64, k=64, r=4;
        long full=d*k, lora=(long)r*(d+k);
        System.out.printf("full=%d lora=%d ratio=%.4f%n", full, lora, (double)lora/full);
        System.out.printf("frozen_base + trainable BA (rank %d)%n", r);
    }
}
```
Observed output:
```
full=4096 lora=512 ratio=0.1250
frozen_base + trainable BA (rank 4)
```
## Snippet 2: Lg07B - adapter scaling
alpha=8, r=4: scale 2.0; update 0.25 on x=[1,0.5].
```java
public class Lg07B {
    public static void main(String[] args) {
        double alpha=8, r=4;
        System.out.printf("scale=alpha/r=%.1f%n", alpha/r);
        double[] x={1.0,0.5};
        double adapt=0.5*(0.4*x[0]+0.2*x[1]);
        System.out.printf("adapter_out=%.4f (scaled low-rank update)%n", adapt);
    }
}
```
Observed output:
```
scale=alpha/r=2.0
adapter_out=0.2500 (scaled low-rank update)
```
## Checks
- r*(d+k) = 4*128 = 512 exact; ratio 1/8.
- 0.5*(0.4*1+0.2*0.5) = 0.25 hand-verified.

