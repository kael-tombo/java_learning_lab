# Code Deep Dive - Causal Inference (JDK only)

Three single-class programs. Compile with
`javac --release 21 -encoding UTF-8`, run with `java -cp . <Class>`.
Outputs are observed, byte-for-byte.

## 1. Simpson - pooling reverses the verdict

```java
public class Simpson {
    public static void main(String[] args) {
        double aMild = 90.0 / 100, bMild = 190.0 / 200;
        double aSev = 10.0 / 100, bSev = 90.0 / 200;
        double aAll = 100.0 / 200, bAll = 280.0 / 400;
        System.out.println("mild: A=" + aMild + " B=" + bMild + " -> A worse");
        System.out.println("severe: A=" + aSev + " B=" + bSev + " -> A worse");
        System.out.println("pooled: A=" + aAll + " B=" + bAll + " -> A better (reversal)");
    }
}
```

Observed output:

```
mild: A=0.9 B=0.95 -> A worse
severe: A=0.1 B=0.45 -> A worse
pooled: A=0.5 B=0.7 -> A better (reversal)
```

Hospital B takes harder cases, so its pooled rate mixes case-mix with
skill. Within each severity stratum A is worse; pooled, A looks better.

## 2. DiD - the double difference

```java
public class DiD {
    public static void main(String[] args) {
        double treatPre = 40.0, treatPost = 55.0;
        double ctrlPre = 42.0, ctrlPost = 47.0;
        double did = (treatPost - treatPre) - (ctrlPost - ctrlPre);
        System.out.println("treat change=" + f(treatPost - treatPre));
        System.out.println("control change=" + f(ctrlPost - ctrlPre));
        System.out.println("DiD estimate=" + f(did));
    }
    static String f(double v) { return String.format("%.2f", v); }
}
```

Observed output:

```
treat change=15.00
control change=5.00
DiD estimate=10.00
```

The treated group gained 15, but 5 of that is shared trend (control
gained 5), leaving 10 - valid only under parallel trends.

## 3. Confound - adjustment removes most of the naive gap

```java
public class Confound {
    public static void main(String[] args) {
        double mildD = 32.0 / 40, mildN = 108.0 / 120;
        double sevD = 33.0 / 110, sevN = 6.0 / 30;
        double naiveD = 65.0 / 150, naiveN = 114.0 / 150;
        double adj = (mildD - mildN) * 160 / 300 + (sevD - sevN) * 140 / 300;
        System.out.println("naive diff=" + f(naiveD - naiveN) + " (looks strongly harmful)");
        System.out.println("mild diff=" + f(mildD - mildN) + " severe diff=" + f(sevD - sevN));
        System.out.println("adjusted diff=" + f(adj) + " (confounding exaggerated harm)");
    }
    static String f(double v) { return String.format("%.4f", v); }
}
```

Observed output:

```
naive diff=-0.3267 (looks strongly harmful)
mild diff=-0.1000 severe diff=0.1000
adjusted diff=-0.0067 (confounding exaggerated harm)
```

Severity drives both drug assignment and recovery, so the pooled gap is
almost pure selection bias; holding severity fixed leaves ~zero effect.
