# Model Monitoring - Code Deep Dive

Three single-class programs (plain JDK 21+, no libraries). Compile and run:

```sh
javac --release 21 -encoding UTF-8 A*.java B*.java C*.java
```

## A06Psi.java

```java
public class A06Psi {
    public static void main(String[] args) {
        double[] expected = {0.50, 0.30, 0.15, 0.05};
        double[] actual =   {0.42, 0.31, 0.19, 0.08};
        double psi = 0.0;
        for (int i = 0; i < expected.length; i++) {
            double e = expected[i], a = actual[i];
            double term = (a - e) * Math.log(a / e);
            psi += term;
            System.out.printf("bin%d e=%.2f a=%.2f term=%.4f%n", i, e, a, term);
        }
        System.out.printf("PSI=%.4f (relative shift size; larger = more drift)%n", psi);
    }
}
```

Observed output:

```
bin0 e=0.50 a=0.42 term=0.0139
bin1 e=0.30 a=0.31 term=0.0003
bin2 e=0.15 a=0.19 term=0.0095
bin3 e=0.05 a=0.08 term=0.0141
PSI=0.0378 (relative shift size; larger = more drift)
```

## B06Ks.java

```java
import java.util.*;
public class B06Ks {
    public static void main(String[] args) {
        double[] ref = {0.10, 0.22, 0.31, 0.45, 0.52, 0.60, 0.71, 0.83};
        double[] cur = {0.15, 0.28, 0.40, 0.55, 0.62, 0.70, 0.80, 0.95};
        TreeSet<Double> grid = new TreeSet<>();
        for (double v : ref) grid.add(v);
        for (double v : cur) grid.add(v);
        double ks = 0.0, at = 0.0;
        for (double t : grid) {
            double f = cdf(ref, t), g = cdf(cur, t);
            double d = Math.abs(f - g);
            if (d > ks) { ks = d; at = t; }
        }
        System.out.printf("KS=%.3f at x=%.2f (max CDF gap)%n", ks, at);
    }
    static double cdf(double[] s, double t) {
        int c = 0;
        for (double v : s) if (v <= t) c++;
        return (double) c / s.length;
    }
}
```

Observed output:

```
KS=0.250 at x=0.52 (max CDF gap)
```

## C06Alerts.java

```java
public class C06Alerts {
    public static void main(String[] args) {
        int tp = 9, fp = 21, fn = 3;
        double prec = (double) tp / (tp + fp);
        double rec = (double) tp / (tp + fn);
        System.out.printf("tp=%d fp=%d fn=%d precision=%.3f recall=%.3f%n", tp, fp, fn, prec, rec);
        System.out.println("read: tight thresholds cut pages (precision up) but miss drifts (recall down)");
    }
}
```

Observed output:

```
tp=9 fp=21 fn=3 precision=0.300 recall=0.750
read: tight thresholds cut pages (precision up) but miss drifts (recall down)
```

## What each snippet shows
- A06Psi: core measurement for model monitoring.
- B06Ks: central tradeoff or bookkeeping computation.
- C06Alerts: decision rule used before acting on a result.
