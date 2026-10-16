# MLOps Orchestration - Code Deep Dive

Three single-class programs (plain JDK 21+, no libraries). Compile and run:

```sh
javac --release 21 -encoding UTF-8 A*.java B*.java C*.java
```

## A07Backoff.java

```java
public class A07Backoff {
    public static void main(String[] args) {
        long baseMs = 1000, capMs = 30000;
        for (int attempt = 0; attempt < 6; attempt++) {
            long delay = Math.min(capMs, baseMs * (1L << attempt));
            System.out.printf("attempt=%d delay_ms=%d%n", attempt, delay);
        }
        System.out.println("read: cap bounds worst-case wait; add jitter to avoid herd retry");
    }
}
```

Observed output:

```
attempt=0 delay_ms=1000
attempt=1 delay_ms=2000
attempt=2 delay_ms=4000
attempt=3 delay_ms=8000
attempt=4 delay_ms=16000
attempt=5 delay_ms=30000
read: cap bounds worst-case wait; add jitter to avoid herd retry
```

## B07Lineage.java

```java
public class B07Lineage {
    public static void main(String[] args) {
        String data = "dataset:transactions-v14 rows=50000 hash=a3f9";
        String code = "git:abc1234 train.py";
        String params = "lr=0.01 depth=6 seed=7";
        String pointer = data + " | " + code + " | " + params;
        int fp = pointer.hashCode();
        System.out.println("lineage=" + pointer);
        System.out.printf("fingerprint=%d (rerun same pointer -> same id)%n", fp);
        boolean reproducible = fp == (data + " | " + code + " | " + params).hashCode();
        System.out.println("reproducible=" + reproducible);
    }
}
```

Observed output:

```
lineage=dataset:transactions-v14 rows=50000 hash=a3f9 | git:abc1234 train.py | lr=0.01 depth=6 seed=7
fingerprint=1047179432 (rerun same pointer -> same id)
reproducible=true
```

## C07Gate.java

```java
public class C07Gate {
    public static void main(String[] args) {
        double baseline = 0.82, candidate = 0.845, minLift = 0.01, maxDrop = 0.005;
        double[] slices = {0.851, 0.838, 0.802};
        boolean overall = candidate - baseline >= minLift;
        boolean noRegress = true;
        for (int i = 0; i < slices.length; i++) {
            boolean ok = slices[i] >= baseline - maxDrop;
            noRegress &= ok;
            System.out.printf("slice%d=%.3f ok=%b%n", i, slices[i], ok);
        }
        System.out.printf("overall lift=%.3f pass=%b promote=%b%n",
            candidate - baseline, overall, overall && noRegress);
    }
}
```

Observed output:

```
slice0=0.851 ok=true
slice1=0.838 ok=true
slice2=0.802 ok=false
overall lift=0.025 pass=true promote=false
```

## What each snippet shows
- A07Backoff: core measurement for mlops orchestration.
- B07Lineage: central tradeoff or bookkeeping computation.
- C07Gate: decision rule used before acting on a result.
