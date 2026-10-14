# Code Deep Dive - Data Pipelines (JDK only)

Compile with `javac --release 21 -encoding UTF-8`; outputs below are observed.

## 1. PipeIdem - replay-safe keyed sink

```java
import java.util.*;
public class PipeIdem {
    public static void main(String[] args) {
        Map<String, Double> sink = new LinkedHashMap<>();
        List<String[]> batch1 = List.of(new String[][]{{"o1", "9.5"}, {"o2", "4.0"}});
        List<String[]> batch2 = List.of(new String[][]{{"o1", "9.5"}, {"o2", "4.0"}, {"o3", "7.25"}});
        for (String[] r : batch1) sink.merge(r[0], Double.parseDouble(r[1]), (a, b) -> b);
        System.out.println("after batch1: " + sink);
        for (String[] r : batch2) sink.merge(r[0], Double.parseDouble(r[1]), (a, b) -> b);
        System.out.println("after replay+new: " + sink + " rows=" + sink.size());
    }
}
```

```
after batch1: {o1=9.5, o2=4.0}
after replay+new: {o1=9.5, o2=4.0, o3=7.25} rows=3
```

Replaying o1/o2 overwrote identical values (no-op) while o3 landed:
Map.merge by key is the fixed point m(m(S,b),b) = m(S,b) in code.

## 2. PipeQuality - counts, nulls, drift

```java
public class PipeQuality {
    public static void main(String[] args) {
        String[][] rows = {{"1", "9.5"}, {"2", ""}, {"3", "7.25"}, {"4", ""}, {"5", "12.0"}, {"6", "8.75"}};
        int nulls = 0; double sum = 0; int n = 0;
        for (String[] r : rows) {
            if (r[1].isBlank()) nulls++;
            else { sum += Double.parseDouble(r[1]); n++; }
        }
        double mean = sum / n, ref = 9.0;
        System.out.println("rows=" + rows.length + " nulls=" + nulls
            + " nullRate=" + String.format("%.3f", (double) nulls / rows.length));
        System.out.println("mean=" + String.format("%.3f", mean)
            + " driftVsRef=" + String.format("%.3f", Math.abs(mean - ref)));
    }
}
```

```
rows=6 nulls=2 nullRate=0.333
mean=9.375 driftVsRef=0.375
```

Three exact-arithmetic checks that gate every batch: counts, null
share, and drift against reference. Thresholds are policy; these
numbers are fact.

## 3. PipeSchema - compat verdicts plus tumbling windows

```java
import java.util.*;
public class PipeSchema {
    public static void main(String[] args) {
        Set<String> v1 = new LinkedHashSet<>(List.of("id", "amount"));
        Map<String, String> v2add = Map.of("id", "int", "amount", "double", "currency", "string");
        Map<String, String> v2break = Map.of("id", "int", "amount", "string");
        System.out.println("additive field currency: "
            + (v2add.keySet().containsAll(v1) ? "COMPATIBLE" : "BREAKING"));
        System.out.println("type change amount double->string: "
            + ("double".equals(v2break.get("amount")) ? "COMPATIBLE" : "BREAKING"));
        List<Double> stream = List.of(1.0, 5.0, 3.0, 8.0, 2.0);
        int w = 3;
        for (int i = 0; i + w <= stream.size(); i++)
            System.out.println("window[" + i + "] avg="
                + String.format("%.3f", stream.subList(i, i + w).stream().mapToDouble(d -> d).average().orElseThrow()));
    }
}
```

```
additive field currency: COMPATIBLE
type change amount double->string: BREAKING
window[0] avg=3.000
window[1] avg=5.333
window[2] avg=4.333
```

Subset-with-types decides compatibility mechanically; the windows are
plain means over slices - streaming's simplest correct building block.
