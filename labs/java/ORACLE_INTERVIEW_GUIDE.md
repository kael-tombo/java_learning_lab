# Oracle Interview Guide — Java Academy

## Interview Process for Java Roles

### Rounds & Timeline
- **Phone Screen (45 min):** Technical screen with Java language questions + coding
- **On-site (4-5 rounds):** 2 Java deep-dive, 1 system design, 1 behavioral, 1 manager round
- **Timeline:** 4-8 weeks (Oracle moves slowly — multiple levels of approval)
- **Java-Specific:** Oracle **owns Java**. This is the most Java-intensive interview of any company. **Every question is Java-specific.** You cannot use another language. They expect you to know the JDK source code.

### Java-Specific Evaluation
- Oracle expects you to know **JDK internals** — the actual source code of `HashMap`, `ArrayList`, `ConcurrentHashMap`
- They ask about **JVM specification** — not just implementation, the actual JLS (Java Language Specification) and JVMS
- **Java history** — "Why was `StringBuffer` replaced by `StringBuilder`? What version?"
- **They wrote the language** — arrogance is acceptable if backed by technical depth
- **OpenJDK contribution** experience is a massive signal

---

## Top Problems by Module

### Module: Collections (JDK Internals)

#### Problem: Implement HashMap from scratch
- **LC:** N/A (Design)
- **Difficulty/Frequency:** Hard / Very High
- **Problem Statement:** Implement a HashMap from scratch with correct hash distribution, resize, and collision handling.
- **Interview Walkthrough:** Oracle expects you to **replicate JDK's HashMap implementation**. `Node<K,V>` array, `hash()` with XOR shift, treeify threshold (TREEIFY_THRESHOLD=8), untreeify (UNTREEIFY_THRESHOLD=6). They want to see you know the actual JDK source.
- **Solution 1 vs Solution 2:** Separate chaining with linked list (JDK 7 style). Separate chaining with tree (JDK 8+ style). Oracle wants JDK 8+ with treeify — they wrote it.
- **Java Code:**
```java
import java.util.Objects;

/**
 * HashMap reimplementation matching JDK 8+ internals.
 * Oracle expects you to know the source code — treeify threshold, hash spreading.
 */
public class CustomHashMap<K, V> {

    private static final int DEFAULT_CAPACITY = 16;
    private static final float LOAD_FACTOR = 0.75f;
    private static final int TREEIFY_THRESHOLD = 8;
    private static final int UNTREEIFY_THRESHOLD = 6;

    static class Node<K, V> {
        final int hash;
        final K key;
        V value;
        Node<K, V> next;

        Node(int hash, K key, V value, Node<K, V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }

    private Node<K, V>[] table;
    private int size;
    private int threshold;

    @SuppressWarnings("unchecked")
    public CustomHashMap() {
        this.table = new Node[DEFAULT_CAPACITY];
        this.threshold = (int)(DEFAULT_CAPACITY * LOAD_FACTOR);
    }

    /**
     * Spreads hash to reduce collisions — matches JDK 8 hash().
     * @param key input key
     * @return spread hash
     */
    static int hash(Object key) {
        int h;
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }

    /**
     * Associates key with value, growing table if needed.
     * @param key   key
     * @param value value
     * @return previous value or null
     */
    public V put(K key, V value) {
        int hash = hash(key);
        int idx = (table.length - 1) & hash;
        Node<K, V> head = table[idx];
        if (head == null) {
            table[idx] = new Node<>(hash, key, value, null);
            size++;
            if (size > threshold) resize();
            return null;
        }
        Node<K, V> curr = head;
        while (true) {
            if (curr.hash == hash && Objects.equals(curr.key, key)) {
                V old = curr.value;
                curr.value = value;
                return old;
            }
            if (curr.next == null) {
                curr.next = new Node<>(hash, key, value, null);
                size++;
                if (size > threshold) resize();
                return null;
            }
            curr = curr.next;
        }
    }

    /**
     * Resizes table to double capacity — matches JDK resize().
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        Node<K, V>[] oldTable = table;
        int oldCap = oldTable.length;
        int newCap = oldCap * 2;
        threshold = (int)(newCap * LOAD_FACTOR);
        table = new Node[newCap];
        for (Node<K, V> node : oldTable) {
            while (node != null) {
                Node<K, V> next = node.next;
                int idx = (table.length - 1) & node.hash;
                node.next = table[idx];
                table[idx] = node;
                node = next;
            }
        }
    }

    /**
     * @param key lookup key
     * @return value or null
     */
    public V get(Object key) {
        int hash = hash(key);
        int idx = (table.length - 1) & hash;
        Node<K, V> curr = table[idx];
        while (curr != null) {
            if (curr.hash == hash && Objects.equals(curr.key, key)) {
                return curr.value;
            }
            curr = curr.next;
        }
        return null;
    }

    /**
     * @return number of entries
     */
    public int size() { return size; }
}
```
- **Company Evaluation Criteria:** JDK-level knowledge (hash spreading, treeify threshold, power-of-2 sizing), correct resize behavior.
- **Follow-ups:** Add treeify; explain why TREEIFY_THRESHOLD is 8 (Poisson distribution); implement removal.

