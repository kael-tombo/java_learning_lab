# Code Deep Dive — JVM Memory Internals (memory-deep)

Six runnable snippets that make HotSpot's memory areas observable using only the JDK: management beans, `-Xlog` unified logging, `-XX` flags and `jcmd`. Every number in an "Observed output" block was produced by running the snippet; none is typed in by hand.

How to use this file: each snippet is a complete single-file program. Save it as `<ClassName>.java`, compile with `javac --release 21 -proc:none <ClassName>.java`, then run the command shown under it. Every snippet targets Java 21 without preview features and uses only the JDK. The outputs below were produced on JDK 23.0.1 (HotSpot 64-Bit Server VM, Windows) with `--release 21`. Memory figures depend on the JVM version, collector, heap flags and the machine, so treat each block as one representative run: exact byte counts for object sizes are stable, while GC timings, usage figures and recursion depths are not.

## Snippet 1: heap vs stack

Each thread owns a stack that holds one frame per active method call: local primitives, references and return state. Objects and arrays always live in the heap, which all threads share and the garbage collector manages. The stack size is fixed per thread (`-Xss`) and overflowing it throws `StackOverflowError`; the heap has a ceiling (`-Xmx`) and exhausting it throws `OutOfMemoryError: Java heap space`. The snippet has three modes: count frames until the stack overflows, retain 1 MiB arrays until the heap is full, and measure how many heap bytes a loop of local `int`s allocates compared with one `new int[1000]`.

```java
import java.lang.management.ManagementFactory;
import java.util.ArrayList;
import java.util.List;

public class HeapVsStack {
    static int depth;
    static volatile Object sink;

    static void recurse() {
        depth++;
        recurse();
    }

    static void stackDemo() {
        depth = 0;
        try {
            recurse();
        } catch (StackOverflowError e) {
            System.out.println("StackOverflowError after " + depth + " frames");
        }
    }

    static void heapDemo() {
        List<byte[]> retained = new ArrayList<>();
        try {
            while (true) {
                retained.add(new byte[1024 * 1024]);
            }
        } catch (OutOfMemoryError e) {
            int mebibytes = retained.size();
            retained.clear();
            System.out.println("OutOfMemoryError after retaining " + mebibytes + " MiB: " + e.getMessage());
        }
    }

    static void allocDemo() {
        com.sun.management.ThreadMXBean mx = (com.sun.management.ThreadMXBean) ManagementFactory.getThreadMXBean();
        long id = Thread.currentThread().threadId();
        mx.getThreadAllocatedBytes(id);                    // warm-up call

        long t0 = mx.getThreadAllocatedBytes(id);
        int sum = 0;
        for (int i = 0; i < 1000; i++) {
            sum += i;                                      // locals live in the stack frame
        }
        long t1 = mx.getThreadAllocatedBytes(id);
        int[] array = new int[1000];                       // an object: allocated on the heap
        sink = array;
        long t2 = mx.getThreadAllocatedBytes(id);

        System.out.println("sum = " + sum);
        System.out.println("heap bytes allocated by the loop over local ints: " + (t1 - t0));
        System.out.println("heap bytes allocated by new int[1000]           : " + (t2 - t1));
    }

    public static void main(String[] args) {
        String mode = args.length > 0 ? args[0] : "alloc";
        switch (mode) {
            case "stack" -> stackDemo();
            case "heap" -> heapDemo();
            case "alloc" -> allocDemo();
            default -> System.out.println("usage: HeapVsStack stack|heap|alloc");
        }
    }
}
```

Run: `java HeapVsStack alloc`

Observed output:
```text
sum = 499500
heap bytes allocated by the loop over local ints: 0
heap bytes allocated by new int[1000]           : 4016
```

Run: `java -Xss256k HeapVsStack stack`

Observed output (256 KiB stack):
```text
StackOverflowError after 3848 frames
```

Run: `java -Xss1m HeapVsStack stack`

Observed output (1 MiB stack):
```text
StackOverflowError after 23390 frames
```

Run: `java -Xss1m HeapVsStack stack`

Observed output (the same command run a second time, to show the depth is not fixed):
```text
StackOverflowError after 35639 frames
```

Run: `java -Xmx32m HeapVsStack heap`

Observed output (32 MiB heap ceiling):
```text
OutOfMemoryError after retaining 15 MiB: Java heap space
```

