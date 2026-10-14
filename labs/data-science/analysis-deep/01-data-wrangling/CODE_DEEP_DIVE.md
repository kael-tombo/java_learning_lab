# Data Wrangling - Code Deep Dive (JDK-only; outputs observed)

## 1. Mean imputation (`{2, 4, NaN, 8, 10}`)

```java
import java.util.Arrays;

public class WrangleMeanImputeC {
    public static void main(String[] args) {
        double[] col = {2.0, 4.0, Double.NaN, 8.0, 10.0};
        int missing = 0;
        double sum = 0.0;
        for (double v : col) { if (Double.isNaN(v)) missing++; else sum += v; }
        double mean = sum / (col.length - missing);
        double[] filled = new double[col.length];
        for (int i = 0; i < col.length; i++) filled[i] = Double.isNaN(col[i]) ? mean : col[i];
        double[] obs = {2.0, 4.0, 8.0, 10.0};
        Arrays.sort(obs);
        System.out.println("n=" + col.length + " missing=" + missing + " observed=" + (col.length - missing));
        System.out.println("mean of observed=" + mean);
        System.out.println("imputed=" + Arrays.toString(filled));
        System.out.println("median of observed=" + ((obs[1] + obs[2]) / 2.0));
    }
}
```

```text
n=5 missing=1 observed=4
mean of observed=6.0
imputed=[2.0, 4.0, 6.0, 8.0, 10.0]
median of observed=6.0
```

Fill fits on observed cells only; `Double.isNaN` is mandatory since `==` never matches NaN.

## 2. Dedup with composite keys

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class WrangleDedupC {
    public static void main(String[] args) {
        String[][] rows = {{"c7", "2026-01-05"}, {"c7", "2026-01-05"}, {"c7", "2026-01-06"},
            {"c9", "2026-01-05"}, {"c9", "2026-01-05"}};
        Map<String, Integer> seen = new LinkedHashMap<>();
        for (String[] r : rows) seen.putIfAbsent(r[0] + "|" + r[1], 1);
        System.out.println("input rows=" + rows.length + " unique keys=" + seen.size());
        System.out.println("keys=" + seen.keySet());
        System.out.println("duplicates removed=" + (rows.length - seen.size()));
    }
}
```

```text
input rows=5 unique keys=3
keys=[c7|2026-01-05, c7|2026-01-06, c9|2026-01-05]
duplicates removed=2
```

## 3. Strict coercion with reject log

```java
public class WrangleCoercionC {
    public static void main(String[] args) {
        String[] raw = {"12", " 45 ", "3x", "", "7.5", "N/A", "-8"};
        int ok = 0, bad = 0;
        double sum = 0.0;
        for (String s : raw) {
            try {
                String t = s.trim();
                if (t.isEmpty()) throw new NumberFormatException("blank");
                if (t.equals("N/A")) throw new NumberFormatException("sentinel");
                sum += Double.parseDouble(t);
                ok++;
            } catch (NumberFormatException e) {
                bad++;
                System.out.println("reject [" + s + "] reason=" + e.getMessage());
            }
        }
        System.out.println("parsed=" + ok + " rejected=" + bad + " sum=" + sum);
    }
}
```

```text
reject [3x] reason=For input string: "3x"
reject [] reason=blank
reject [N/A] reason=sentinel
parsed=4 rejected=3 sum=56.5
```
