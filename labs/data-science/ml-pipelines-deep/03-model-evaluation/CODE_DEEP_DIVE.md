# Model Evaluation — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Datasets are small and fixed; every number is hand-checkable.

## 1. Confusion Matrix: Precision, Recall, F1 — and Accuracy's Lie

```java
public class ConfusionMetrics {
    public static void main(String[] args) {
        // A fraud screen: 1000 transactions, 20 frauds. Model flags 30, catches 15.
        int tp = 15, fp = 15, fn = 5, tn = 965;
        double precision = (double) tp / (tp + fp);
        double recall = (double) tp / (tp + fn);
        double f1 = 2 * precision * recall / (precision + recall);
        double accuracy = (double) (tp + tn) / (tp + fp + fn + tn);
        double dumbAccuracy = (double) (tn + fn) / (tp + fp + fn + tn); // always-"no"
        System.out.println("precision = " + precision);
        System.out.println("recall = " + recall);
        System.out.println("f1 = " + f1);
        System.out.println("accuracy = " + accuracy);
        System.out.println("always-no accuracy = " + dumbAccuracy + " (finds nothing)");
    }
}
```

Expected output:
```
precision = 0.5
recall = 0.75
f1 = 0.6
accuracy = 0.98
always-no accuracy = 0.97 (finds nothing)
```

## 2. F1 Punishes Lopsidedness (Harmonic, Not Arithmetic)

```java
public class F1Harmonic {
    static double f1(double p, double r) {
        return 2 * p * r / (p + r);
    }

    public static void main(String[] args) {
        System.out.println("P=1.0 R=0.1 -> F1 = " + f1(1.0, 0.1));
        System.out.println("P=0.5 R=0.5 -> F1 = " + f1(0.5, 0.5));
        System.out.println("P=0.9 R=0.9 -> F1 = " + f1(0.9, 0.9));
        System.out.println("harmonic <= arithmetic: "
                + (f1(1.0, 0.1) < (1.0 + 0.1) / 2));
    }
}
```

Expected output:
```
P=1.0 R=0.1 -> F1 = 0.18181818181818182
P=0.5 R=0.5 -> F1 = 0.5
P=0.9 R=0.9 -> F1 = 0.9
harmonic <= arithmetic: true
```

## 3. Log-Loss and Brier: Calibration Has a Price

```java
public class ScoringRules {
    static double logLoss(double[] p, int[] y) {
        double s = 0;
        for (int i = 0; i < p.length; i++) {
            double q = Math.min(Math.max(p[i], 1e-15), 1 - 1e-15);  // never exactly 0/1
            s += y[i] * Math.log(q) + (1 - y[i]) * Math.log(1 - q);
        }
        return -s / p.length;
    }

    static double brier(double[] p, int[] y) {
        double s = 0;
        for (int i = 0; i < p.length; i++) s += (p[i] - y[i]) * (p[i] - y[i]);
        return s / p.length;
    }

    public static void main(String[] args) {
        int[] y = {1, 0, 1, 1, 0};
        double[] confident = {0.99, 0.01, 0.99, 0.01, 0.5};  // one confident error
        double[] modest = {0.7, 0.3, 0.7, 0.7, 0.5};
        System.out.println("confident logloss = " + logLoss(confident, y));
        System.out.println("modest logloss = " + logLoss(modest, y));
        System.out.println("confident brier = " + brier(confident, y));
        System.out.println("modest brier = " + brier(modest, y));
        System.out.println("confident error costs more under both rules: "
                + (logLoss(confident, y) > logLoss(modest, y)
                && brier(confident, y) > brier(modest, y)));
    }
}
```

Expected output:
```
confident logloss = 1.065693674821708
modest logloss = 0.42396939126297506
confident brier = 0.24608
modest brier = 0.12200000000000003
confident error costs more under both rules: true
```
