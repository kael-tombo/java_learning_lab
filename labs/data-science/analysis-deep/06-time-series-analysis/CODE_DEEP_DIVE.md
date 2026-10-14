# Code Deep Dive - Time Series (JDK only)

Compile with `javac --release 21 -encoding UTF-8`, run with `java -cp . <Class>`. Outputs are observed, byte-for-byte.

## 1. TsDiff - differencing calms a trending series

```java
public class TsDiff {
    public static void main(String[] args) {
        double[] y = {4.0, 6.0, 9.0, 13.0, 18.0, 24.0};
        double[] d = new double[y.length - 1];
        for (int i = 1; i < y.length; i++) d[i - 1] = y[i] - y[i - 1];
        System.out.println("orig mean=" + fmt(mean(y)) + " var=" + fmt(var(y)));
        System.out.println("diff mean=" + fmt(mean(d)) + " var=" + fmt(var(d)));
        System.out.print("diffs:");
        for (double v : d) System.out.print(" " + fmt(v));
        System.out.println();
    }
    static double mean(double[] a) {
        double s = 0; for (double v : a) s += v; return s / a.length;
    }
    static double var(double[] a) {
        double m = mean(a), s = 0; for (double v : a) s += (v - m) * (v - m);
        return s / a.length;
    }
    static String fmt(double v) { return String.format("%.4f", v); }
}
```

```
orig mean=12.3333 var=48.2222
diff mean=4.0000 var=2.0000
diffs: 2.0000 3.0000 4.0000 5.0000 6.0000
```

Level variance 48.2 collapses after one difference: the d = 1 effect.

## 2. TsErrors - MAE/RMSE/MAPE plus naive baselines

```java
public class TsErrors {
    public static void main(String[] args) {
        double[] actual = {10.0, 12.0, 0.0, 14.0, 16.0};
        double[] pred = {11.0, 11.0, 2.0, 13.0, 18.0};
        double mae = 0, sq = 0, mape = 0; int n = 0;
        for (int i = 0; i < actual.length; i++) {
            double e = Math.abs(actual[i] - pred[i]);
            mae += e; sq += e * e;
            if (actual[i] != 0.0) { mape += e / Math.abs(actual[i]); n++; }
        }
        System.out.println("MAE=" + f(mae / actual.length) + " RMSE=" + f(Math.sqrt(sq / actual.length)));
        System.out.println("MAPE=" + f(mape / n * 100.0) + "% over n=" + n + " (1 zero skipped)");
        double[] s = {5.0, 7.0, 6.0, 8.0, 7.0, 9.0};
        System.out.println("naive=" + f(s[s.length - 1]) + " seasonal-naive(m=3)=" + f(s[s.length - 3]));
    }
    static String f(double v) { return String.format("%.4f", v); }
}
```

```
MAE=1.4000 RMSE=1.4832
MAPE=9.4940% over n=4 (1 zero skipped)
naive=9.0000 seasonal-naive(m=3)=8.0000
```

RMSE exceeds MAE as theory requires; the zero actual is excluded, not divided.

## 3. TsAcf - sample autocorrelation at lags 1..3

```java
public class TsAcf {
    public static void main(String[] args) {
        double[] y = {3.0, 5.0, 4.0, 6.0, 5.0, 7.0, 6.0, 8.0};
        double m = 0; for (double v : y) m += v; m /= y.length;
        double denom = 0; for (double v : y) denom += (v - m) * (v - m);
        for (int lag = 1; lag <= 3; lag++) {
            double num = 0;
            for (int t = lag; t < y.length; t++) num += (y[t] - m) * (y[t - lag] - m);
            System.out.println("ACF lag " + lag + " = " + String.format("%.4f", num / denom));
        }
    }
}
```

```
ACF lag 1 = 0.1250
ACF lag 2 = 0.4722
ACF lag 3 = -0.2361
```

Strong lag-2 with weak lag-1 fingerprints the series' zigzag shape.