**Pitfall:** the depth at which `StackOverflowError` strikes is not a constant of the program. With `-Xss256k` the recursion stopped after 3848 frames, and the same `-Xss1m` command stopped after 23390 frames in one run and 35639 in the next, so code that recurses 30,000 deep can pass on one start and fail on another (JIT-compiled and interpreted frames differ in size; the JVM version and the frame size of the method matter too). The heap run shows the same lack of slack: with `-Xmx32m` the program died with `Java heap space` after retaining only 15 MiB, because the ceiling covers the whole heap, including young-generation space and collector headroom, not just room for your live data. Bound recursion depth explicitly or switch to an explicit stack, and size `-Xmx` from a measured live set plus headroom.

## Snippet 2: eden/survivor/old gen

Generational collectors split the heap by object age because most objects die young. New objects are allocated in eden; a young collection copies survivors into a survivor space and increments their age; objects that reach the tenuring threshold (or do not fit in the survivor space) are promoted to the old generation, which is collected less often. Pool names depend on the collector: the serial collector reports `Eden Space`, `Survivor Space` and `Tenured Gen`, while G1 (the default) reports `G1 Eden Space`, `G1 Survivor Space` and `G1 Old Gen`. The snippet prints each heap pool's usage through `MemoryPoolMXBean` after phases of short-lived garbage and after a small set of objects has lived through several collections.

```java
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryPoolMXBean;
import java.lang.management.MemoryType;
import java.util.ArrayList;
import java.util.List;

public class Generations {
    static final List<byte[]> longLived = new ArrayList<>();
    static volatile Object sink;

    static void printHeapPools(String label) {
        System.out.println("-- " + label);
        for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans()) {
            if (pool.getType() == MemoryType.HEAP) {
                System.out.printf("   %-20s used = %6d KiB%n", pool.getName(), pool.getUsage().getUsed() / 1024);
            }
        }
    }

    static void churn(int chunks) {
        for (int i = 0; i < chunks; i++) {
            sink = new byte[100 * 1024];                   // short-lived: unreachable right after the next iteration
        }
    }

    public static void main(String[] args) {
        printHeapPools("start");

        churn(600);                                        // about 60 MiB of garbage
        printHeapPools("after 60 MiB of short-lived garbage");

        for (int i = 0; i < 20; i++) {
            longLived.add(new byte[100 * 1024]);           // 2000 KiB that stays reachable
        }
        churn(1200);                                       // enough allocation for several young collections
        printHeapPools("after 2000 KiB of long-lived data and 120 MiB more garbage");

        for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
            System.out.println("collector " + gc.getName() + ": " + gc.getCollectionCount() + " collections");
        }
        System.out.println("long-lived data still reachable: " + longLived.size() * 100 + " KiB");
    }
}
```

Run: `java -XX:+UseSerialGC -Xmx64m -Xmn32m -XX:MaxTenuringThreshold=1 Generations`

Observed output (serial collector, 32 MiB young generation, objects promoted after surviving one collection):
```text
-- start
   Tenured Gen          used =      0 KiB
   Eden Space           used =   3674 KiB
   Survivor Space       used =      0 KiB
-- after 60 MiB of short-lived garbage
   Tenured Gen          used =   1084 KiB
   Eden Space           used =  11645 KiB
   Survivor Space       used =    100 KiB
-- after 2000 KiB of long-lived data and 120 MiB more garbage
   Tenured Gen          used =   3084 KiB
   Eden Space           used =   2722 KiB
   Survivor Space       used =    100 KiB
collector Copy: 7 collections
collector MarkSweepCompact: 0 collections
long-lived data still reachable: 2000 KiB
```

Run: `java -XX:+UseSerialGC -Xmx64m -Xmn32m -XX:MaxTenuringThreshold=1 -Xlog:gc Generations`

