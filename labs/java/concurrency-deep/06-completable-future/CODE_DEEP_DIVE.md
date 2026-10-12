# CompletableFuture — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Who Runs the Stage: Completing Thread vs Common Pool

Three rules, one snippet each inside a single class ("attached a stage to a
future nobody completes" hangs forever — the sketches below always complete
their gates):

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;

public class WhoRunsIt {
    public static void main(String[] args) throws Exception {
        String mainName = Thread.currentThread().getName();

        // 1. Non-async on completed future: runs HERE
        String[] syncThread = {null};
        CompletableFuture.completedFuture("x")
                .thenApply(v -> { syncThread[0] = Thread.currentThread().getName(); return v; });
        System.out.println("sync stage thread: " + syncThread[0]);
        System.out.println("ran in caller thread: " + mainName.equals(syncThread[0]));

        // 2. Async variant: common pool worker
        String[] asyncThread = {null};
        CountDownLatch done = new CountDownLatch(1);
        CompletableFuture.completedFuture("x").thenApplyAsync(v -> {
            asyncThread[0] = Thread.currentThread().getName();
            done.countDown();
            return v;
        });
        done.await();
        System.out.println("async stage thread: " + asyncThread[0]);
        System.out.println("ran in ForkJoinPool.commonPool-worker: "
                + asyncThread[0].startsWith("ForkJoinPool.commonPool-worker"));

        // 3. Non-async on INCOMPLETE future: runs in whoever completes it
        CompletableFuture<String> gate = new CompletableFuture<>();
        String[] finisherThread = {null};
        gate.thenApply(v -> {
            finisherThread[0] = Thread.currentThread().getName();
            return v;
        });
        Thread finisher = new Thread(() -> gate.complete("go"), "finisher-thread");
        finisher.start();
        finisher.join();
        System.out.println("dependent ran in completing thread: "
                + "finisher-thread".equals(finisherThread[0]));
    }
}
```

Expected output:
```
sync stage thread: main
ran in caller thread: true
async stage thread: ForkJoinPool.commonPool-worker-1
ran in ForkJoinPool.commonPool-worker: true
dependent ran in completing thread: true
```

Three rules, three demonstrations: completed futures run dependents inline,
`*Async` borrows the common pool, and pending futures donate their
continuation to whoever calls `complete()`. (Worker number varies —
`worker-1` here; the `startsWith` assertion is the portable claim.)

## 2. thenApply vs thenCompose (the Nested-Future Bug)

```java
import java.util.concurrent.CompletableFuture;

public class MapVsFlatMap {
    static CompletableFuture<String> lookup(String id) {
        return CompletableFuture.completedFuture("name-for-" + id);
    }

    public static void main(String[] args) throws Exception {
        // WRONG shape: thenApply over a future-returning function nests
        CompletableFuture<CompletableFuture<String>> nested =
                CompletableFuture.completedFuture("42").thenApply(MapVsFlatMap::lookup);
        System.out.println("nested type value: " + nested.get().get());

        // RIGHT shape: thenCompose flattens to CF<String>
        CompletableFuture<String> flat =
                CompletableFuture.completedFuture("42").thenCompose(MapVsFlatMap::lookup);
        System.out.println("flat value: " + flat.get());
        System.out.println("flat is direct (no .get().get()): "
                + "name-for-42".equals(flat.get()));
    }
}
```

Expected output:
```
nested type value: name-for-42
flat value: name-for-42
flat is direct (no .get().get()): true
```

Both "work" — the bug is ergonomic, not functional: every downstream stage
on `nested` must unwrap twice, and combinators (`allOf`, `exceptionally`)
operate on the *outer* future. `map` vs `flatMap`, same as streams.

## 3. allOf Carries No Values; Failures Need Unpacking

```java
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

