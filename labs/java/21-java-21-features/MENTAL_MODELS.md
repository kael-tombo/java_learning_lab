# Mental Models for Java 21 Features

## Virtual Threads: The Conveyor Belt Model

Imagine a **conveyor belt** (the carrier thread, a platform thread) moving through a factory. Workers (virtual threads) hop onto the conveyor belt when they have work to do, ride it through their task, and hop off when they need to wait (block on I/O). While they wait, they sit on a bench (the heap) without blocking the conveyor belt. When the waiting ends, they hop back onto the conveyor belt (possibly a different one) and continue.

Key insights from this model:
- **Mounting/Unmounting**: Virtual threads don't own the carrier thread; they borrow it
- **Parking**: Blocking operations cause the virtual thread to "park" (sit on the bench)
- **Continuation**: The JVM saves the virtual thread's stack as a continuation on the heap
- **Many-to-Few**: Thousands of virtual threads share a handful of carrier threads

When you see `Thread.sleep(1000)` in a virtual thread, think: "the virtual thread steps off the conveyor belt, takes a 1-second break on the bench, then steps back onto a conveyor belt."

## Pattern Matching: The Sorting Machine

Imagine a **sorting machine** in a package distribution center. Packages (objects) arrive on a conveyor belt. The machine examines each package's label and routes it to the appropriate chute. The machine has different chutes for:
- Specific box sizes (type patterns)
- Boxes with certain labels (guarded patterns)
- Boxes that contain smaller boxes that can be inspected recursively (record patterns)

The sorting machine must have a chute for every possible package type (exhaustiveness). If a new type of package is added, the machine won't work until a new chute is built (compile error).

## Sequenced Collections: The Double-Ended Queue

Think of a line of people (elements) standing in a defined order. With sequenced collections, you can:
- See who's first (`getFirst()`)
- See who's last (`getLast()`)
- Add someone to the front (`addFirst()`)
- Add someone to the back (`addLast()`)
- Remove the front person (`removeFirst()`)
- Remove the last person (`removeLast()`)
- Look at the line from the opposite direction (`reversed()` — returning a mirror view, not a new line)

This model works whether the line is a List (e.g., ArrayList), a Deque, or an ordered Set.

## String Templates: The Mad Libs Book

String Templates — previewed in JDK 21/22 and withdrawn before JDK 23, so this model is historical (apply it to `String.formatted` today) — work like a Mad Libs book. The book has fixed text with blanks to fill in:

```
"Hello, \{name}! You have \{count} new messages."
```

The `\{name}` and `\{count}` are the blanks. The **template processor** would have filled in the blanks, with different processors filling them differently:
- `STR`: Simple string interpolation (the literal interpretation)
- `FMT`: Formatted output with format specifiers — the role `String.formatted` plays today
- Custom processor (e.g., `SQL`): Builds parameterized queries safely

The key mental shift: instead of building strings by gluing pieces together, you start with a template and let the processor handle the composition safely.

## Structured Concurrency: The Project Manager

Think of a **project manager** who creates a project (scope), assigns tasks to team members (child virtual threads), and waits for all team members to complete before declaring the project done. If any team member fails (throws an exception), the project manager cancels all remaining tasks and reports the failure. If the project manager is told to stop early (shutdown/cancel), they cancel all team members immediately.

The project manager ensures:
- No task runs after the project is complete (no orphaned threads)
- All resources acquired during the project are released
- Failures are collected and reported coherently

This model directly maps to `StructuredTaskScope`:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> user = scope.fork(() -> fetchUser(id));
    Future<Address> addr = scope.fork(() -> fetchAddress(id));
    scope.join();
    scope.throwIfFailed();
    return new Result(user.resultNow(), addr.resultNow());
}
```

The `try-with-resources` block ensures the scope waits for all tasks, just as a project manager ensures all tasks complete before the project is closed.
