# Code Deep Dive: 05-transformer-from-scratch
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl05A - scaled dot-product attention 2x2
Q=K=I, d=2: scores 0.7071/0, softmax rows [0.6698,0.3302].
```java
public class Dl05A {
    public static void main(String[] args) {
        double[][] Q={{1,0},{0,1}}, K={{1,0},{0,1}};
        double d=2;
        double[][] S=new double[2][2];
        for(int i=0;i<2;i++)for(int j=0;j<2;j++){S[i][j]=(Q[i][0]*K[j][0]+Q[i][1]*K[j][1])/Math.sqrt(d);}
        for(int i=0;i<2;i++){
            double m=Math.max(S[i][0],S[i][1]);
            double e0=Math.exp(S[i][0]-m), e1=Math.exp(S[i][1]-m);
            System.out.printf("row%d scores=[%.4f,%.4f] attn=[%.4f,%.4f]%n", i, S[i][0],S[i][1], e0/(e0+e1), e1/(e0+e1));
        }
    }
}
```
Observed output:
```
row0 scores=[0.7071,0.0000] attn=[0.6698,0.3302]
row1 scores=[0.0000,0.7071] attn=[0.3302,0.6698]
```
## Snippet 2: Dl05B - toy MHA + FFN budget
d=8, 2 heads, dk=4: MHA 256, FFN(32) 512.
```java
public class Dl05B {
    public static void main(String[] args) {
        int d=8, heads=2, dk=4;
        int perHead=3*dk*d+dk*d;
        System.out.printf("per_head_qkvo=%d total_mha=%d (d=8,2 heads,dk=4)%n", perHead, perHead*heads);
        int ff=2*d*32;
        System.out.printf("ffn(d_ff=32)=%d%n", ff);
    }
}
```
Observed output:
```
per_head_qkvo=128 total_mha=256 (d=8,2 heads,dk=4)
ffn(d_ff=32)=512
```
## Checks
- 1/sqrt(2)=0.7071; e^0.7071/(e^0.7071+1)=0.6698 hand-verified.
- Per head 3*32+32=128 QKVO... total 256; FFN 2*8*32=512.

