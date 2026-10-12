# Structured Concurrency — Code Deep Dive

**Build flags (required, JDK 23): `javac --release 23 --enable-preview` /
`java --enable-preview`. Every snippet below was verified exactly so on JDK
23.** The standard `--release 21` harness cannot compile preview APIs — see
`verify_preview.py` in the temp workspace for the adapted verifier used
here. If you run on JDK 25+, expect API drift (JEP 505 reshaped parts).

## 1. ShutdownOnFailure Fan-Out: All Results or First Failure

```java
import java.util.concurrent.StructuredTaskScope;

public class FanOut {
    static String fetchUser() throws InterruptedException {
        Thread.sleep(50);
        return "ada";
    }
    static int fetchOrders() throws InterruptedException {
        Thread.sleep(80);
        return 7;
    }

    public static void main(String[] args) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var user = scope.fork(FanOut::fetchUser);
            var orders = scope.fork(FanOut::fetchOrders);
            scope.join();
            scope.throwIfFailed();   // no-op: all succeeded
            System.out.println("user=" + user.get() + " orders=" + orders.get());
            System.out.println("combined: " + (user.get() + ":" + orders.get()));
        }
    }
}
```

Expected output:
```
user=ada orders=7
combined: ada:7
```

The block reads like sequential code: fork two callables, join, use both
results. No latch, no `Future.get` checked-exception plumbing at the use
site (`Subtask.get()` is unchecked after join), no leftover-thread audit —
`close()` guarantees containment.

## 2. First Failure Cancels Siblings and Rethrows

```java
import java.util.concurrent.ExecutionException;
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.atomic.AtomicBoolean;

public class FailFast {
    public static void main(String[] args) throws Exception {
        AtomicBoolean siblingInterrupted = new AtomicBoolean();
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var ok = scope.fork(() -> {
                Thread.sleep(5_000);   // would outlive the scope...
                return "slow";
            });
            var bad = scope.fork(() -> {
                Thread.sleep(50);
                throw new IllegalStateException("backend down");
            });
            scope.join();
            try {
                scope.throwIfFailed();
                System.out.println("no failure (unexpected)");
            } catch (ExecutionException e) {
                System.out.println("throwIfFailed cause: "
                        + e.getCause().getClass().getSimpleName());
            }
            System.out.println("ok subtask state: " + ok.state());
            System.out.println("bad subtask state: " + bad.state());
        }
    }
}
```

Expected output:
```
throwIfFailed cause: IllegalStateException
ok subtask state: UNAVAILABLE
bad subtask state: FAILED
```

