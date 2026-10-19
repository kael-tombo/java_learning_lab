# Code Deep Dive: 08-optimization-fundamentals
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt08A - GD on convex quadratic
f=(w-1)^2 from 5, lr=0.2: 5 steps 5.76 -> 0.0967; f''=2>0.
```java
public class Mt08A {
    public static void main(String[] args) {
        double w=5.0;
        for(int t=0;t<5;t++){double g=2*(w-1);w-=0.2*g;System.out.printf("t%d w=%.4f f=%.4f%n",t,w,(w-1)*(w-1));}
        System.out.printf("f''=2>0 convex global_min_at_w=1%n");
    }
}
```
Observed output:
```
t0 w=3.4000 f=5.7600
t1 w=2.4400 f=2.0736
t2 w=1.8640 f=0.7465
t3 w=1.5184 f=0.2687
t4 w=1.3110 f=0.0967
f''=2>0 convex global_min_at_w=1
```
## Snippet 2: Mt08B - conditioning and stability edge
cond=10 rate 0.6694; lr=0.19 near 2/L=0.2 overshoots to -1.916.
```java
public class Mt08B {
    public static void main(String[] args) {
        double lmax=10, lmin=1;
        System.out.printf("cond=%.1f rate=((k-1)/(k+1))^2=%.4f%n", lmax/lmin, Math.pow((lmax/lmin-1)/(lmax/lmin+1),2));
        double w=5.0;
        for(int t=0;t<3;t++){double g=10*(w-1);w-=0.19*g;}
        System.out.printf("steep_dir_w=%.4f (lr near 2/L edge oscillates slowly)%n", w);
    }
}
```
Observed output:
```
cond=10.0 rate=((k-1)/(k+1))^2=0.6694
steep_dir_w=-1.9160 (lr near 2/L edge oscillates slowly)
```
## Checks
- Monotone descent 5.76/2.07/0.75/0.27/0.10: linear convergence on convex bowl.
- Rate ((10-1)/(10+1))^2=0.6694 per step predicted; lr near limit overshoots past minimum.

