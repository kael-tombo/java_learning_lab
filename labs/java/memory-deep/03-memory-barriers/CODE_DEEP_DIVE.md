# Memory Barriers — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23, x86-64; absolute costs
are platform-relative, ratios and verdicts are the claims), no dependencies.
Timing snippets compare *within one JVM* (warm both paths, then measure)
so machine drift can't confound the ordering.

## 1. The Fence Tax: Plain vs Volatile Stores

```java
import java.util.concurrent.atomic.AtomicIntegerArray;

public class WriteFenceCost {
    public static void main(String[] args) {
        int n = 20_000_000, mask = 1023;
        int[] plain = new int[1024];
        AtomicIntegerArray vol = new AtomicIntegerArray(1024);
        // warmup both paths
        for (int i = 0; i < 2_000_000; i++) { plain[i & mask] = i; vol.set(i & mask, i); }

        long t0 = System.nanoTime();
        for (int i = 0; i < n; i++) plain[i & mask] = i;
        double plainNs = (System.nanoTime() - t0) / (double) n;

        t0 = System.nanoTime();
        for (int i = 0; i < n; i++) vol.set(i & mask, i);
        double volNs = (System.nanoTime() - t0) / (double) n;

        System.out.println("plain store ns = " + String.format("%.2f", plainNs));
        System.out.println("volatile store ns = " + String.format("%.2f", volNs));
        System.out.println("fence costs (volatile > 3x plain): " + (volNs > plainNs * 3));
    }
}
```

Expected output (absolutes vary — elided):
```
...
fence costs (volatile > 3x plain): true
```

Indexed stores defeat JIT elimination (distinct slots each iteration), so
both numbers are honest memory traffic: ~1 ns plain vs ~10 ns volatile
here — the StoreLoad fence costs roughly an order of magnitude, every
store, unconditionally. (First-run JVMs show wider spreads until frequency
scaling settles; the in-JVM warmup absorbs it.)

## 2. Reads Are (Nearly) Free: The x86 Asymmetry

```java
import java.util.concurrent.atomic.AtomicIntegerArray;

public class ReadCheap {
    public static void main(String[] args) {
        int n = 20_000_000, mask = 1023;
        int[] plain = new int[1024];
        AtomicIntegerArray vol = new AtomicIntegerArray(1024);
        for (int i = 0; i < 2_000_000; i++) { plain[i & mask] = i; vol.set(i & mask, i); }
        int sink = 0;

        long t0 = System.nanoTime();
        for (int i = 0; i < n; i++) sink += plain[i & mask];
        double plainNs = (System.nanoTime() - t0) / (double) n;

        t0 = System.nanoTime();
        for (int i = 0; i < n; i++) sink += vol.get(i & mask);
        double volNs = (System.nanoTime() - t0) / (double) n;
        plain[0] = sink;

        System.out.println("plain read ns = " + String.format("%.2f", plainNs));
        System.out.println("volatile read ns = " + String.format("%.2f", volNs));
        System.out.println("acquire nearly free (volatile < 5x plain): "
                + (volNs < Math.max(plainNs, 0.2) * 5));
    }
}
```

Expected output (absolutes vary — elided):
```
...
acquire nearly free (volatile < 5x plain): true
```

Acquire on TSO needs no fence instruction — the compiler barrier is the
whole implementation, so reads land within noise of plain (~1.2 vs ~1.0 ns
warmed here). The barrier tax is *directional*: writes pay, reads don't.
(ARM64 charges more for both — same taxonomy, different price list.)

## 3. Release Costs Plain: lazySet vs Volatile Set

```java
import java.util.concurrent.atomic.AtomicIntegerArray;

public class ReleaseCheaper {
    public static void main(String[] args) {
        int n = 20_000_000, mask = 1023;
        AtomicIntegerArray aia = new AtomicIntegerArray(1024);
        for (int i = 0; i < 2_000_000; i++) { aia.set(i & mask, i); aia.lazySet(i & mask, i); }

        long t0 = System.nanoTime();
        for (int i = 0; i < n; i++) aia.set(i & mask, i);
        double volNs = (System.nanoTime() - t0) / (double) n;

        t0 = System.nanoTime();
        for (int i = 0; i < n; i++) aia.lazySet(i & mask, i);
        double relNs = (System.nanoTime() - t0) / (double) n;

        System.out.println("volatile set ns = " + String.format("%.2f", volNs));
        System.out.println("release set ns = " + String.format("%.2f", relNs));
        System.out.println("release avoids the StoreLoad fence (>3x cheaper): "
                + (volNs > Math.max(relNs, 0.2) * 3));
    }
}
```

Expected output (absolutes vary — elided):
```
...
release avoids the StoreLoad fence (>3x cheaper): true
```

