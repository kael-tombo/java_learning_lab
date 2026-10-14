# Code Deep Dive - Anomaly Detection (JDK only)

Compile with `javac --release 21 -encoding UTF-8`; outputs below are observed.

## 1. AnomBase - z-score and IQR flags agree

```java
public class AnomBase {
    public static void main(String[] args) {
        double[] x = {10.1, 9.8, 10.3, 10.0, 9.9, 10.2, 10.1, 30.0, 9.7, 10.4, 10.0};
        double m = 0; for (double v : x) m += v; m /= x.length;
        double s = 0; for (double v : x) s += (v - m) * (v - m); s = Math.sqrt(s / x.length);
        System.out.println("mean=" + f(m) + " sd=" + f(s));
        System.out.print("z>3 flags:");
        for (int i = 0; i < x.length; i++)
            if (Math.abs((x[i] - m) / s) > 3) System.out.print(" [" + i + "]=" + f(x[i]));
        System.out.println();
        double[] q = x.clone(); java.util.Arrays.sort(q);
        double q1 = q[q.length / 4], q3 = q[3 * q.length / 4], iqr = q3 - q1;
        System.out.println("Q1=" + f(q1) + " Q3=" + f(q3) + " IQR=" + f(iqr));
        System.out.print("iqr flags:");
        for (int i = 0; i < x.length; i++)
            if (x[i] < q1 - 1.5 * iqr || x[i] > q3 + 1.5 * iqr) System.out.print(" [" + i + "]=" + f(x[i]));
        System.out.println();
    }
    static String f(double v) { return String.format("%.3f", v); }
}
```

```
mean=11.864 sd=5.739
z>3 flags: [7]=30.000
Q1=9.900 Q3=10.300 IQR=0.400
iqr flags: [7]=30.000
```

Both rules isolate index 7; the drifted mean (11.864 vs bulk ~10.0) shows masking in miniature.

## 2. PrCurve - threshold sweep trades P for R

```java
public class PrCurve {
    public static void main(String[] args) {
        double[] scores = {0.95, 0.9, 0.8, 0.6, 0.55, 0.4, 0.3, 0.2, 0.1, 0.05};
        int[] label = {1, 1, 0, 1, 0, 0, 1, 0, 0, 0};
        for (double t : new double[]{0.8, 0.5, 0.2}) {
            int tp = 0, fp = 0, fn = 0;
            for (int i = 0; i < scores.length; i++) {
                boolean flag = scores[i] >= t;
                if (flag && label[i] == 1) tp++;
                else if (flag) fp++;
                else if (label[i] == 1) fn++;
            }
            double prec = tp + fp == 0 ? 1 : (double) tp / (tp + fp);
            double rec = (double) tp / (tp + fn);
            System.out.println("t=" + t + " P=" + f(prec) + " R=" + f(rec));
        }
    }
    static String f(double v) { return String.format("%.3f", v); }
}
```

```
t=0.8 P=0.667 R=0.500
t=0.5 P=0.600 R=0.750
t=0.2 P=0.500 R=1.000
```

Lower thresholds lift recall to perfect while precision sags; costs pick the operating row.

## 3. BaseRate - the fallacy, quantified

```java
public class BaseRate {
    public static void main(String[] args) {
        double prev = 0.001, sens = 0.99, fpr = 0.01;
        double ppv = sens * prev / (sens * prev + fpr * (1 - prev));
        System.out.println("PPV=" + String.format("%.4f", ppv));
        System.out.println("per 100k: true=" + (int) (sens * prev * 100000)
            + " false=" + (int) (fpr * (1 - prev) * 100000));
    }
}
```

```
PPV=0.0902
per 100k: true=99 false=999
```

A 99%-sensitive detector is still wrong nine times in ten at 1-in-1000 prevalence: cut fpr first.
