# Code Deep Dive: 09-kv-cache
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Dl09A - KV-cache byte math
12 layers, 8 heads, dim 64: 12288 elems/token, 24KB fp16; 25.17MB at 1024.
```java
public class Dl09A {
    public static void main(String[] args) {
        long L=12, H=8, D=64;
        long perTok=(long)2*L*H*D;
        System.out.printf("per_token_elems=%d fp16_bytes=%d%n", perTok, perTok*2);
        System.out.printf("seq1024_fp16_MB=%.2f%n", perTok*1024*2/1e6);
    }
}
```
Observed output:
```
per_token_elems=12288 fp16_bytes=24576
seq1024_fp16_MB=25.17
```
## Snippet 2: Dl09B - cached vs recompute toy ops
T=512: cached 6.29M vs 25.17M full, saving 18.87M in toy units.
```java
public class Dl09B {
    public static void main(String[] args) {
        long L=12, H=8, D=64, T=512;
        long cached=(long)2*L*H*D*T;
        long fresh=(long)T*T*H*L;
        System.out.printf("cached_attn_ops=%d vs recompute=%d saved=%d%n", cached, fresh, fresh-cached);
    }
}
```
Observed output:
```
cached_attn_ops=6291456 vs recompute=25165824 saved=18874368
```
## Checks
- 2*12*8*64 = 12288; x2 bytes x1024 = 25,165,824 = 25.17MB.
- Toy model stated in code: per-step O(T) cached vs O(T^2) full attention work.