public class AllOfShape {
    public static void main(String[] args) {
        CompletableFuture<Integer> a = CompletableFuture.completedFuture(10);
        CompletableFuture<Integer> b = CompletableFuture.completedFuture(20);
        CompletableFuture<Integer> c = CompletableFuture.completedFuture(30);

        CompletableFuture<Void> all = CompletableFuture.allOf(a, b, c);
        all.join();   // yield CF<Void>: completed, no payload
        int sum = a.join() + b.join() + c.join();   // join can't block now
        System.out.println("sum after allOf: " + sum);

        // failure surfacing: allOf completes exceptionally; cause is first failure
        CompletableFuture<Integer> bad =
                CompletableFuture.failedFuture(new IllegalStateException("boom"));
        try {
            CompletableFuture.allOf(a, bad).join();
            System.out.println("no failure (unexpected)");
        } catch (CompletionException e) {
            System.out.println("allOf failure cause: "
                    + e.getCause().getClass().getSimpleName());
        }
        System.out.println("anyOf type is Object: "
                + (CompletableFuture.anyOf(a, b) instanceof CompletableFuture));
    }
}
```

Expected output:
```
sum after allOf: 60
allOf failure cause: IllegalStateException
anyOf type is Object: true
```

`allOf` is a barrier, not a collector — values come from the inputs (safe to
`join` since all completed). The failure path shows the unwrapping rule:
`join` wraps in `CompletionException`; the *cause* is the domain error.

## 4. cancel() Never Interrupts; Handlers Have Distinct Contracts

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;

public class CancelAndHandle {
    public static void main(String[] args) throws Exception {
        // cancel() on a RUNNING task: task finishes anyway
        CountDownLatch entered = new CountDownLatch(1);
        CountDownLatch mayFinish = new CountDownLatch(1);
        AtomicBoolean taskCompleted = new AtomicBoolean();
        CompletableFuture<String> running = CompletableFuture.supplyAsync(() -> {
            entered.countDown();
            try {
                mayFinish.await();   // sensitive to interrupt...
            } catch (InterruptedException e) {
                return "interrupted";   // ...but cancel() never sends one
            }
            taskCompleted.set(true);
            return "finished-normally";
        });
        entered.await();
        boolean cancelled = running.cancel(true);   // mayInterruptIfRunning=true, ignored
        mayFinish.countDown();
        Thread.sleep(200);
        System.out.println("cancel returned: " + cancelled);
        System.out.println("task still ran to completion: " + taskCompleted.get());
        System.out.println("future isCancelled: " + running.isCancelled());

        // exceptionally vs handle vs whenComplete
        CompletableFuture<Integer> failed =
                CompletableFuture.failedFuture(new IllegalArgumentException("bad"));
        System.out.println("exceptionally recovers: "
                + failed.exceptionally(ex -> -1).join());
        System.out.println("handle sees ex: "
                + failed.handle((v, ex) -> ex == null ? "v=" + v : "ex=" + ex.getMessage()).join());
        StringBuilder log = new StringBuilder();
        Integer probe = failed.whenComplete((v, ex) ->
                log.append("saw:").append(ex.getMessage())).exceptionally(ex -> -2).join();
        System.out.println("whenComplete peeked (" + log + ") without changing outcome: "
                + (probe == -2));
    }
}
```

Expected output:
```
cancel returned: true
task still ran to completion: true
future isCancelled: true
exceptionally recovers: -1
handle sees ex: ex=bad
whenComplete peeked (saw:bad) without changing outcome: true
```

`cancel(true)` returned true (state flip won) while the task *also* ran to
completion — both statements true simultaneously, because cancellation and
execution are independent races. The handler trio: `exceptionally` replaces
failure with value, `handle` unifies both paths into one function,
`whenComplete` observes without altering (the `-2` still comes from the
chained `exceptionally`).

## 5. orTimeout Bounds a Wait Without an Executor

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class OrTimeout {
    public static void main(String[] args) {
        CompletableFuture<String> never = new CompletableFuture<>();
        try {
            never.orTimeout(200, TimeUnit.MILLISECONDS).join();
            System.out.println("completed (unexpected)");
        } catch (java.util.concurrent.CompletionException e) {
            System.out.println("orTimeout cause: "
                    + e.getCause().getClass().getSimpleName());
        }

        CompletableFuture<String> quick =
                CompletableFuture.completedFuture("fast")
                        .completeOnTimeout("fallback", 200, TimeUnit.MILLISECONDS);
        System.out.println("completeOnTimeout on ready future: " + quick.join());

        CompletableFuture<String> slow = new CompletableFuture<>();
        CompletableFuture<String> withFallback =
                slow.completeOnTimeout("fallback", 200, TimeUnit.MILLISECONDS);
        System.out.println("same object returned (not a derived stage): " + (withFallback == slow));
        System.out.println("pending future gets fallback: " + withFallback.join());
        System.out.println("original now complete: " + slow.isDone());
    }
}
```

Expected output:
```
orTimeout cause: TimeoutException
completeOnTimeout on ready future: fast
same object returned (not a derived stage): true
pending future gets fallback: fallback
original now complete: true
```

`orTimeout` fails the future itself with `TimeoutException` (wrapped in
`CompletionException` by `join`); `completeOnTimeout` completes the future
itself with the fallback. Both return `this` — there is no derived stage,
so unlike `exceptionally`/`handle` chains there is nothing downstream to
diverge: the timeout act is in-place.

## Common Pitfalls Encountered Here

- **Attaching stages to futures nobody completes** — silent hangs (snippet
  1's deleted sketch).
- **Blocking the common pool** — I/O stages need a dedicated executor;
  single-CPU containers silently switch the default to thread-per-task.
- **`thenApply` with future-returning functions** — `CF<CF<U>>` nesting
  (snippet 2).
- **Expecting values from `allOf`** — barrier only; join the inputs
  (snippet 3).
- **Expecting `cancel(true)` to interrupt** — it never does; running tasks
  finish (snippet 4).
- **`whenComplete` as a recovery tool** — it can't change the outcome;
  `exceptionally`/`handle` do (snippet 4).
- **Recursive join on a tiny pool** — self-deadlock; size pools for the
  dependency depth or restructure with composition.
