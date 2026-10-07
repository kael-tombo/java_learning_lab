# CODE_DEEP_DIVE — Java Version History

Five transformations of the *same problem*, each annotated with the version that
made it shorter and the price it charged. Where the change is visible in bytecode,
`javap -c` output is included — because the mechanism is the lesson.

---

## 1. Anonymous class → lambda (7 → 8)

### Before (Java 7)

```java
import java.util.concurrent.Callable;

public final class TaskSubmitter {
    private final String tenantId;

    public TaskSubmitter(String tenantId) { this.tenantId = tenantId; }

    public Callable<String> callFor(final String op) {
        return new Callable<String>() {          // 4 extra lines of ceremony
            @Override
            public String call() {
                return "tenant=" + tenantId + " op=" + op;
            }
        };
    }
}
```

### After (Java 8)

```java
import java.util.concurrent.Callable;

public final class TaskSubmitter {
    private final String tenantId;

    public TaskSubmitter(String tenantId) { this.tenantId = tenantId; }

    public Callable<String> callFor(String op) {   // `final` no longer required
        return () -> "tenant=" + tenantId + " op=" + op;   // 1 line
    }
}
```

### Bytecode

```bash
javac -d out8 TaskSubmitter.java && javap -p -c -cp out8 TaskSubmitter
```

Before, `javac` emits a **separate class file** `TaskSubmitter$1` with its own
`call()` method and a synthetic `this$0` field for the captured `tenantId`. The
call site is `new` + `invokespecial` + `invokespecial`.

After, `javap -p` shows **no nested class at all**:

```text
private java.lang.String lambda$callFor$0(java.lang.String);   // synthetic, in TaskSubmitter
...
invokedynamic #2, 0 // InvokeDynamic #0:callFor:()Ljava/util/concurrent/Callable;
```

The `invokedynamic` call site has a bootstrap method (`LambdaMetafactory`) that
spins the implementation class **once at first execution and caches it**. Three
consequences that matter:

1. **Anonymous classes are loaded once per instance; lambda call sites link once
   per class.** In a hot loop of anonymous inner classes you pay class loading
   repeatedly.
2. The captured variables become **arguments** to the synthetic method rather
   than fields, which is why lambda capture costs no per-instance object.
3. The design could then change underneath the call site — serializable lambdas,
   better inlining — without recompiling callers. `invokedynamic` is an
   *evolution mechanism*, exactly as THEORY.md's pattern 3 says.

**What 8 charged for it.** Lambdas only work on *single*-abstract-method
interfaces, so every "functional interface" in your codebase becomes part of the
platform's API contract. And `Collection.toArray(IntFunction)` is the visible
scars of default methods, which were added in the same release so interfaces could
grow without breaking implementors.

---

## 2. Entity class → record (7 → 16)

### Before (Java 8)

```java
import java.util.Objects;

public final class Order {
    private final String id;
    private final double total;

    public Order(String id, double total) {
        this.id = id;
        this.total = total;
    }
    public String getId()       { return id; }      // 12 lines of pure ceremony
    public double getTotal()    { return total; }
    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Order)) return false;
        Order other = (Order) o;
        return Double.compare(total, other.total) == 0
            && Objects.equals(id, other.id);
    }
    @Override public int hashCode() { return Objects.hash(id, total); }
    @Override public String toString() { return "Order[id=" + id + ", total=" + total + "]"; }
}
```

### After (Java 16)

```java
public record Order(String id, double total) {}
```

### What the compiler synthesizes

`equals`, `hashCode`, and `toString` are generated; the accessors are `id()` and
`total()`, **not** `getId()`/`getTotal()`; the class is `final`; a canonical
constructor is generated; and a **compact constructor** lets you normalise without
declaring fields:

```java
public record Order(String id, double total) {
    public Order {                // compact constructor — no field list. Must be at
                                  // least as accessible as the record itself (public here)
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id");
        if (total < 0) throw new IllegalArgumentException("total");
    }
}
```

### Bytecode and the API surface

```bash
javap -p -cp out16 Order    # equals/hashCode/toString/id()/total() all present, none written by you
javap -v -cp out16 Order | grep -E 'Record|flags'
```

The class file carries a **`Record` attribute** naming the components. That is how
reflection, serialization frameworks, and `MethodHandles` can tell a record from a
hand-written class with the same members — a genuine semantic addition, unlike
`var`.

**What 16 charged for it.** Two prices, both permanent:

1. **Shallow immutability.** `record Line(Order o, List<Item> items)` is not
   deeply immutable; the list is still mutable, so a record can carry a mutable
   field and defeat every immutability assumption downstream.
2. **No inheritance.** Records extend only `Record` and are final, so the
   subclass-based modelling patterns built between 2004 and 2016 no longer
   compose. And the synthesized `equals` can differ from a hand-written one —
   `Double.compare` vs `==` — which changes `HashMap` behaviour for anyone
   migrating incrementally.

---

## 3. `instanceof` chain → pattern match (7 → 16 → 21)

