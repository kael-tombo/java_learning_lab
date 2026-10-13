# Final Field Semantics — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Finals Publish Safely Through a Race (the §17.5 Guarantee)

```java
public class FinalViaRace {
    static class Holder {
        final int a;
        final String s;
        final int[] arr;
        Holder(int a, String s) {
            this.a = a;
            this.s = s;
            this.arr = new int[]{a, a + 1};   // finals-of-finals (transitive)
        }
    }

    static Holder shared;   // PLAIN reference: racy publication, deliberately

    public static void main(String[] args) throws Exception {
        int iters = 3000;
        boolean[] ok = {true};
        for (int i = 1; i <= iters; i++) {
            shared = null;
            final int v = i;
            Thread writer = new Thread(() -> { shared = new Holder(v, "n" + v); });
            Thread reader = new Thread(() -> {
                Holder h;
                while ((h = shared) == null) Thread.onSpinWait();
                if (h.a != v || !h.s.equals("n" + v)
                        || h.arr[0] != v || h.arr[1] != v + 1) ok[0] = false;
            });
            writer.start();
            reader.start();
            writer.join(5000);
            reader.join(5000);
            if (writer.isAlive() || reader.isAlive()) { ok[0] = false; break; }
        }
        System.out.println("rounds = " + iters);
        System.out.println("all finals (incl. transitive array) exact, every round: " + ok[0]);
    }
}
```

Expected output:
```
rounds = 3000
all finals (incl. transitive array) exact, every round: true
```

The reference races (plain static, no edge) — yet `a`, `s`, and both array
elements are exact all 3000 rounds. The freeze at constructor end orders
the field stores before any post-construction read through *any* chain
(mc/dc) — guaranteed by JLS §17.5 on every JVM, not luck on this one.

## 2. Records: The Same Guarantee in Modern Dress

```java
record Config(String host, int port, java.util.List<String> tags) { }

public class RecordViaRace {
    static Config shared;   // plain reference again

    public static void main(String[] args) throws Exception {
        int iters = 3000;
        boolean[] ok = {true};
        for (int i = 1; i <= iters; i++) {
            shared = null;
            final int v = i;
            Thread writer = new Thread(() -> {
                shared = new Config("h" + v, v, java.util.List.of("a", "b"));
            });
            Thread reader = new Thread(() -> {
                Config c;
                while ((c = shared) == null) Thread.onSpinWait();
                if (!c.host().equals("h" + v) || c.port() != v
                        || c.tags().size() != 2 || !"a".equals(c.tags().get(0))) ok[0] = false;
            });
            writer.start();
            reader.start();
            writer.join(5000);
            reader.join(5000);
        }
        System.out.println("record rounds = " + iters);
        System.out.println("record components exact under racy publication: " + ok[0]);
    }
}
```

Expected output:
```
record rounds = 3000
record components exact under racy publication: true
```

Record components are final fields — a published record is a snapshot safe
by construction. (Caveat from THEORY, restated in code: the `tags()` *list
contents* are safe here only because `List.of` is itself immutable;
a record holding a mutable `ArrayList` would publish the *reference*
safely and leave the *contents* racy.)

## 3. This-Escape Voids It (Deterministically Shown)

```java
public class ThisEscape {
    static Leaky published;

    static class Leaky {
        final int x;
        Leaky(int v, long delayMs) {
            published = this;                    // escape BEFORE the store
            try { Thread.sleep(delayMs); }       // hold the window open
            catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            this.x = v;                          // freeze comes too late
        }
    }

    public static void main(String[] args) throws Exception {
        Thread writer = new Thread(() -> { new Leaky(42, 300); });
        writer.start();
        while (published == null) Thread.onSpinWait();
        int observed = published.x;              // read inside the window
        writer.join(5000);
        System.out.println("observed during construction window = " + observed);
        System.out.println("default value observed (freeze not yet run): " + (observed == 0));
        System.out.println("final value after construction = " + published.x);
    }
}
```