Observed output with `-Xlog:gc` added, so each collection is logged between the program's own lines:
```text
[0.033s][info][gc] Using Serial
-- start
   Tenured Gen          used =      0 KiB
   Eden Space           used =   3674 KiB
   Survivor Space       used =      0 KiB
[0.204s][info][gc] GC(0) Pause Young (Allocation Failure) 25M->1M(60M) 3.225ms
[0.212s][info][gc] GC(1) Pause Young (Allocation Failure) 26M->1M(60M) 2.675ms
-- after 60 MiB of short-lived garbage
   Tenured Gen          used =   1084 KiB
   Eden Space           used =  11645 KiB
   Survivor Space       used =    100 KiB
[0.219s][info][gc] GC(2) Pause Young (Allocation Failure) 26M->3M(60M) 1.220ms
[0.225s][info][gc] GC(3) Pause Young (Allocation Failure) 28M->3M(60M) 1.719ms
[0.229s][info][gc] GC(4) Pause Young (Allocation Failure) 28M->3M(60M) 0.184ms
[0.234s][info][gc] GC(5) Pause Young (Allocation Failure) 28M->3M(60M) 0.179ms
[0.238s][info][gc] GC(6) Pause Young (Allocation Failure) 28M->3M(60M) 0.223ms
-- after 2000 KiB of long-lived data and 120 MiB more garbage
   Tenured Gen          used =   3084 KiB
   Eden Space           used =   2722 KiB
   Survivor Space       used =    100 KiB
collector Copy: 7 collections
collector MarkSweepCompact: 0 collections
long-lived data still reachable: 2000 KiB
```

Run: `java -Xmx64m Generations`

Observed output with the default collector (G1 on this machine):
```text
-- start
   G1 Eden Space        used =   2048 KiB
   G1 Old Gen           used =      0 KiB
   G1 Survivor Space    used =      0 KiB
-- after 60 MiB of short-lived garbage
   G1 Eden Space        used =  11264 KiB
   G1 Old Gen           used =      0 KiB
   G1 Survivor Space    used =   1261 KiB
-- after 2000 KiB of long-lived data and 120 MiB more garbage
   G1 Eden Space        used =  30720 KiB
   G1 Old Gen           used =   1120 KiB
   G1 Survivor Space    used =   2248 KiB
collector G1 Young Generation: 5 collections
collector G1 Concurrent GC: 0 collections
collector G1 Old Generation: 0 collections
long-lived data still reachable: 2000 KiB
```

**Pitfall:** pool figures are not "your" data and do not transfer between collectors. Under the serial collector `Tenured Gen` already held 1084 KiB after the first phase, before the program had retained anything, because startup objects were promoted too; only the delta (1084 to 3084 KiB) matches the 2000 KiB the program kept. Under G1 the same program split those 2000 KiB across `G1 Old Gen` (1120 KiB) and `G1 Survivor Space` (2248 KiB), so an alert on "old gen used" sees very different numbers for identical behaviour. Read pool usage as a sample at an arbitrary instant (Eden showed 11645 KiB right after a phase that had allocated 60 MiB, because collections had already reset it), and compare deltas under the exact collector flags you deploy with.

## Snippet 3: metaspace vs permgen

Class metadata (method bytecode, constant pools, field layouts) lives in native memory called metaspace, not on the Java heap. Metaspace replaced the permanent generation in JDK 8 (JEP 122); it grows on demand, is bounded only by `-XX:MaxMetaspaceSize` (unlimited by default), and a class's metadata is freed only when its defining class loader becomes unreachable and is collected. The snippet defines the same class bytes in thousands of fresh class loaders, each producing a distinct `Class` and its own metadata, and prints the `Metaspace` and `Compressed Class Space` pool usage.