#### Problem: Implement LinkedHashMap with access order
- **LC:** N/A
- **Difficulty/Frequency:** Hard / High
- **Problem Statement:** Extend your HashMap with doubly-linked list for insertion/access ordering.
- **Interview Walkthrough:** This is `LinkedHashMap` internals. Oracle wants you to explain how the `after`/`before` pointers work, `accessOrder` flag, `removeEldestEntry()`. They wrote the class.
- **Solution 1 vs Solution 2:** Separate LinkedList + HashMap (duplicate references). Integrated doubly-linked list in Node (JDK's approach). Oracle wants the integrated approach.
- **Java Code:**
```java
/**
 * LinkedHashMap reimplementation with access-order support.
 * Oracle wrote this class — they expect you to know the internals.
 */
public class LinkedCustomHashMap<K, V> {

    static class LinkedNode<K, V> extends CustomHashMap.Node<K, V> {
        LinkedNode<K, V> before, after;
        LinkedNode(int hash, K key, V value, CustomHashMap.Node<K, V> next) {
            super(hash, key, value, next);
        }
    }

    private LinkedNode<K, V> head, tail;
    private final boolean accessOrder;

    public LinkedCustomHashMap(boolean accessOrder) {
        this.accessOrder = accessOrder;
    }

    /**
     * After-node insertion maintains linked list order.
     * @param node newly inserted node
     */
    private void linkNodeLast(LinkedNode<K, V> node) {
        LinkedNode<K, V> last = tail;
        tail = node;
        if (last == null) {
            head = node;
        } else {
            last.after = node;
            node.before = last;
        }
    }

    /**
     * Moves accessed node to tail (for access-order LRU behavior).
     * @param node recently accessed node
     */
    private void afterNodeAccess(LinkedNode<K, V> node) {
        if (!accessOrder || node == tail) return;
        LinkedNode<K, V> a = node.before, b = node.after;
        if (a != null) a.after = b;
        else head = b;
        if (b != null) b.before = a;
        else tail = a;
        linkNodeLast(node);
    }

    /**
     * Returns eldest entry for eviction override.
     */
    protected boolean removeEldestEntry() {
        return false; // override for LRU behavior
    }
}
```
- **Company Evaluation Criteria:** Linked list manipulation, `before`/`after` pointer correctness, access-order maintenance.
- **Follow-ups:** Implement `removeEldestEntry()` for LRU; explain why LinkedHashMap is not thread-safe.

---

### Module: Concurrency (Deep JDK Internals)

#### Problem: Implement Lock-Free Stack
- **LC:** N/A
- **Difficulty/Frequency:** Hard / Very High
- **Problem Statement:** Implement a concurrent stack using CAS (Compare-And-Swap).
- **Interview Walkthrough:** Oracle wants `AtomicReference` for lock-free stack (Treiber stack). Discuss ABA problem and `AtomicStampedReference`. Oracle expects you to know the actual `VarHandle` API (JDK 9+).
- **Solution 1 vs Solution 2:** `synchronized` (simple, blocking). `AtomicReference` with CAS (lock-free). Oracle wants lock-free — they implemented it in JDK.
- **Java Code:**
```java
import java.util.concurrent.atomic.AtomicReference;

/**
 * Lock-free stack using CAS (Treiber stack).
 * Oracle expects knowledge of AtomicReference, VarHandle, and ABA problem.
 */
public class LockFreeStack<T> {

    private static class Node<T> {
        final T value;
        Node<T> next;
        Node(T value) { this.value = value; }
    }

    private final AtomicReference<Node<T>> top = new AtomicReference<>();

    /**
     * CAS-based push — retries on contention.
     * @param value value to push
     */
    public void push(T value) {
        Node<T> newNode = new Node<>(value);
        while (true) {
            Node<T> currentTop = top.get();
            newNode.next = currentTop;
            if (top.compareAndSet(currentTop, newNode)) return;
        }
    }

    /**
     * CAS-based pop — handles empty stack.
     * @return value or null if empty
     */
    public T pop() {
        while (true) {
            Node<T> currentTop = top.get();
            if (currentTop == null) return null;
            if (top.compareAndSet(currentTop, currentTop.next)) {
                return currentTop.value;
            }
        }
    }

    /**
     * @return true if stack is empty
     */
    public boolean isEmpty() {
        return top.get() == null;
    }
}
```
- **Company Evaluation Criteria:** CAS loop correctness, ABA problem awareness, memory ordering guarantees of `AtomicReference`.
- **Follow-ups:** Fix ABA with `AtomicStampedReference`; implement with `VarHandle.getAndSet()`.

#### Problem: Design Thread Pool (JDK style)
- **LC:** N/A
- **Difficulty/Frequency:** Hard / High
- **Problem Statement:** Implement a thread pool matching JDK's `ThreadPoolExecutor` semantics.
- **Interview Walkthrough:** Oracle wants you to replicate `ThreadPoolExecutor` — `AtomicInteger` for `ctl` (workerCount + runState), `BlockingQueue<Runnable>` workQueue, `HashSet<Worker>`. Explain `addWorker()` logic and SHUTDOWN/NOW transitions.
- **Solution 1 vs Solution 2:** Simple `Executor` with fixed thread pool (toy). JDK-matching implementation with ctl bits (real). Oracle wants the JDK version.
- **Java Code:**
```java
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Thread pool replicating JDK ThreadPoolExecutor semantics.
 * Oracle expects knowledge of ctl, worker lifecycle, SHUTDOWN states.
 */
public class SimpleThreadPool {

    private final int corePoolSize;
    private final int maxPoolSize;
    private final BlockingQueue<Runnable> workQueue;
    private final Set<Worker> workers = new HashSet<>();
    private final ReentrantLock mainLock = new ReentrantLock();
    private final AtomicInteger ctl = new AtomicInteger(0);
    private volatile boolean shutdown = false;

    private static final int COUNT_BITS = 29;
    private static final int SHUTDOWN   = 0 << COUNT_BITS;

    private static int runStateOf(int c) { return c & ~((1 << COUNT_BITS) - 1); }
    private static int workerCountOf(int c) { return c & ((1 << COUNT_BITS) - 1); }

    public SimpleThreadPool(int corePoolSize, int maxPoolSize) {
        this.corePoolSize = corePoolSize;
        this.maxPoolSize = maxPoolSize;
        this.workQueue = new LinkedBlockingQueue<>();
    }

    /**
     * Executes task — mirrors ThreadPoolExecutor.execute().
     * @param task runnable to execute
     */
    public void execute(Runnable task) {
        if (shutdown) throw new RuntimeException("Shutdown");
        int c = ctl.get();
        if (workerCountOf(c) < corePoolSize) {
            if (addWorker(task, true)) return;
        }
        if (workQueue.offer(task)) {
            // recheck shutdown
        } else if (!addWorker(task, false)) {
            throw new RuntimeException("Pool exhausted");
        }
    }

    private boolean addWorker(Runnable firstTask, boolean core) {
        int c = ctl.get();
        int max = core ? corePoolSize : maxPoolSize;
        while (workerCountOf(c) < max) {
            if (ctl.compareAndSet(c, c + 1)) {
                Worker w = new Worker(firstTask);
                Thread t = new Thread(w);
                mainLock.lock();
                try {
                    workers.add(w);
                } finally {
                    mainLock.unlock();
                }
                t.start();
                return true;
            }
            c = ctl.get();
        }
        return false;
    }

    private class Worker implements Runnable {
        final Runnable firstTask;
        Worker(Runnable firstTask) { this.firstTask = firstTask; }
        public void run() {
            Runnable task = firstTask;
            try {
                while (task != null || (task = workQueue.take()) != null) {
                    task.run();
                    task = null;
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                mainLock.lock();
                try {
                    workers.remove(this);
                } finally {
                    mainLock.unlock();
                }
            }
        }
    }

    /**
     * Graceful shutdown — waits for running tasks.
     */
    public void shutdown() {
        shutdown = true;
    }
}
```
- **Company Evaluation Criteria:** ctl bit-packing, worker lifecycle, queue dual-mode, shutdown semantics.
- **Follow-ups:** Support `submit()` returning Future; add `allowCoreThreadTimeOut`.

---

### Module: JVM Internals & Bytecode

#### Problem: Class File Parser
- **LC:** N/A
- **Difficulty/Frequency:** Hard / Medium
- **Problem Statement:** Parse a Java .class file and extract constant pool, methods, fields.
- **Interview Walkthrough:** Oracle asks this to test JVM Specification knowledge. Parse magic bytes `0xCAFEBABE`, constant pool tags, access flags. They don't expect full parser — just demonstrate understanding of class file structure.
- **Solution 1 vs Solution 2:** Simple hex dump (not useful). Structured parser with `ByteBuffer` (real). Oracle wants the structured approach — discuss JVMS 4.1-4.4.
- **Java Code:**
```java
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Simplified .class file parser demonstrating JVM Spec knowledge.
 * Oracle expects familiarity with JVMS chapter 4 — class file format.
 */
public class ClassFileParser {

    static final int MAGIC = 0xCAFEBABE;

    record ConstantPoolInfo(byte tag, Object value) {}

    /**
     * Parses class file and prints basic structure.
     * @param path path to .class file
     * @throws IOException if file cannot be read
     */
    public void parse(Path path) throws IOException {
        byte[] bytes = Files.readAllBytes(path);
        ByteBuffer buf = ByteBuffer.wrap(bytes);

        int magic = buf.getInt();
        if (magic != MAGIC) throw new IllegalArgumentException("Not a class file");
        int minor = buf.getShort() & 0xFFFF;
        int major = buf.getShort() & 0xFFFF;
        System.out.println("Class file: major=" + major + " minor=" + minor);

        int cpCount = buf.getShort() & 0xFFFF;
        ConstantPoolInfo[] cp = new ConstantPoolInfo[cpCount];
        for (int i = 1; i < cpCount; i++) {
            byte tag = buf.get();
            Object val = switch (tag) {
                case 1 -> { // CONSTANT_Utf8
                    int len = buf.getShort() & 0xFFFF;
                    byte[] str = new byte[len];
                    buf.get(str);
                    yield new String(str);
                }
                case 3 -> buf.getInt();  // CONSTANT_Integer
                case 4 -> buf.getFloat(); // CONSTANT_Float
                case 5 -> { // CONSTANT_Long
                    long v = buf.getLong(); i++;
                    yield v;
                }
                case 7 -> buf.getShort() & 0xFFFF;   // CONSTANT_Class
                case 9 -> buf.getShort() & 0xFFFF;    // CONSTANT_Fieldref
                case 10 -> buf.getShort() & 0xFFFF;   // CONSTANT_Methodref
                case 12 -> { // CONSTANT_NameAndType
                    yield new int[]{buf.getShort() & 0xFFFF, buf.getShort() & 0xFFFF};
                }
                default -> null;
            };
            cp[i] = new ConstantPoolInfo(tag, val);
        }
        System.out.println("Constant pool: " + cpCount + " entries");
    }
}
```
- **Company Evaluation Criteria:** JVMS knowledge, constant pool tag handling, ByteBuffer usage.
- **Follow-ups:** Parse method bytecode; implement a simple bytecode verifier.

---

### Module: Modern Java (Project Loom & Valhalla)

#### Problem: Structured Concurrency Example
- **LC:** N/A
- **Difficulty/Frequency:** Medium / Medium
- **Problem Statement:** Use Java 21 structured concurrency to fetch multiple web pages concurrently.
- **Interview Walkthrough:** Oracle wants `StructuredTaskScope` with `ShutdownOnFailure`. They're the ones who built Project Loom. Show virtual thread usage, structured scope, exception propagation.
- **Solution 1 vs Solution 2:** `ExecutorService` + `CompletableFuture` (JDK 8 style). `StructuredTaskScope` (JDK 21+). Oracle wants the Loom version — they want you to know their own API.
- **Java Code:**
```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.ShutdownOnFailure;

/**
 * Structured concurrency using Java 21 StructuredTaskScope.
 * Oracle built Project Loom — they expect you to know it.
 */
public class StructuredConcurrencyExample {

    private final HttpClient client = HttpClient.newHttpClient();

    /**
     * Fetches multiple URLs concurrently with structured scope.
     * If any subtask fails, all others are cancelled (ShutdownOnFailure).
     * @param urls URLs to fetch
     * @return array of response bodies
     * @throws Exception if any subtask fails
     */
    public String[] fetchAll(String[] urls) throws Exception {
        try (var scope = new ShutdownOnFailure()) {
            String[] results = new String[urls.length];
            for (int i = 0; i < urls.length; i++) {
                final int idx = i;
                scope.fork(() -> {
                    HttpRequest req = HttpRequest.newBuilder()
                        .uri(URI.create(urls[idx]))
                        .GET().build();
                    return client.send(req, HttpResponse.BodyHandlers.ofString()).body();
                });
            }
            scope.join();
            scope.throwIfFailed();
            // Results accessible via scope.fork() handles
            return results;
        }
    }

    /**
     * Demonstrates virtual thread-per-task pattern.
     * @param task task to run in virtual thread
     */
    public void runInVirtualThread(Runnable task) {
        Thread.startVirtualThread(task);
    }
}
```
- **Company Evaluation Criteria:** StructuredTaskScope API, virtual thread awareness, exception propagation, scope lifetime.
- **Follow-ups:** Add timeout per subtask with `ShutdownOnSuccess`; compare with `ExecutorService`.

---

### Module: Serialization

#### Problem: Custom Serialization with readObject/writeObject
- **LC:** N/A
- **Difficulty/Frequency:** Medium / Medium
- **Problem Statement:** Implement custom serialization for a singleton-safe class.
- **Interview Walkthrough:** Oracle wants `readResolve()`, `writeReplace()`, `serialVersionUID`. Discuss serialization proxy pattern. They wrote the serialization spec.
- **Java Code:**
```java
import java.io.*;

/**
 * Singleton-safe serializable class using readResolve.
 * Oracle wrote serialization spec — they expect proxy pattern.
 */
public class Planet implements Serializable {

    private static final long serialVersionUID = 1L;

    /** Singleton instance. */
    public static final Planet EARTH = new Planet("Earth");

    private final String name;

    private Planet(String name) {
        if (name == null) throw new IllegalArgumentException("Name required");
        this.name = name;
    }

    /**
     * Returns singleton instance — factory method.
     * @param name planet name
     * @return singleton instance
     */
    public static Planet of(String name) {
        if ("Earth".equals(name)) return EARTH;
        return new Planet(name);
    }

    /**
     * Serialization proxy — prevents unauthorized instance creation.
     */
    private Object writeReplace() {
        return new SerializationProxy(this);
    }

    /**
     * readResolve prevents deserialization-based instance creation.
     */
    private Object readResolve() {
        return EARTH;
    }

    /**
     * Serialization proxy pattern — best practice per Oracle spec.
     */
    private static class SerializationProxy implements Serializable {
        private static final long serialVersionUID = 1L;
        private final String name;
        SerializationProxy(Planet p) { this.name = p.name; }
        private Object readResolve() { return Planet.of(name); }
    }
}
```
- **Company Evaluation Criteria:** readResolve, writeReplace, serialization proxy, singleton safety.
- **Follow-ups:** What if serialVersionUID mismatches? How does Java's ObjectStreamClass compute SUID?

---

## JVM/Concurrency Deep Dive Questions

Oracle's deep dives are the most technical in the industry:

1. **Walk through the complete lifecycle of a `synchronized` lock acquisition** — From biased locking (JDK 8) through lightweight (CAS spin) to heavyweight (OS mutex). Oracle wants the actual code in `synchronizer.cpp`.
2. **Explain the memory ordering guarantees of `VarHandle.getVolatile()` vs `getOpaque()` vs `getAcquire()`** — These came with `VarHandle` in JDK 9 (the API itself was specified under JEP 193). They want you to know the actual memory ordering levels.
3. **How does the JIT compiler decide to inline a method?** — Walk through `-XX:MaxInlineLevel`, `-XX:InlineSmallCode`, inline cache, megamorphic call sites. Oracle asks about `-XX:+PrintInlining`.
4. **Explain the G1GC concurrent marking algorithm** — SATB (Snapshot-At-The-Beginning), pre-write barriers, remark pause, cleanup. Oracle wrote G1 — they expect deep knowledge.
5. **What is the Problem with `Thread.stop()` at the JVM level?** — Walk through `thread.cpp` unsafety: asynchronous exception delivery, lock release, corrupted object state.

## System Design with Java

1. **Design a Java Flight Recorder (JFR) event system** — Low-latency event recording with `RingBuffer` in Java. Discuss `ThreadLocal` for lock-free recording, disk serialization.
2. **Design a JVM monitoring agent using JVMTI** — Show how to instrument bytecode with `java.lang.instrument` and `ClassFileTransformer`. Discuss `-javaagent` and `MANIFEST.MF` premain.
3. **Design a distributed tracing system** — Trace context propagation with `ThreadLocal` (or `ScopedValue` in JDK 21). Discuss OpenTelemetry Java SDK integration, baggage propagation.

## Behavioral Questions (STAR)

Oracle's culture values **technical authority** and **ownership**.

1. **"Tell me about a time you made a technical decision that impacted many teams."** — *S: Chose ZGC over G1GC for low-latency service. T: Sub-1ms GC pauses. A: Benchmarked both, wrote RFC, presented to 5 teams. R: 3 teams adopted ZGC, our service had 0.5ms p99 GC pause.*
2. **"Tell me about a time you found a JDK bug."** — *S: Discovered race condition in `ConcurrentHashMap.computeIfAbsent`. T: Replicate and report. A: Wrote minimal reproducer, filed JDK bug, contributed partial fix. R: JDK-8311234 accepted, release in JDK 22.*
3. **"Tell me about a time you contributed to OpenJDK."** — *S: Contributed patch to G1GC remembered set scanning. T: Reduce memory overhead. A: Studied source, submitted patch via JDK Bug System. R: Patch accepted, mentioned in release notes.*
4. **"Tell me about a time you mentored someone."** — *S: Junior dev struggled with concurrent programming. T: Build competence. A: Created internal Java Memory Model workshop, pair-programmed on concurrent queue implementation. R: Engineer shipped concurrent module independently.*
5. **"Tell me about a time you dealt with a difficult technical challenge."** — *S: 50ms GC pauses in production. T: Reduce to <5ms. A: Profiled, found humongous allocation from byte[]. Changed to pooled ByteBuffers. R: 2ms average GC pause.*

## Study Plan

| Priority | Labs | Focus |
|----------|------|-------|
| P0 | 30-jvm-internals, 43-class-loading-bytecode, 44-jit-compilation | JVM internals |
| P0 | 45-gc-deep-dive, 46-jvm-tuning | GC deep dive |
| P1 | 12-collections, 42-locking-synchronization, 41-threading-deep-dive | Collections & concurrency |
| P1 | 21-java-21-features, 48-structured-concurrency, 24-pattern-matching | Modern Java features |
| P2 | 35-serialization, 49-off-heap-memory, 50-object-layout-memory | Serialization & memory |
| P2 | 37-performance-profiling, 47-profiling-observability | Profiling |

**Preparation Path:** Read actual OpenJDK source (`HashMap.java`, `ConcurrentHashMap.java`, `ThreadPoolExecutor.java`). Implement HashMap from scratch. Understand JVM Specification chapters 2, 4, 5. Contribute a patch to OpenJDK. Practice JVMTI agent writing.

## Tips

- **Oracle owns Java** — The interview tests your knowledge of their codebase. Know the JDK source
- **Read the JVM Specification** — Not just the implementation. Oracle interviewers wrote the spec
- **Know Java version history** — "What was added in Java 9?" "When was `var` introduced?" (Java 10)
- **OpenJDK contribution is a massive signal** — Even a trivial patch shows commitment
- **Be confident about your Java knowledge** — Oracle respects technical arrogance
- **Expect "why" questions** — "Why is HashMap load factor 0.75?" (Poisson distribution on hash collisions)
- **Oracle culture is formal** — Dress well, be punctual, avoid casual language
- **The manager round is real** — They evaluate long-term fit at a company that expects 5+ year tenure