`lazySet` (release) on x86 is a compiler-barrier-only store (~1.3 ns,
rock-stable across runs); `set` (volatile) adds the hardware fence
(~10 ns). Same visibility eventual-guarantee class, different ordering
contract, ~8x price gap — the economic argument for release/acquire
chains (lab 02, snippet 4) wherever total order isn't needed.

## 4. Accidental Correctness: Plain Message-Passing Passes (Means Nothing)

```java
public class AccidentalCorrect {
    static int data;
    static boolean flag;

    public static void main(String[] args) throws Exception {
        int iters = 2000, bad = 0;
        for (int i = 1; i <= iters; i++) {
            data = 0;
            flag = false;
            Thread w = new Thread(() -> { data = 42; flag = true; });
            final int[] seen = {-1};
            Thread r = new Thread(() -> {
                while (!flag) Thread.onSpinWait();
                seen[0] = data;
            });
            w.start();
            r.start();
            w.join(5000);
            r.join(5000);
            if (seen[0] != 42) bad++;
        }
        System.out.println("stale reads = " + bad + "/" + iters);
        System.out.println("passes on x86 (StoreStore preserved + coherence): " + (bad == 0));
        System.out.println("verdict is STILL 'data race' (JMM promises nothing): true");
    }
}
```

Expected output:
```
stale reads = 0/2000
passes on x86 (StoreStore preserved + coherence): true
verdict is STILL 'data race' (JMM promises nothing): true
```

StoreStore order is free on TSO and coherence delivers the values, so this
passes thousands of runs — and guarantees nothing. The compiler *may*
hoist the `data` read above the spin (legal: no edge forbids it); ARM may
reorder the stores. Green here, red elsewhere, undefined per spec: the
textbook accident. (Compare lab 02's Dekker, which fails loudly on the
same machine — StoreLoad is the escaped pair, StoreStore the preserved
one.)

## 5. Release/Acquire Still Races Dekker (Chains Aren't Total Orders)

```java
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

public class RaDekker {
    static int x, y;
    static final VarHandle X, Y;

    static {
        try {
            X = MethodHandles.lookup().findStaticVarHandle(RaDekker.class, "x", int.class);
            Y = MethodHandles.lookup().findStaticVarHandle(RaDekker.class, "y", int.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    static volatile boolean go;
    static volatile boolean done1, done2;
    static int r1slot, r2slot;

    public static void main(String[] args) throws Exception {
        int iters = 20_000, bad = 0;
        Thread t1 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                X.setRelease(1);
                r1slot = (int) Y.getAcquire();
                done1 = true;
                while (go) Thread.onSpinWait();
                done1 = false;
            }
        });
        Thread t2 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                while (!go) Thread.onSpinWait();
                Y.setRelease(1);
                r2slot = (int) X.getAcquire();
                done2 = true;
                while (go) Thread.onSpinWait();
                done2 = false;
            }
        });
        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();
        for (int i = 0; i < iters; i++) {
            x = 0; y = 0;
            done1 = false; done2 = false;
            go = true;
            while (!done1 || !done2) Thread.onSpinWait();
            if (r1slot == 0 && r2slot == 0) bad++;
            go = false;
            while (done1 || done2) Thread.onSpinWait();
        }
        t1.interrupt();
        t2.interrupt();
        System.out.println("forbidden (0,0) under release/acquire = " + bad + "/" + iters);
        System.out.println("pairwise chains don't compose (anomalies persist): "
                + (bad > iters / 100));
    }
}
```

Expected output (count varies — elided):
```
...
pairwise chains don't compose (anomalies persist): true
```

Measured 61–90% anomaly rate — release/acquire Dekker races like plain
Dekker (on x86 both compile to bare MOVs). Each pair chains correctly
(my-release → your-acquire), but the two chains never form the total
order Dekker demands. Only StoreLoad on both sides (full volatile) or
exclusion closes it. Ordering modes are not a ladder where "stronger
sounding" suffices — match the mode to the shape.

## Common Pitfalls Encountered Here

- **Quoting absolutes across machines** — ratios and verdicts port;
  nanoseconds don't (every timing claim here is a ratio for exactly this
  reason).
- **Trusting accidental green** — plain message-passing passes on x86 and
  means nothing (snippet 4 vs lab 02 snippet 1: preserved pair vs escaped
  pair).
- **Release/acquire as SC-lite** — pairwise chains, no total order
  (snippet 5's 61–90% anomaly rate).
- **Assuming reads cost like writes** — directional tax: writes fence,
  reads (nearly) don't, on TSO (snippets 1–2).
- **Paying volatile for release jobs** — `lazySet` where chains suffice
  saves ~8x per store (snippet 3).
- **Forgetting warmup inside the measurement** — first-run frequency
  scaling dwarfs fence effects; warm both paths in-JVM (snippets 1–3).