```java
import java.io.IOException;
import java.io.InputStream;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryPoolMXBean;
import java.util.ArrayList;
import java.util.List;

public class MetaspaceDemo {
    static class IsolatedLoader extends ClassLoader {
        IsolatedLoader() {
            super(null);                                   // parent = bootstrap: nothing is shared with other loaders
        }

        Class<?> define(byte[] bytes) {
            return defineClass(null, bytes, 0, bytes.length);
        }
    }

    static long usedKiB(String poolName) {
        for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans()) {
            if (pool.getName().equals(poolName)) {
                return pool.getUsage().getUsed() / 1024;
            }
        }
        return -1;
    }

    static void report(String label) {
        System.out.println(label + ": Metaspace=" + usedKiB("Metaspace") + " KiB, Compressed Class Space="
                + usedKiB("Compressed Class Space") + " KiB");
    }

    public static void main(String[] args) throws IOException {
        int count = Integer.parseInt(args[0]);
        boolean retain = args[1].equals("retain");

        byte[] bytes;
        try (InputStream in = MetaspaceDemo.class.getResourceAsStream("Payload.class")) {
            bytes = in.readAllBytes();
        }
        System.out.println("class file size: " + bytes.length + " bytes");
        report("before");

        List<Class<?>> kept = new ArrayList<>();
        int defined = 0;
        try {
            for (int i = 0; i < count; i++) {
                Class<?> c = new IsolatedLoader().define(bytes);
                defined++;
                if (retain) {
                    kept.add(c);                           // keeps the class, and through it the loader, reachable
                }
            }
            System.out.println("defined " + defined + " classes, retain=" + retain);
        } catch (OutOfMemoryError e) {
            kept.clear();                                  // drop the classes first: even printing needs metaspace
            System.out.println("OutOfMemoryError after " + defined + " classes: " + e.getMessage());
        }
        report("after the loop");

        kept.clear();
        System.gc();
        report("after clearing references and System.gc()");
    }
}

class Payload {
    private long a, b, c, d;
    private String name = "payload";

    long sum() { return a + b + c + d; }
    void set(long v) { a = v; b = v * 2; c = v * 3; d = v * 4; }
    String describe() { return name + ":" + sum(); }
    static int twice(int x) { return x * 2; }
}
```

Run: `java MetaspaceDemo 5000 retain`

Observed output (5000 classes, all retained):
```text
class file size: 1139 bytes
before: Metaspace=733 KiB, Compressed Class Space=64 KiB
defined 5000 classes, retain=true
after the loop: Metaspace=11943 KiB, Compressed Class Space=2777 KiB
after clearing references and System.gc(): Metaspace=891 KiB, Compressed Class Space=81 KiB
```

Run: `java MetaspaceDemo 5000 release`

Observed output (5000 classes, references dropped as we go):
```text
class file size: 1139 bytes
before: Metaspace=747 KiB, Compressed Class Space=64 KiB
defined 5000 classes, retain=false
after the loop: Metaspace=11965 KiB, Compressed Class Space=2777 KiB
after clearing references and System.gc(): Metaspace=913 KiB, Compressed Class Space=81 KiB
```

Run: `java -XX:MaxMetaspaceSize=16m MetaspaceDemo 100000 retain`

Observed output (metaspace capped at 16 MiB):
```text
class file size: 1139 bytes
before: Metaspace=746 KiB, Compressed Class Space=64 KiB
OutOfMemoryError after 2584 classes: Metaspace
after the loop: Metaspace=860 KiB, Compressed Class Space=72 KiB
after clearing references and System.gc(): Metaspace=862 KiB, Compressed Class Space=72 KiB
```

Run: `java -XX:MaxPermSize=64m -version`

The pre-JDK-8 flag for the permanent generation no longer exists:
```text
Unrecognized VM option 'MaxPermSize=64m'
Error: Could not create the Java Virtual Machine.
Error: A fatal exception has occurred. Program will exit.
```

**Pitfall:** dropping references does not free metaspace until a collection runs. In the `release` run no loaded class was reachable, yet metaspace stood at 11965 KiB after the loop, about the same as the 11943 KiB of the `retain` run; only `System.gc()` brought it down to 913 KiB. The dangerous case is a class-loader leak (a redeployed web application whose old loader stays reachable through a static field or a `ThreadLocal`): with `-XX:MaxMetaspaceSize=16m` the process failed with `OutOfMemoryError: Metaspace` after 2584 classes, a heap dump would not show the cause because the memory is native, and even the code that handles the error needs metaspace to load its own classes (the snippet clears the list before printing for that reason). There is no PermGen left to tune: JDK 23 refuses `-XX:MaxPermSize` at startup.

## Snippet 4: object header & alignment

Every heap object starts with a header: a mark word (identity hash, GC age, lock state) and a class pointer. With compressed class pointers (the default on 64-bit HotSpot) that is 8 + 4 = 12 bytes, without them 8 + 8 = 16 bytes, and arrays add a 4-byte length after the header. Instances are padded so each object's size is a multiple of 8 bytes (`-XX:ObjectAlignmentInBytes`), and fields are packed into the gaps the header leaves. Compact object headers (JEP 450 experimental in JDK 24, JEP 519 product feature in JDK 25 via `-XX:+UseCompactObjectHeaders`, planned as the default by JEP 534 in JDK 27) merge the class pointer into the mark word and shrink the header from 96 or 128 bits to 64 bits, i.e. 4 to 8 bytes saved per object. The JDK-only measurement below asks the JVM how many bytes the current thread allocated around a loop of `new` expressions.

