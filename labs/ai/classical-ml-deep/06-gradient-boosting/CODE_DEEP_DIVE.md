# Code Deep Dive: 06-gradient-boosting
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml06A - residual fitting step
y=[2,3,5,4], constant init 3.5; residuals and SSE after lr=0.5 shrinkage update.
```java
public class Cml06A {
    public static void main(String[] args) {
        double[] y={2,3,5,4};
        double mean=3.5;
        System.out.printf("init_pred=%.1f%n", mean);
        double[] r=new double[4]; double sse=0;
        for(int i=0;i<4;i++){r[i]=y[i]-mean;sse+=r[i]*r[i];}
        System.out.printf("residuals=[%.1f,%.1f,%.1f,%.1f] SSE=%.2f%n", r[0],r[1],r[2],r[3],sse);
        double lr=0.5, sse2=0;
        for(int i=0;i<4;i++){double p=mean+lr*r[i];sse2+=(y[i]-p)*(y[i]-p);}
        System.out.printf("lr=0.5 update SSE=%.4f (was %.2f)%n", sse2, sse);
    }
}
```
Observed output:
```
init_pred=3.5
residuals=[-1.5,-0.5,1.5,0.5] SSE=5.00
lr=0.5 update SSE=1.2500 (was 5.00)
```
## Snippet 2: Cml06B - squared vs absolute loss robustness
Mean/SSE vs median/SAE on [1,2,3,10].
```java
public class Cml06B {
    public static void main(String[] args) {
        double[] y={1,2,3,10};
        double mean=4.0;
        double sseM=0; for(double v:y) sseM+=(v-mean)*(v-mean);
        double med=2.5;
        double sae=0; for(double v:y) sae+=Math.abs(v-med);
        double saeM=0; for(double v:y) saeM+=Math.abs(v-mean);
        System.out.printf("mean=%.1f SSE=%.1f SAE_at_mean=%.1f%n", mean, sseM, saeM);
        System.out.printf("median=%.1f SAE=%.1f -> robust to outlier 10%n", med, sae);
    }
}
```
Observed output:
```
mean=4.0 SSE=50.0 SAE_at_mean=12.0
median=2.5 SAE=10.0 -> robust to outlier 10
```
## Checks
- Residuals [-1.5,-0.5,1.5,0.5], SSE 5.0 -> 1.25 after one lr=0.5 step (4x drop).
- Outlier 10: mean SSE 50.0 vs median SAE 10.0, showing why absolute loss resists outliers.

