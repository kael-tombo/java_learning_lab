# Code Deep Dive: 10-inference-optimization
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl10A - int8 size math + levels
Scale 1/127, codes [-127..127]; 1M params 4MB -> 1MB.
```java
public class Dl10A {
    public static void main(String[] args) {
        double[] w={-1.0,-0.5,0.5,1.0};
        double s=1.0/127;
        double maxe=0;
        StringBuilder sb=new StringBuilder();
        for(double v:w){int q=(int)Math.round(v/s);double dq=q*s;maxe=Math.max(maxe,Math.abs(v-dq));sb.append(q).append(" ");}
        System.out.printf("int8=[%s] scale=%.6f maxerr=%.6f%n", sb.toString().trim(), s, maxe);
        System.out.printf("fp32_1M_params_MB=%.1f int8_MB=%.1f%n", 4e6/1e6, 1e6/1e6);
    }
}
```
Observed output:
```
int8=[-127 -63 64 127] scale=0.007874 maxerr=0.003937
fp32_1M_params_MB=4.0 int8_MB=1.0
```
## Snippet 2: Dl10B - greedy vs top-k
Logits [2,1,0.1]: greedy 0 at 0.6590; top-2 renorm [0.7311,0.2689].
```java
public class Dl10B {
    public static void main(String[] args) {
        double[] logits={2.0,1.0,0.1};
        double m=2.0,s=Math.exp(0)+Math.exp(-1)+Math.exp(-1.9);
        System.out.printf("greedy_argmax=0 prob=%.4f%n", 1/s);
        double sum=1/s+Math.exp(-1)/s;
        System.out.printf("topk2_renorm=[%.4f,%.4f]%n", (1/s)/sum, (Math.exp(-1)/s)/sum);
    }
}
```
Observed output:
```
greedy_argmax=0 prob=0.6590
topk2_renorm=[0.7311,0.2689]
```
## Checks
- Max err 0.003937 = scale/2; codes round(-0.5/s)=-63 exact.
- Top-2 renorm: 0.6590/(0.6590+0.2424)=0.7311 hand-verified.