JOL (Java Object Layout) prints the exact field offsets and padding of a class. This is the typical use:

```java not-compiled
// Requires org.openjdk.jol:jol-core; not compiled in this repo.
import org.openjdk.jol.info.ClassLayout;

public class JolLayout {
    static class IntThenLong {
        int a;
        long b;
    }

    public static void main(String[] args) {
        System.out.println(ClassLayout.parseClass(IntThenLong.class).toPrintable());
        System.out.println(ClassLayout.parseInstance(new byte[1]).toPrintable());
    }
}
```

The JDK-only version, which was compiled and run:

```java
import java.lang.management.ManagementFactory;

public class ObjectSizes {
    static class Empty { }
    static class OneInt { int a; }
    static class OneLong { long a; }
    static class IntThenLong { int a; long b; }
    static class ThreeInts { int a, b, c; }
    static class OneRef { Object ref; }

    interface Maker {
        Object make();
    }

    static volatile Object sink;
    static final com.sun.management.ThreadMXBean MX =
            (com.sun.management.ThreadMXBean) ManagementFactory.getThreadMXBean();

    static long bytesPerObject(Maker maker) {
        final int n = 10_000;
        for (int i = 0; i < n; i++) {
            sink = maker.make();                           // warm-up: class initialization and JIT
        }
        long id = Thread.currentThread().threadId();
        long before = MX.getThreadAllocatedBytes(id);
        for (int i = 0; i < n; i++) {
            sink = maker.make();
        }
        long after = MX.getThreadAllocatedBytes(id);
        return Math.round((double) (after - before) / n);
    }

    static void row(String name, Maker maker) {
        System.out.printf("%-14s %3d bytes%n", name, bytesPerObject(maker));
    }

    public static void main(String[] args) {
        row("Object", Object::new);
        row("Empty", Empty::new);
        row("OneInt", OneInt::new);
        row("OneLong", OneLong::new);
        row("IntThenLong", IntThenLong::new);
        row("ThreeInts", ThreeInts::new);
        row("OneRef", OneRef::new);
        row("byte[0]", () -> new byte[0]);
        row("byte[1]", () -> new byte[1]);
        row("byte[8]", () -> new byte[8]);
        row("byte[9]", () -> new byte[9]);
        row("int[3]", () -> new int[3]);
    }
}
```

Run: `java ObjectSizes`

Observed output (defaults: compressed class pointers, 12-byte header):
```text
Object          16 bytes
Empty           16 bytes
OneInt          16 bytes
OneLong         24 bytes
IntThenLong     24 bytes
ThreeInts       24 bytes
OneRef          16 bytes
byte[0]         16 bytes
byte[1]         24 bytes
byte[8]         24 bytes
byte[9]         32 bytes
int[3]          32 bytes
```

Run: `java -XX:-UseCompressedClassPointers ObjectSizes`

Observed output with compressed class pointers off (16-byte header):
```text
Object          16 bytes
Empty           16 bytes
OneInt          24 bytes
OneLong         24 bytes
IntThenLong     32 bytes
ThreeInts       32 bytes
OneRef          24 bytes
byte[0]         24 bytes
byte[1]         24 bytes
byte[8]         32 bytes
byte[9]         32 bytes
int[3]          32 bytes
```

Run: `java -XX:+UseCompactObjectHeaders ObjectSizes`

JDK 23 does not contain compact object headers, so the flag cannot be tried here:
```text
Unrecognized VM option 'UseCompactObjectHeaders'
Error: Could not create the Java Virtual Machine.
Error: A fatal exception has occurred. Program will exit.
```

**Pitfall:** an object's size is not the sum of its fields. `OneInt` holds 4 bytes of data and costs 16, and `byte[0]`, which holds nothing, costs 16. The sizes also move with VM flags: turning compressed class pointers off made `OneInt` 24, `IntThenLong` 32 and `byte[0]` 24 bytes, while `Object` stayed at 16 (8 + 8). `getThreadAllocatedBytes` measures shallow size only, so it says nothing about what a collection or a `String` retains. Compact headers help unevenly: by arithmetic on the 8-byte header (computed, not measured, since JDK 23 lacks the flag), `OneLong` would need 8 + 8 = 16 bytes instead of the measured 24, while `OneInt` would need 8 + 4 = 12, which rounds back up to 16 and saves nothing, so estimate the benefit per class layout rather than assuming 4 bytes per object.

