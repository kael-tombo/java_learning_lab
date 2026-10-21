# Model Interpretability — Code Deep Dive (JDK only, verified)
Single-class programs, `javac --release 21 -encoding UTF-8`, outputs observed.
## 1. PermutationImportance — reversed-x1 shuffle drops 1.0 to 4/6
```java
public class PermutationImportance {
    static int rule(double x1, double x2) { return (x1 + 0.2 * x2 > 0.5) ? 1 : 0; }
    static double acc(int[] y, int[] p) { int c = 0;
        for (int i = 0; i < y.length; i++) if (y[i] == p[i]) c++; return c / (double) y.length; }
    public static void main(String[] a) {
        double[] x1 = {0.1,0.9,0.8,0.2,0.7,0.3}, x2 = {0.5,0.4,0.9,0.1,0.2,0.8};
        int[] y = {0,1,1,0,1,0}, base = new int[6], perm = new int[6]; int[] rx = {5,4,3,2,1,0};
        for (int i = 0; i < 6; i++) { base[i] = rule(x1[i], x2[i]); perm[i] = rule(x1[rx[i]], x2[i]); }
        double b = acc(y, base), q = acc(y, perm);
        System.out.println("baseline_acc=" + b);
        System.out.println("permuted_x1_acc=" + q);
        System.out.println("importance_x1=" + (b - q));
    }
}
```
```
baseline_acc=1.0
permuted_x1_acc=0.6666666666666666
importance_x1=0.33333333333333337
```
Reversal is a fixed deterministic permutation: same role as a seeded shuffle.
## 2. ShapleyTiny — 2-player margins averaged over both orders
```java
public class ShapleyTiny {
    static double v(boolean p, boolean q) { if (p && q) return 10.0; if (p) return 4.0; if (q) return 3.0; return 0.0; }
    public static void main(String[] a) {
        double p1 = 0.5 * (v(true,false) - v(false,false)) + 0.5 * (v(true,true) - v(false,true));
        double p2 = 0.5 * (v(false,true) - v(false,false)) + 0.5 * (v(true,true) - v(true,false));
        System.out.println("phi1=" + p1);
        System.out.println("phi2=" + p2);
        System.out.println("sum=" + (p1 + p2));
        System.out.println("v12=" + v(true,true));
        System.out.println("efficiency_holds=" + ((p1 + p2) == v(true,true)));
    }
}
```
```
phi1=5.5
phi2=4.5
sum=10.0
v12=10.0
efficiency_holds=true
```
Orders (1,2): margins 4,6; (2,1): 7,3; averages 5.5 and 4.5; sum is exact.
## 3. LimeSurrogate — weighted least squares recovers tangent slope 4
```java
public class LimeSurrogate {
    static double f(double x) { return x * x; }
    public static void main(String[] a) {
        double x0 = 2.0; double[] dx = {-0.4,-0.2,0.0,0.2,0.4};
        double sw = 0, sx = 0, sy = 0, sxx = 0, sxy = 0;
        for (double d : dx) { double w = Math.exp(-(d * d) / (2 * 0.3 * 0.3)), v = f(x0 + d);
            sw += w; sx += w * d; sy += w * v; sxx += w * d * d; sxy += w * d * v; }
        double s = (sw * sxy - sx * sy) / (sw * sxx - sx * sx), c = (sy - s * sx) / sw;
        System.out.println("x0=" + x0 + " true_f=" + f(x0) + " true_grad=" + (2 * x0));
        System.out.println("slope=" + s);
        System.out.println("intercept=" + c);
        System.out.println("slope_close_to_4=" + (Math.abs(s - 4.0) < 0.3));
    }
}
```
```
x0=2.0 true_f=4.0 true_grad=4.0
slope=3.9999999999999982
intercept=4.057135543484657
slope_close_to_4=true
```
Intercept lift above 4.0 is Jensen lift from parabola curvature.