### Before (Java 7)

```java
public String describe(Object o) {
    if (o instanceof String && ((String) o).length() > 3) {   // test, then cast: the type
        return "long string: " + o;                           // is written twice
    } else if (o instanceof String) {
        return "short string";
    } else if (o instanceof Integer) {
        return "int " + (((Integer) o) + 1);
    } else if (o instanceof int[]) {
        return "int array of " + ((int[]) o).length;
    }
    return "other";                        // silently absorbs every unknown type
}
```

### After (Java 21)

```java
public String describe(Object o) {
    return switch (o) {                    // exhaustive: no default needed for sealed input
        case String s when s.length() > 3 -> "long string: " + s;
        case String s                     -> "short string";
        case Integer i                    -> "int " + (i + 1);
        case int[] a                      -> "int array of " + a.length;
        case null                         -> "no value";        // 21: explicit null case
        default                           -> "other";
    };
}
```

Three separate features contributed, over many releases: `instanceof` type
binding (**previews in 14 and 15, final in 16**, JEPs 305, 375, 394), `switch`
pattern matching (**previews in 17, 18, 19 and 20, final in 21**, JEPs 406, 420,
427, 433, 441; guards were written `&&` early on and became `when` in the third
preview) and record patterns (**previews in 19 and 20, final in 21**, JEPs 405, 432,
440).

### The win that is only visible in the sealed case

```java
sealed interface Result permits Ok, Err {}
record Ok(int value)                 implements Result {}
record Err(String message, int code) implements Result {}

final class Renderer {
    // 21: record patterns (final) — destructuring in the case label
    static String render(Result r) {
        return switch (r) {
            case Ok(int v)            -> "ok:" + v;
            case Err(String m, int c) -> "err:" + c + ":" + m;
        };                      // no default: the compiler proves the sealed set is covered
    }
}
```

Before sealed types this required either a `default` that silently absorbed
unknown cases or an abstract `render()` on every subtype — pushing dispatch to the
subtypes and breaking the call site.

### Bytecode

```bash
javap -c -p -cp out21 PatternDemo | grep -E 'instanceof|tableswitch|lookupswitch|invokedynamic'
```

Observed with `javac --release 21` and `javap -c -p`:

- The `if` chain compiles to repeated `instanceof` plus branches.
- The pattern `switch` compiles to a single `invokedynamic` whose bootstrap method is
  `java.lang.runtime.SwitchBootstraps.typeSwitch`; it returns the index of the
  matching case, and a `tableswitch` (or `lookupswitch`) then dispatches on that
  index.
- **Record patterns do not use `invokedynamic`.** javac emits ordinary
  `invokevirtual` calls to the record's **accessor methods** (`Ok.value()`,
  `Err.message()`, `Err.code()`), so a custom accessor is honoured, and wraps the
  extraction so that an exception thrown by an accessor surfaces as a
  `MatchException`. (`ObjectMethods` is the bootstrap behind a record's
  `equals`/`hashCode`/`toString`, not its patterns.)

The desugaring is an implementation detail and can change between JDK releases, but
two consequences are part of the language: patterns call *accessors*, and they match
components **positionally**, so a record's component order is part of its
deconstruction contract.

**What it charged.** Adding a permitted subtype is a **compile error** at every
exhaustive switch. You have bought exhaustiveness by giving up open-ended
extension — an inversion of the usual trade-off, and the single most surprising
migration consequence of 17/21.

---

## 4. `if`/`else` chain → switch expression (1.0 → 14)

### Before (Java 7)

```java
public final class Calc {
    enum Operation { ADD, SUB, MUL, DIV }

    public int apply(Operation op, int lhs, int rhs) {
        int result;
        switch (op) {                    // switch since 1.0 (ints/enums; strings from 7)
            case ADD: result = lhs + rhs; break;
            case SUB: result = lhs - rhs; break;
            case MUL: result = lhs * rhs; break;
            case DIV:
                if (rhs == 0) throw new ArithmeticException("div by zero");
                result = lhs / rhs;
                break;
            default: throw new IllegalArgumentException("op " + op);
        }
        return result;                    // variable + breaks + a sentinel
    }
}
```

### After (Java 14)

```java
public final class Calc {
    enum Operation { ADD, SUB, MUL, DIV }

    public int apply(Operation op, int lhs, int rhs) {
        return switch (op) {
            case ADD -> lhs + rhs;
            case SUB -> lhs - rhs;
            case MUL -> lhs * rhs;
            case DIV -> {
                if (rhs == 0) throw new ArithmeticException("div by zero");
                yield lhs / rhs;         // yield, not return, not break
            }
        };                    // no result variable, no breaks, and no default
    }
}
```

The throwaway `result` variable disappears, `break` becomes `yield`, and because
every `enum` constant is covered the compiler knows the switch is exhaustive — so
**`default` is optional**, and omitting it means a future enum constant is a
compile error rather than a runtime `IllegalArgumentException`.

For strings it compounds with pattern matching (Java 7 added strings to
`switch`; 21 added patterns):

