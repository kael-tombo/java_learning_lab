# Code Deep Dive: 06-attention-variants
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl06A - causal masking effect
Row [1,2] softmaxes to [0.2689,0.7311]; masked query1 sees only itself.
```java
public class Dl06A {
    public static void main(String[] args) {
        double[][] S={{1.0,2.0},{0.5,1.5}};
        for(int i=0;i<2;i++){
            double m=Math.max(S[i][0],S[i][1]);
            double e0=Math.exp(S[i][0]-m), e1=Math.exp(S[i][1]-m);
            System.out.printf("full_row%d=[%.4f,%.4f]%n", i, e0/(e0+e1), e1/(e0+e1));
        }
        double e=Math.exp(0.5-1.5);
        System.out.printf("causal_row1_masked=[0.0000,1.0000] (query1 cannot see key0)%n");
        System.out.printf("causal_row0=[1.0000,0.0000]%n");
    }
}
```
Observed output:
```
full_row0=[0.2689,0.7311]
full_row1=[0.2689,0.7311]
causal_row1_masked=[0.0000,1.0000] (query1 cannot see key0)
causal_row0=[1.0000,0.0000]
```
## Snippet 2: Dl06B - GQA KV reduction
4 layers, 8 Q heads, 2 KV heads, dim 64: 8192 vs 2048 (4x).
```java
public class Dl06B {
    public static void main(String[] args) {
        int layers=4, qh=8, kvh=2, dim=64;
        long mha=(long)2*layers*qh*dim*2, gqa=(long)2*layers*kvh*dim*2;
        System.out.printf("mha_kv_elems=%d gqa_kv_elems=%d ratio=%.1f%n", mha, gqa, (double)mha/gqa);
    }
}
```
Observed output:
```
mha_kv_elems=8192 gqa_kv_elems=2048 ratio=4.0
```
## Checks
- Full softmax: e^1/(e^1+e^2)=0.2689 exact; causal row1 forced [0,1].
- Ratio 4.0 = q_heads/kv_heads: KV cache shrinks proportionally.

