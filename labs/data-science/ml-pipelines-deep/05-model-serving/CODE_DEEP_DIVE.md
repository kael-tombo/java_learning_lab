# Model Serving - Code Deep Dive

Three single-class programs (plain JDK 21+, no libraries). Compile and run:

```sh
javac --release 21 -encoding UTF-8 A*.java B*.java C*.java
```

## A05Latency.java

```java
import java.util.*;
public class A05Latency {
    static double percentile(double[] sorted, double p) {
        if (sorted.length == 0) throw new IllegalArgumentException("empty");
        double rank = p / 100.0 * (sorted.length - 1);
        int lo = (int) Math.floor(rank), hi = (int) Math.ceil(rank);
        if (lo == hi) return sorted[lo];
        return sorted[lo] + (sorted[hi] - sorted[lo]) * (rank - lo);
    }
    public static void main(String[] args) {
        double[] lat = {8, 12, 9, 25, 11, 10, 14, 9, 13, 120, 11, 10, 15, 9, 12};
        Arrays.sort(lat);
        System.out.printf("n=%d p50=%.1fms p99=%.1fms max=%.0fms%n",
            lat.length, percentile(lat, 50), percentile(lat, 99), lat[lat.length - 1]);
        System.out.println("read: p99 >> p50 means tail dominated; size timeouts from p99 not mean");
    }
}
```

Observed output:

```
n=15 p50=11.0ms p99=106.7ms max=120ms
read: p99 >> p50 means tail dominated; size timeouts from p99 not mean
```

## B05Batching.java

```java
public class B05Batching {
    public static void main(String[] args) {
        double overheadMs = 4.0, perItemMs = 1.5;
        System.out.println("batch size | latency_ms | items_per_sec");
        for (int b : new int[]{1, 4, 16, 64}) {
            double lat = overheadMs + b * perItemMs;
            double tput = 1000.0 * b / lat;
            System.out.printf("%10d | %10.1f | %13.1f%n", b, lat, tput);
        }
        System.out.println("read: bigger batch raises throughput but also latency");
    }
}
```

Observed output:

```
batch size | latency_ms | items_per_sec
         1 |        5.5 |         181.8
         4 |       10.0 |         400.0
        16 |       28.0 |         571.4
        64 |      100.0 |         640.0
read: bigger batch raises throughput but also latency
```

## C05Canary.java

```java
public class C05Canary {
    public static void main(String[] args) {
        int baseN = 2000, baseErr = 38, canN = 200, canErr = 6;
        double baseRate = (double) baseErr / baseN, canRate = (double) canErr / canN;
        double se = Math.sqrt(baseRate * (1 - baseRate) / baseN + canRate * (1 - canRate) / canN);
        double z = (canRate - baseRate) / se;
        System.out.printf("baseline=%.3f canary=%.3f diff=%+.4f se=%.4f z=%.2f%n",
            baseRate, canRate, canRate - baseRate, se, z);
        System.out.println("read: |z|<2 here, no signal; canary needs enough traffic before judging");
    }
}
```

Observed output:

```
baseline=0.019 canary=0.030 diff=+0.0110 se=0.0124 z=0.88
read: |z|<2 here, no signal; canary needs enough traffic before judging
```

## What each snippet shows
- A05Latency: core measurement for model serving.
- B05Batching: central tradeoff or bookkeeping computation.
- C05Canary: decision rule used before acting on a result.