Expected output:
```
observed during construction window = 0
default value observed (freeze not yet run): true
final value after construction = 42
```

The 300 ms sleep wedges the construction window open so the read provably
lands inside it — no timing luck. `final` promised nothing here because the
freeze (constructor end) postdates the publication. Constructors must store
first, publish last — or never publish at all.

## 4. Mutable Control: Passes Here, Guaranteed Nowhere

```java
public class MutableControl {
    static class Mutable {
        int a;
        String s;
        Mutable(int a, String s) { this.a = a; this.s = s; }
    }

    static Mutable shared;

    public static void main(String[] args) throws Exception {
        int iters = 3000, bad = 0;
        for (int i = 1; i <= iters; i++) {
            shared = null;
            final int v = i;
            Thread writer = new Thread(() -> { shared = new Mutable(v, "n" + v); });
            final boolean[] roundOk = {true};
            Thread reader = new Thread(() -> {
                Mutable m;
                while ((m = shared) == null) Thread.onSpinWait();
                if (m.a != v || !("n" + v).equals(m.s)) roundOk[0] = false;
            });
            writer.start();
            reader.start();
            writer.join(5000);
            reader.join(5000);
            if (!roundOk[0]) bad++;
        }
        System.out.println("stale rounds = " + bad + "/" + iters);
        System.out.println("passes on x86 (StoreStore + coherence, NOT guaranteed): " + (bad == 0));
        System.out.println("verdict is still 'data race' — contrast snippet 1's guarantee: true");
    }
}
```

Expected output:
```
stale rounds = 0/3000
passes on x86 (StoreStore + coherence, NOT guaranteed): true
verdict is still 'data race' — contrast snippet 1's guarantee: true
```

Same shape as snippet 1 minus `final` — passes 3000 rounds here by TSO
accident, guaranteed nowhere (a reordering JIT or weak-memory CPU may show
stale `a`/`s` any day). Snippet 1's identical run is a *theorem*; this
one's is *weather*. Ship the theorem.

## 5. Strings: The Most-Used Finals Guarantee in the JDK

```java
public class StringSharing {
    static String shared;   // plain reference; String carries its own safety

    public static void main(String[] args) throws Exception {
        String payload = "payload-" + "x".repeat(100);
        int iters = 3000;
        boolean[] ok = {true};
        for (int i = 0; i < iters; i++) {
            shared = null;
            Thread writer = new Thread(() -> { shared = payload; });
            Thread reader = new Thread(() -> {
                String s;
                while ((s = shared) == null) Thread.onSpinWait();
                if (!s.equals(payload) || s.length() != payload.length()
                        || s.charAt(0) != 'p' || s.charAt(s.length() - 1) != 'x') ok[0] = false;
            });
            writer.start();
            reader.start();
            writer.join(5000);
            reader.join(5000);
        }
        System.out.println("string rounds = " + iters);
        System.out.println("shared String always intact (final value+coder): " + ok[0]);
    }
}
```

Expected output:
```
string rounds = 3000
shared String always intact (final value+coder): true
```

`String`'s `value` byte array and `coder` are final — every unsynchronized
`String` handoff in every Java program leans on §17.5, including the array
*contents* via the transitive rule. No locks on the read path exist
because none are needed: immutability + freeze is the synchronization.

## Common Pitfalls Encountered Here

- **Publishing `this` from constructors** — listeners, thread starts,
  static installs before field stores void the freeze (snippet 3).
- **Reading "final means immutable"** — final *references* publish safely;
  mutable *referents* stay racy (snippet 2's `List.of` caveat).
- **Trusting the mutable twin** — passes on x86, guaranteed nowhere
  (snippet 4 vs snippet 1: weather vs theorem).
- **Reflective/`Unsafe` writes to finals post-construction** — outside the
  model entirely; observed behavior is version-dependent accident.
- **Deserialization-shaped allocation** — allocate-then-fill skips the
  constructor freeze path; frameworks supply their own fences, and custom
  `readObject` code must reason about them explicitly.