## Snippet 5: GC roots & reachability

The collector keeps an object if a chain of strong references leads to it from a GC root: local variables and operand slots of live stack frames, static fields of loaded classes, live threads, JNI handles. Everything else, including cycles of objects that point at each other, is garbage. A `WeakReference` does not keep its referent alive, so `ref.get() == null` after a collection tells you the referent was unreachable. The snippet tests five situations and calls `System.gc()` as a request, which HotSpot honors by default and ignores under `-XX:+DisableExplicitGC`.

```java
import java.lang.ref.Reference;
import java.lang.ref.WeakReference;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

public class Reachability {
    static final Map<String, Object> CACHE = new HashMap<>();

    static class Node {
        Node other;
        final byte[] padding = new byte[1024];
    }

    static boolean collectedAfterGc(WeakReference<?> ref) {
        for (int attempt = 0; attempt < 3 && ref.get() != null; attempt++) {
            System.gc();
        }
        return ref.get() == null;
    }

    static Thread startWorker(CountDownLatch release, WeakReference<?>[] observed) {
        Object payload = new Object();
        observed[0] = new WeakReference<>(payload);
        Thread worker = new Thread(() -> {
            try {
                release.await();
            } catch (InterruptedException e) {
                return;
            }
            System.out.println("   worker resumed, payload is " + payload.getClass().getName());
        });
        worker.start();
        return worker;                                     // main keeps no reference to payload itself
    }

    public static void main(String[] args) throws Exception {
        Object local = new Object();
        WeakReference<Object> w1 = new WeakReference<>(local);
        System.out.println("1 held by a local variable      : collected=" + collectedAfterGc(w1));
        Reference.reachabilityFence(local);                // keeps the local live up to this point
        local = null;
        System.out.println("  after local = null             : collected=" + collectedAfterGc(w1));

        Object cached = new Object();
        CACHE.put("k", cached);
        WeakReference<Object> w2 = new WeakReference<>(cached);
        cached = null;
        System.out.println("2 reachable via a static map     : collected=" + collectedAfterGc(w2));
        CACHE.remove("k");
        System.out.println("  after CACHE.remove(\"k\")        : collected=" + collectedAfterGc(w2));

        Node a = new Node();
        Node b = new Node();
        a.other = b;
        b.other = a;
        WeakReference<Node> wa = new WeakReference<>(a);
        WeakReference<Node> wb = new WeakReference<>(b);
        a = null;
        b = null;
        System.out.println("3 unreachable cycle a <-> b      : a collected=" + collectedAfterGc(wa)
                + ", b collected=" + collectedAfterGc(wb));

        CountDownLatch release = new CountDownLatch(1);
        WeakReference<?>[] observed = new WeakReference<?>[1];
        Thread worker = startWorker(release, observed);
        System.out.println("4 captured by a blocked thread   : collected=" + collectedAfterGc(observed[0]));
        release.countDown();
        worker.join();
        worker = null;
        System.out.println("  after the thread has finished  : collected=" + collectedAfterGc(observed[0]));
    }
}
```

Run: `java -XX:+UseSerialGC -Xlog:gc Reachability`

Observed output (`-Xlog:gc` lines show each requested collection):
```text
[0.031s][info][gc] Using Serial
[0.111s][info][gc] GC(0) Pause Full (System.gc()) 5M->0M(247M) 2.159ms
[0.113s][info][gc] GC(1) Pause Full (System.gc()) 0M->0M(247M) 1.156ms
[0.114s][info][gc] GC(2) Pause Full (System.gc()) 0M->0M(247M) 1.084ms
1 held by a local variable      : collected=false
[0.140s][info][gc] GC(3) Pause Full (System.gc()) 3M->0M(247M) 2.112ms
  after local = null             : collected=true
[0.142s][info][gc] GC(4) Pause Full (System.gc()) 3M->0M(247M) 1.584ms
[0.144s][info][gc] GC(5) Pause Full (System.gc()) 0M->0M(247M) 1.540ms
[0.145s][info][gc] GC(6) Pause Full (System.gc()) 0M->0M(247M) 1.439ms
2 reachable via a static map     : collected=false
[0.147s][info][gc] GC(7) Pause Full (System.gc()) 3M->0M(247M) 1.488ms
  after CACHE.remove("k")        : collected=true
[0.150s][info][gc] GC(8) Pause Full (System.gc()) 4M->0M(247M) 1.467ms
3 unreachable cycle a <-> b      : a collected=true, b collected=true
[0.166s][info][gc] GC(9) Pause Full (System.gc()) 4M->0M(247M) 2.113ms
[0.173s][info][gc] GC(10) Pause Full (System.gc()) 1M->0M(247M) 2.116ms
[0.175s][info][gc] GC(11) Pause Full (System.gc()) 0M->0M(247M) 2.098ms
4 captured by a blocked thread   : collected=false
   worker resumed, payload is java.lang.Object
[0.179s][info][gc] GC(12) Pause Full (System.gc()) 4M->0M(247M) 1.825ms
  after the thread has finished  : collected=true
```

