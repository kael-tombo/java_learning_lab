# Exploratory Analysis - Code Deep Dive (JDK-only; outputs observed)

## 1. Grouped means with sanity checks

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class EdaGroupByC {
    public static void main(String[] args) {
        String[] region = {"north", "south", "north", "south", "north", "south"};
        double[] spend = {10, 20, 30, 40, 50, 60};
        Map<String, double[]> acc = new LinkedHashMap<>();
        double total = 0;
        for (int i = 0; i < region.length; i++) {
            double[] a = acc.computeIfAbsent(region[i], k -> new double[2]);
            a[0] += spend[i]; a[1]++; total += spend[i];
        }
        for (Map.Entry<String, double[]> e : acc.entrySet()) {
            double[] v = e.getValue();
            System.out.println(e.getKey() + ": n=" + (int) v[1] + " mean=" + (v[0] / v[1]));
        }
        System.out.println("overall mean=" + (total / spend.length));
        System.out.println("check: group n sums to " + spend.length);
    }
}
```

```text
north: n=3 mean=30.0
south: n=3 mean=40.0
overall mean=35.0
check: group n sums to 6
```

## 2. Simpson reversal in counts

```java
public class EdaSimpsonC {
    static double pct(int k, int n) {
        return 100.0 * k / n;
    }
    public static void main(String[] args) {
        int aT = 81, aTn = 90, aC = 234, aCn = 270;
        int bT = 192, bTn = 263, bC = 55, bCn = 80;
        System.out.println("wardA treat=" + pct(aT, aTn) + "% control=" + pct(aC, aCn) + "%");
        System.out.println("wardB treat=" + pct(bT, bTn) + "% control=" + pct(bC, bCn) + "%");
        System.out.println("pooled treat=" + (100.0 * (aT + bT) / (aTn + bTn)) + "% control=" + (100.0 * (aC + bC) / (aCn + bCn)) + "%");
    }
}
```

```text
wardA treat=90.0% control=86.66666666666667%
wardB treat=73.00380228136882% control=68.75%
pooled treat=77.33711048158641% control=82.57142857142857%
```

## 3. Correlation trio, one routine

```java
public class EdaCorrMatrixC {
    static double corr(double[] a, double[] b) {
        int n = a.length;
        double ma = 0, mb = 0, sxy = 0, sxx = 0, syy = 0;
        for (double v : a) ma += v;
        for (double v : b) mb += v;
        ma /= n; mb /= n;
        for (int i = 0; i < n; i++) {
            double da = a[i] - ma, db = b[i] - mb;
            sxy += da * db; sxx += da * da; syy += db * db;
        }
        return sxy / Math.sqrt(sxx * syy);
    }
    public static void main(String[] args) {
        double[] age = {25, 32, 47, 51, 62}, spend = {200, 350, 500, 550, 700}, visits = {8, 6, 4, 3, 2};
        System.out.println("r(age,spend)=" + corr(age, spend));
        System.out.println("r(age,visits)=" + corr(age, visits));
        System.out.println("r(spend,visits)=" + corr(spend, visits));
        System.out.println("note: strong r does not imply causation");
    }
}
```

```text
r(age,spend)=0.9932316263764919
r(age,visits)=-0.9853034458841585
r(spend,visits)=-0.990942442678138
note: strong r does not imply causation
```