The failing subtask triggers `shutdown()`; the slow sibling is interrupted
while parked in `sleep` (interruptible — a compute loop ignoring interrupts
would linger until the scope's `close()` still reaps it). States tell the
story afterwards: FAILED vs never-completed. Note `ok.get()` here would
throw — only `get()` on SUCCESS states.

## 3. ShutdownOnSuccess: Hedged Redundancy, First Answer Wins

```java
import java.util.concurrent.StructuredTaskScope;

public class Hedged {
    public static void main(String[] args) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
            scope.fork(() -> {
                Thread.sleep(30);
                throw new IllegalStateException("replica A failed");
            });
            scope.fork(() -> {
                Thread.sleep(120);
                return "replica B answer";
            });
            scope.join();
            System.out.println("result: " + scope.result());
            System.out.println("first success wins despite earlier failure: "
                    + "replica B answer".equals(scope.result()));
        }
    }
}
```

Expected output:
```
result: replica B answer
first success wins despite earlier failure: true
```

Deterministic regardless of timing: exactly one subtask ever succeeds, so
`result()` has exactly one possible answer. (With two *racing* successes the
winner would be scheduler-dependent — the snippet avoids asserting that.)
The failed replica's exception never surfaces: success preempts failure
under this policy, the mirror image of snippet 2.

## 4. joinUntil Bounds the Wait; Ownership Is Enforced

```java
import java.time.Instant;
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.TimeoutException;

public class DeadlineAndOwner {
    public static void main(String[] args) throws Exception {
        // joinUntil: bounded wait with TimeoutException
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            scope.fork(() -> {
                Thread.sleep(5_000);
                return "too-slow";
            });
            try {
                scope.joinUntil(Instant.now().plusMillis(200));
                System.out.println("joined (unexpected)");
            } catch (TimeoutException e) {
                System.out.println("joinUntil timed out as designed");
            }
        } // close() shuts down the lingering subtask: no leak

        // ownership: only the creating thread may join
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            scope.fork(() -> "x");
            Thread intruder = new Thread(() -> {
                try {
                    scope.join();
                    System.out.println("intruder joined (unexpected)");
                } catch (java.util.concurrent.StructureViolationException e) {
                    System.out.println("intruder got StructureViolation (unexpected kind)");
                } catch (Exception e) {
                    System.out.println("intruder rejected: "
                            + e.getClass().getSimpleName());
                }
            });
            intruder.start();
            intruder.join(5_000);
            scope.join();
        }
    }
}
```

Expected output:
```
joinUntil timed out as designed
intruder rejected: WrongThreadException
```

Two guarantees in one snippet: bounded waits via deadline (the scope still
cleans up afterwards through `close()`), and structural ownership — the
intruder's `join()` throws `WrongThreadException`, not a silent mis-join.
Structure is enforced by exceptions, not conventions.

## 5. Nesting Composes: Scopes Inside Subtasks

```java
import java.util.concurrent.StructuredTaskScope;

public class Nested {
    static int leaves(String prefix, int lo, int hi) throws Exception {
        if (hi - lo <= 2) {
            int s = 0;
            for (int i = lo; i < hi; i++) s += i;
            return s;
        }
        int mid = (lo + hi) >>> 1;
        try (var inner = new StructuredTaskScope.ShutdownOnFailure()) {
            var l = inner.fork(() -> leaves(prefix + "L", lo, mid));
            var r = inner.fork(() -> leaves(prefix + "R", mid, hi));
            inner.join();
            inner.throwIfFailed();
            return l.get() + r.get();
        }
    }

    public static void main(String[] args) throws Exception {
        int total;
        try (var outer = new StructuredTaskScope.ShutdownOnFailure()) {
            var t = outer.fork(() -> leaves("", 0, 100));
            outer.join();
            outer.throwIfFailed();
            total = t.get();
        }
        System.out.println("nested sum 0..99 = " + total + " (expected 4950)");
        System.out.println("exact: " + (total == 4950));
    }
}
```

Expected output:
```
nested sum 0..99 = 4950 (expected 4950)
exact: true
```

Fork-join-shaped recursion with scope-per-level: each inner scope contains
its own children, failures propagate level by level via `throwIfFailed`,
and the outer block still bounds everything. Compare lab 07's
`RecursiveTask` version — same shape, plus failure propagation and
containment the raw pool never provided.

## Common Pitfalls Encountered Here

- **Compiling without `--enable-preview`** — preview APIs are invisible
  otherwise; the error (`package StructuredTaskScope does not exist`-style)
  looks like a missing import.
- **Calling `get()` on non-SUCCESS subtasks** — throws; check `state()` or
  rely on the policy methods (`throwIfFailed`/`result`) first.
- **Joining from a non-owner thread** — `WrongThreadException` (snippet 4);
  hand results out, not scope handles.
- **Compute loops ignoring interrupts** — shutdown requests linger until
  `close()` reaps them; honor interruption for prompt cancellation.
- **Assuming JDK 25 API identity** — JEP 505 reshaped parts; pin snippets to
  the stated JDK or re-verify (this file: JDK 23).
- **Platform-thread-per-subtask at scale** — the model assumes cheap
  threads (virtual); hundreds of platform-thread subtasks waste R1MB stacks
  each.
