# Code Deep Dive: 06-bayesian-inference
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt06A - Beta-Binomial conjugate update
Beta(2,2) + 7 heads/10 -> posterior mean 0.6429.
```java
public class Mt06A {
    public static void main(String[] args) {
        int a=2, b=2, heads=7, n=10;
        double postA=(double)(a+heads)/(a+b+n), mean=(double)(a+heads)/(a+b+n);
        System.out.printf("Beta(2,2)+7/10 -> a=%d b=%d post_mean=%.4f%n", a+heads, a+b+n-(a+heads), postA);
        System.out.printf("prior_mean=%.2f post_mean=%.4f%n", 0.5, mean);
    }
}
```
Observed output:
```
Beta(2,2)+7/10 -> a=9 b=5 post_mean=0.6429
prior_mean=0.50 post_mean=0.6429
```
## Snippet 2: Mt06B - MAP grid search
Data [1,2,4] with N(0,sqrt(2)) prior: MAP at m=2.0.
```java
public class Mt06B {
    public static void main(String[] args) {
        double[] xs={1,2,4};
        double best=0, bv=1e18;
        for(double m:new double[]{1.0,2.0,2.5,3.0}){
            double s=0; for(double x:xs)s+=(x-m)*(x-m);
            double post=s+0.5*m*m;
            System.out.printf("m=%.1f nll=%.2f post=%.2f%n", m, s, post);
            if(post<bv){bv=post;best=m;}
        }
        System.out.printf("MAP=%.1f%n", best);
    }
}
```
Observed output:
```
m=1.0 nll=10.00 post=10.50
m=2.0 nll=5.00 post=7.00
m=2.5 nll=4.75 post=7.88
m=3.0 nll=6.00 post=10.50
MAP=2.0
```
## Checks
- Posterior a=9, b=5 (prior + counts); mean 9/14=0.6429 between prior 0.5 and MLE 0.7.
- Post objectives: 10.5/7.0/7.88/10.5 minimum exactly at 2.0.

