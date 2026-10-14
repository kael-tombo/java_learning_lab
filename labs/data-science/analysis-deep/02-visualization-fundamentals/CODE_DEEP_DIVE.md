# Visualization Fundamentals - Code Deep Dive (JDK-only; outputs observed)

## 1. Text histogram, width 2 from 0

```java
public class VizHistogramC {
    public static void main(String[] args) {
        double[] x = {1, 2, 2, 3, 3, 3, 4, 4, 5, 9};
        int[] counts = new int[5]; // edges 0,2,4,6,8,10
        for (double v : x) {
            int b = (int) (v / 2);
            counts[Math.min(Math.max(b, 0), 4)]++;
        }
        for (int b = 0; b < 5; b++) {
            StringBuilder bar = new StringBuilder();
            for (int i = 0; i < counts[b]; i++) bar.append('#');
            System.out.println("[" + (b * 2.0) + "," + (b * 2.0 + 2) + "): " + counts[b] + " " + bar);
        }
    }
}
```

```text
[0.0,2.0): 1 #
[2.0,4.0): 5 #####
[4.0,6.0): 3 ###
[6.0,8.0): 0
[8.0,10.0): 1 #
```

Counts sum to 10; the empty [6,8) bin is printed, preserving the gap.

## 2. Category bars with denominators

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class VizCategoryBarsC {
    public static void main(String[] args) {
        String[] sales = {"books", "games", "books", "food", "games", "games", "food", "books"};
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (String s : sales) counts.merge(s, 1, Integer::sum);
        for (Map.Entry<String, Integer> e : counts.entrySet()) {
            System.out.println(e.getKey() + ": " + e.getValue() + "/" + sales.length + " " + "#".repeat(e.getValue()));
        }
    }
}
```

```text
books: 3/8 ###
games: 3/8 ###
food: 2/8 ##
```

First-seen label order is kept; counts ride beside fractions so n stays
visible.

## 3. Binned means tame overplotting

```java
import java.util.Map;
import java.util.TreeMap;

public class VizBinnedMeansC {
    public static void main(String[] args) {
        double[] xs = {1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6};
        double[] ys = {2, 4, 3, 5, 4, 6, 5, 7, 8, 6, 7, 9};
        Map<Integer, double[]> cells = new TreeMap<>();
        for (int i = 0; i < xs.length; i++) {
            double[] acc = cells.computeIfAbsent((int) (xs[i] / 2), k -> new double[2]);
            acc[0] += ys[i];
            acc[1]++;
        }
        for (Map.Entry<Integer, double[]> e : cells.entrySet()) {
            int b = e.getKey();
            System.out.println("x in [" + (b * 2) + "," + (b * 2 + 2) + "): n=" + (int) e.getValue()[1] + " meanY=" + (e.getValue()[0] / e.getValue()[1]));
        }
    }
}
```

```text
x in [0,2): n=2 meanY=3.0
x in [2,4): n=4 meanY=4.5
x in [4,6): n=4 meanY=6.5
x in [6,8): n=2 meanY=8.0
```

Cells print left to right; the monotone 3.0 to 8.0 trend is what a
saturated scatter blob would hide.