Run: `java -XX:+DisableExplicitGC Reachability`

Observed output with `System.gc()` turned into a no-op:
```text
1 held by a local variable      : collected=false
  after local = null             : collected=false
2 reachable via a static map     : collected=false
  after CACHE.remove("k")        : collected=false
3 unreachable cycle a <-> b      : a collected=false, b collected=false
4 captured by a blocked thread   : collected=false
   worker resumed, payload is java.lang.Object
  after the thread has finished  : collected=false
```

**Pitfall:** reachability, not scope or intent, decides what survives, and `System.gc()` is only a request. The entry in the static `CACHE` kept its object alive even though the local variable had been set to `null` (`collected=false` until `CACHE.remove("k")`), which is the shape of most real heap leaks. With `-XX:+DisableExplicitGC` every line printed `collected=false`, including the unreachable cycle, so a test that asserts on `WeakReference.get() == null` after `System.gc()` passes or fails depending on JVM flags, and production services sometimes set that flag. Use `-Xlog:gc` (as above, `Pause Full (System.gc())`) to confirm a collection actually ran before concluding anything about leaks.

## Snippet 6: NMT & JOL

Native Memory Tracking (NMT) is HotSpot's accounting of memory the JVM itself allocates outside the Java heap: metaspace, thread stacks, code cache, GC data structures and `malloc` calls made through the JVM, including direct `ByteBuffer`s. It is switched on at startup with `-XX:NativeMemoryTracking=summary|detail` and queried with `jcmd <pid> VM.native_memory summary`. The snippet launches `jcmd` against its own process id before and after allocating a 64 MiB direct buffer and starting 20 threads, and prints the Java Heap, Class, Thread and Other categories plus the total each time.

```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.util.List;

public class NativeMemory {
    static List<String> jcmd(String... command) throws IOException, InterruptedException {
        String exe = System.getProperty("os.name").startsWith("Windows") ? "jcmd.exe" : "jcmd";
        String[] full = new String[command.length + 2];
        full[0] = Path.of(System.getProperty("java.home"), "bin", exe).toString();
        full[1] = Long.toString(ProcessHandle.current().pid());
        System.arraycopy(command, 0, full, 2, command.length);

        Process process = new ProcessBuilder(full).redirectErrorStream(true).start();
        List<String> lines;
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            lines = reader.lines().toList();
        }
        process.waitFor();
        return lines;
    }

    static void show(String label) throws IOException, InterruptedException {
        System.out.println("-- " + label);
        for (String line : jcmd("VM.native_memory", "summary")) {
            String t = line.trim();
            if (t.startsWith("Total:") || t.startsWith("Native memory tracking")
                    || line.matches("^\\s*-\\s+(Java Heap|Class|Thread|Other)\\b.*")) {
                System.out.println("   " + t.replaceAll("\\s{2,}", " "));
            }
        }
    }

    public static void main(String[] args) throws Exception {
        show("baseline");

        ByteBuffer direct = ByteBuffer.allocateDirect(64 * 1024 * 1024);
        System.out.println("allocated a direct buffer of " + direct.capacity() / (1024 * 1024) + " MiB");
        show("after allocateDirect(64 MiB)");

        List<Thread> sleepers = new java.util.ArrayList<>();
        for (int i = 0; i < 20; i++) {
            Thread t = new Thread(() -> {
                try {
                    Thread.sleep(60_000);
                } catch (InterruptedException ignored) {
                    // exits when interrupted
                }
            });
            t.setDaemon(true);
            t.start();
            sleepers.add(t);
        }
        show("after starting 20 threads");
        sleepers.forEach(Thread::interrupt);
    }
}
```

