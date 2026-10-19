# Code Deep Dive: 10-numerical-computing
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt10A - log-sum-exp stability
[1000,1001,1002]: stable 1002.4076 vs naive Infinity.
```java
public class Mt10A {
    public static void main(String[] args) {
        double[] z={1000,1001,1002};
        double m=z[0]; for(double v:z)m=Math.max(m,v);
        double s=0; for(double v:z)s+=Math.exp(v-m);
        double lse=m+Math.log(s);
        System.out.printf("logsumexp=%.4f (naive exp(1002)=Inf avoided)%n", lse);
        double naive=0; try{for(double v:z)naive+=Math.exp(v);}catch(Exception e){}
        System.out.printf("naive_sum=%s%n", Double.isInfinite(naive)?"Infinity":"finite");
    }
}
```
Observed output:
```
logsumexp=1002.4076 (naive exp(1002)=Inf avoided)
naive_sum=Infinity
```
## Snippet 2: Mt10B - float32 vs float64 accumulation
100000 x 0.1: err 1.44 vs 0.0000.
```java
public class Mt10B {
    public static void main(String[] args) {
        float s32=0; double s64=0;
        for(int i=0;i<100000;i++){s32+=(float)0.1;s64+=0.1;}
        System.out.printf("float32=%.2f float64=%.2f true=10000.0%n", s32, s64);
        System.out.printf("err32=%.2f err64=%.4f%n", Math.abs(10000-s32), Math.abs(10000-s64));
    }
}
```
Observed output:
```
float32=9998.56 float64=10000.00 true=10000.0
err32=1.44 err64=0.0000
```
## Checks
- lse = 1002 + log(e^-2+e^-1+1) = 1002.4076; naive exp overflows to Infinity.
- float32 sum 9998.56: 0.1 is unrepresentable in binary, error accumulates visibly.