```java
// 21: one construct covers enums, strings, sealed hierarchies and records
String describe(Shape s) {
    return switch (s) {
        case Circle(double r)   -> "circle r=" + r;
        case Square(double side) -> "square a=" + side * side;
    };
}
```

**What it charged.** Exhaustive switch over an `enum` is now a *source
compatibility* commitment: adding a constant breaks every switch expression in the
codebase. This hit every library that had a public API switching on an enum, and
it is why the arrow form shipped first as a preview (12) and took two releases to
stabilise.

---

## 5. `PooledThread` → `virtualThread` (1.5 → 21)

### Before (Java 8 — the shape most services still have)

```java
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class OrderService {
    private final ExecutorService pool =                    // bounded on purpose
            Executors.newFixedThreadPool(200);              // ~200 MiB of reserved thread stacks

    public CompletableFuture<List<String>> fetch(List<String> ids) {
        List<CompletableFuture<String>> calls = ids.stream()
            .map(id -> CompletableFuture.supplyAsync(() -> call(id), pool))  // queues above 200, ever
            .toList();
        return CompletableFuture.allOf(calls.toArray(CompletableFuture[]::new))
            .thenApply(v -> calls.stream().map(CompletableFuture::join).toList());
    }

    private String call(String id) { return id; }           // stands in for a blocking HTTP call
}
```

Two designs are tangled together: a **resource ceiling** (the pool) and a
**concurrency shape** (bounded parallelism). The pool size was a compromise
between OS thread limits and memory, and once you hit it, latency is queueing
delay — not work.

### After (Java 21)

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Semaphore;
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.Joiner;
import java.util.concurrent.StructuredTaskScope.Subtask;

public final class OrderService {
    private static final Semaphore CPU_BOUND = new Semaphore(8);   // where a limit belongs
                                                                   // (guards CPU-heavy work, not I/O)

    // JDK 25 preview API (JEP 505, fifth preview): compile and run with --enable-preview.
    // JDK 21-24 spelled this `new StructuredTaskScope.ShutdownOnFailure()` and
    // `scope.join().throwIfFailed()`; the API changed shape in 25, so check your JDK.
    public List<String> fetch(List<String> ids) throws InterruptedException {
        try (var scope = StructuredTaskScope.open(Joiner.<String>allSuccessfulOrThrow())) {
            for (String id : ids) scope.fork(() -> call(id));
            return scope.join()                    // throws if any subtask failed
                        .map(Subtask::get)
                        .toList();
        }
    }

    // For a plain blocking service, no scope is even needed (virtual threads, JDK 21+ final):
    public List<String> fetchSimple(List<String> ids) throws InterruptedException {
        List<String> results = Collections.synchronizedList(new ArrayList<>());
        List<Thread> workers = new ArrayList<>();
        for (String id : ids) workers.add(Thread.ofVirtual().start(() -> results.add(call(id))));
        for (Thread t : workers) t.join();
        return results;
    }

    private String call(String id) { return id; }          // stands in for a blocking HTTP call
}
```

What changed, and it is a *concurrency model* change, not an API change:

```math
before:  concurrency ceiling = pool_size = 200,  latency = queue + work
after:   concurrency ceiling = min(db_pool, conn_pool, rate_limit), latency = work
```

### Bytecode and runtime evidence

```bash
java -cp out8  -XX:+UnlockDiagnosticVMOptions -XX:+PrintThreadsInDump -jar app.jar & 
jcmd $! Thread.print | grep -c '^"'
java -cp out21 -Djdk.trace.vthread.enabled=true -Djdk.trace.vthread=lock,submit -jar app.jar 2>&1 | head -30
```

The Java-8 thread dump shows thousands of `java.lang.Thread` entries with
1 MiB-reserved stacks. The Java-21 run prints **virtual thread traces** — each
showing mount points (`SocketInputStream.socketRead0`), pinning status, and the
carrier thread — and `Thread.print` shows only a handful of platform threads
because parked virtual threads are unmounted and cost almost nothing.

**What it charged.** This is the important part:

1. **`synchronized` pins the carrier.** A virtual thread that blocks inside a
   synchronized block stays mounted for the whole wait, and you give back the
   entire win. Migrating to virtual threads is a `synchronized`-audit, not a
   pool-deletion.
2. **Pool-based code still compiles and is now wrong.** It did not fail loudly; it
   just stopped being the right shape — which is why this change is more
   dangerous than any compile error in the timeline.
3. **CPU-bound work does not scale.** With 4 cores and 10,000 virtual threads, you
   get 4 cores' worth of work. `Semaphore` is the right tool, per
   MATH_FOUNDATION.md §4.
4. **Structured concurrency is still preview** (JDK 21 → 25), so the
   scope-based example above needs `--enable-preview` and is explicitly not
   production code. The plain `Thread.ofVirtual()` form is standard. This is the
   preview rule from VISION.md in practice: use the standard mechanism, treat the
   preview one as an experiment.