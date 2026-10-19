# Code Deep Dive: 10-model-compression
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Nn10A - magnitude pruning
Threshold 0.1 on 6 weights: sparsity 3/6.
```java
public class Nn10A {
    public static void main(String[] args) {
        double[] w={0.9,-0.05,0.4,-0.01,0.02,-0.7};
        double t=0.1; int kept=0;
        StringBuilder sb=new StringBuilder();
        for(double v:w){boolean k=Math.abs(v)>=t;if(k)kept++;sb.append(k?String.format("%.2f ",v):"0 ");}
        System.out.printf("pruned=[%s]%n", sb.toString().trim());
        System.out.printf("sparsity=%d/%d=%.4f%n", w.length-kept, w.length, (double)(w.length-kept)/w.length);
    }
}
```
Observed output:
```
pruned=[0.90 0 0.40 0 0 -0.70]
sparsity=3/6=0.5000
```
## Snippet 2: Nn10B - int8 quantization + distill KL
Scale 1/127, max error; teacher/student KL=0.0268.
```java
public class Nn10B {
    public static void main(String[] args) {
        double[] w={-1.0,-0.5,0.0,0.5,1.0};
        double scale=1.0/127;
        double maxe=0;
        for(double v:w){int q=(int)Math.round(v/scale);double dq=q*scale;maxe=Math.max(maxe,Math.abs(v-dq));}
        System.out.printf("int8_scale=%.6f max_abs_err=%.6f%n", scale, maxe);
        double[] pt={0.7,0.2,0.1}, ps={0.6,0.3,0.1};
        double kl=0; for(int i=0;i<3;i++) kl+=pt[i]*Math.log(pt[i]/ps[i]);
        System.out.printf("distill_KL=%.4f%n", kl);
    }
}
```
Observed output:
```
int8_scale=0.007874 max_abs_err=0.003937
distill_KL=0.0268
```
## Checks
- Pruned [0.90 0 0.40 0 0 -0.70]: 50% sparse, largest weights survive.
- Max abs error 0.0039 = scale/2; KL 0.0268 quantifies teacher-student gap.

