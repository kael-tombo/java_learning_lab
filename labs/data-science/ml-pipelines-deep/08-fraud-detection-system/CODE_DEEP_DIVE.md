# Fraud Detection System - Code Deep Dive

Three single-class programs (plain JDK 21+, no libraries). Compile and run:

```sh
javac --release 21 -encoding UTF-8 A*.java B*.java C*.java
```

## A08Metrics.java

```java
public class A08Metrics {
    public static void main(String[] args) {
        int tp = 80, fp = 120, fn = 20;
        double prec = (double) tp / (tp + fp);
        double rec = (double) tp / (tp + fn);
        double f1 = 2 * prec * rec / (prec + rec);
        System.out.printf("tp=%d fp=%d fn=%d precision=%.3f recall=%.3f f1=%.3f%n", tp, fp, fn, prec, rec, f1);
        System.out.println("read: accuracy hides misses on rare classes; report precision+recall");
    }
}
```

Observed output:

```
tp=80 fp=120 fn=20 precision=0.400 recall=0.800 f1=0.533
read: accuracy hides misses on rare classes; report precision+recall
```

## B08Cost.java

```java
public class B08Cost {
    public static void main(String[] args) {
        double costFN = 10.0, costFP = 1.0; // illustrative ratio, not a real loss figure
        int[][] points = {{95, 300}, {80, 120}, {60, 40}}; // {tp, fp} per threshold, fn = 100-tp
        for (int[] p : points) {
            int fn = 100 - p[0];
            double cost = fn * costFN + p[1] * costFP;
            System.out.printf("tp=%d fp=%d fn=%d expected_cost=%.0f%n", p[0], p[1], fn, cost);
        }
        System.out.println("read: when misses cost more than reviews, lower threshold wins");
    }
}
```

Observed output:

```
tp=95 fp=300 fn=5 expected_cost=350
tp=80 fp=120 fn=20 expected_cost=320
tp=60 fp=40 fn=40 expected_cost=440
read: when misses cost more than reviews, lower threshold wins
```

## C08Lag.java

```java
public class C08Lag {
    public static void main(String[] args) {
        int[] labeledByDay = {5, 18, 42, 70, 88, 96, 100}; // cumulative of 100 positives
        for (int d = 0; d < labeledByDay.length; d++)
            System.out.printf("day+%d labeled=%d%%%n", d, labeledByDay[d]);
        System.out.println("read: evaluate on mature labels only; fresh data understates fraud");
    }
}
```

Observed output:

```
day+0 labeled=5%
day+1 labeled=18%
day+2 labeled=42%
day+3 labeled=70%
day+4 labeled=88%
day+5 labeled=96%
day+6 labeled=100%
read: evaluate on mature labels only; fresh data understates fraud
```

## What each snippet shows
- A08Metrics: core measurement for fraud detection system.
- B08Cost: central tradeoff or bookkeeping computation.
- C08Lag: decision rule used before acting on a result.