Run: `java -XX:NativeMemoryTracking=summary NativeMemory`

Observed output (NMT enabled; figures are one representative run):
```text
-- baseline
   Total: reserved=5727084KB, committed=344296KB
   - Java Heap (reserved=4194304KB, committed=262144KB)
   - Class (reserved=1048677KB, committed=229KB)
   - Thread (reserved=18481KB, committed=753KB)
allocated a direct buffer of 64 MiB
-- after allocateDirect(64 MiB)
   Total: reserved=5793937KB, committed=411221KB
   - Java Heap (reserved=4194304KB, committed=262144KB)
   - Class (reserved=1048685KB, committed=237KB)
   - Thread (reserved=18481KB, committed=761KB)
   - Other (reserved=65536KB, committed=65536KB)
-- after starting 20 threads
   Total: reserved=5814547KB, committed=412731KB
   - Java Heap (reserved=4194304KB, committed=262144KB)
   - Class (reserved=1048691KB, committed=243KB)
   - Thread (reserved=39022KB, committed=2138KB)
   - Other (reserved=65536KB, committed=65536KB)
```

Run: `java NativeMemory`

Observed output without the startup flag:
```text
-- baseline
   Native memory tracking is not enabled
allocated a direct buffer of 64 MiB
-- after allocateDirect(64 MiB)
   Native memory tracking is not enabled
-- after starting 20 threads
   Native memory tracking is not enabled
```

JOL complements NMT inside the Java heap: it computes the retained size of a whole object graph. This is the typical use:

```java not-compiled
// Requires org.openjdk.jol:jol-core; not compiled in this repo.
import java.util.ArrayList;
import java.util.List;
import org.openjdk.jol.info.GraphLayout;
import org.openjdk.jol.vm.VM;

public class JolFootprint {
    public static void main(String[] args) {
        System.out.println(VM.current().details());             // reports header size, oop size, alignment in use
        List<String> list = new ArrayList<>(List.of("a", "b", "c"));
        System.out.println(GraphLayout.parseInstance(list).toFootprint());
    }
}
```

**Pitfall:** NMT only works if it was enabled when the JVM started: the run without `-XX:NativeMemoryTracking=summary` answered `Native memory tracking is not enabled` to all three queries, and it cannot be switched on later in the same process. With it on, read the numbers carefully: the 64 MiB direct buffer appeared as `Other` at 65536 KB committed while `Java Heap` stayed at 262144 KB, so heap metrics and `-Xmx` never see it. Twenty new threads raised `Thread` by 20541 KB reserved but only 1377 KB committed, and the `Total: reserved=` figure (about 5.5 GB here, mostly the heap and class-space reservations) is address space, not resident memory, so use `committed` (and the OS view) when judging footprint.

## Pitfalls summary

| Topic | Concrete failure | How to observe it |
|---|---|---|
| heap vs stack | identical `-Xss1m` runs overflowed after 23390 and 35639 frames; OOM at 15 MiB retained under `-Xmx32m` | `-Xss`, `-Xmx`, `getThreadAllocatedBytes` |
| eden/survivor/old gen | the same 2000 KiB retained shows as 3084 KiB-1084 KiB (serial) or 1120 KiB old + 2248 KiB survivor (G1) | `-Xlog:gc`, `MemoryPoolMXBean` |
| metaspace vs permgen | no references left, still 11965 KiB until a GC; leaked loaders end in `OutOfMemoryError: Metaspace` | `-XX:MaxMetaspaceSize`, `Metaspace` pool |
| object header & alignment | 4-byte `OneInt` costs 16 B; `-XX:-UseCompressedClassPointers` makes it 24 B | `getThreadAllocatedBytes`, JOL |
| GC roots & reachability | static map entry keeps the object alive; `-XX:+DisableExplicitGC` makes `System.gc()` do nothing | `WeakReference`, `-Xlog:gc` |
| NMT & JOL | NMT must be enabled at startup; direct buffers show up as `Other`, not heap | `-XX:NativeMemoryTracking`, `jcmd VM.native_memory` |
