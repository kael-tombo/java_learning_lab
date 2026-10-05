# FLASHCARDS — Modern Java Deep Dive

## Records

| Q | A |
|---|---|
| Record declaration syntax | `record Point(int x, int y) { }` |
| Generated members | Canonical constructor, accessors (x(), y()), equals, hashCode, toString |
| Serialization support | `writeReplace`/`readResolve` delegate to canonical constructor |
| Compact constructor | `public Point { validate(); }` - runs before field assignment |
| Cannot extend | Classes (implicitly extends `java.lang.Record`) |
| Can implement | Interfaces |
| Generic records | `record Pair<T, U>(T first, U second) { }` |
| Nested records | `record Rectangle(Point tl, Point br) { }` |
| Record pattern | `if (r instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2)))` |
| `toString()` format | `Point[x=1, y=2]` |
| `equals()` | Compares all components |
| `hashCode()` | Based on all components |
| Mutable fields? | Fields are `final` by default |
| `@Override` in records | Can override accessors, equals, hashCode, toString |
| Annotation on record | Applies to class; use `@Target(RECORD_COMPONENT)` for fields |

## Sealed Classes

| Q | A |
|---|---|
| Sealed class syntax | `sealed class Shape permits Circle, Square { }` |
| Sealed interface | `sealed interface Shape permits Circle, Square { }` |
| Permitted subclass modifiers | `final`, `sealed`, `non-sealed` |
| Exhaustiveness checking | Compiler verifies all permitted types handled in switch |
| Same module requirement | Permitted subclasses must be in same module (or same package for `non-sealed`) |
| `non-sealed` | Opens hierarchy for unknown subclasses |
| Sealed + records | Perfect for Algebraic Data Types (Option, Result, Either) |
| Pattern matching switch | `switch (shape) { case Circle c -> ...; case Square s -> ...; }` |
| No default needed | When exhaustive on sealed type |
| Hierarchy depth | Multiple levels allowed (sealed permits sealed permits final) |

## Pattern Matching

| Q | A |
|---|---|
| `instanceof` pattern | `if (obj instanceof String s) { s.length(); }` |
| Switch expression | `String s = switch (x) { case A -> "a"; case B -> "b"; };` |
| Type pattern in switch | `case String s -> s.length();` |
| Record pattern | `case Point(int x, int y) -> ...` |
| Nested pattern | `case Rectangle(Point(int x, int y), Point p2) -> ...` |
| Guarded pattern | `case int i when i > 0 -> "positive"` |
| Null handling | `case null -> "null"` |
| Exhaustiveness | Required for sealed types; optional for open types |
| Dominance | More specific patterns before general ones |
| Variable scope | Pattern variables only in scope where pattern matches |

## Virtual Threads

| Q | A |
|---|---|
| Virtual thread creation | `Thread.startVirtualThread(() -> work())` or `Executors.newVirtualThreadPerTaskExecutor()` |
| Stack size | ~1KB initial (vs 1MB platform) |
| Startup time | ~1μs (vs ~1ms platform) |
| Carrier threads | ForkJoinPool (work-stealing) |
| Pinning causes | `synchronized`, native calls, FFI |
| Pinning fix | Use `ReentrantLock` instead of `synchronized` |
| `ThreadLocal` in VT | Works but not inherited; use `ScopedValue` |
| Structured concurrency | `StructuredTaskScope` for error handling + cancellation |
| `ShutdownOnFailure` | Cancels all on first failure |
| `ShutdownOnSuccess` | Cancels all on first success (racing) |
| Virtual thread count | Millions possible (limited by heap) |
| Debugging | `jstack` shows virtual threads with carrier info |
| Profiling | async-profiler supports VT; JFR has VT events |
| `Thread.ofVirtual()` | Builder API for custom VT factories |

## Structured Concurrency

| Q | A |
|---|---|
| `StructuredTaskScope` | Confines lifetime of subtasks to scope |
| `fork(Callable)` | Submits task, returns `Subtask<T>` |
| `join()` | Waits for all subtasks |
| `throwIfFailed()` | Propagates first exception |
| `ShutdownOnFailure` | Policy: cancel all on first failure |
| `ShutdownOnSuccess` | Policy: cancel all on first success |
| Custom policies | Implement `StructuredTaskScope` |
| Subtask states | `UNAVAILABLE`, `SUCCESS`, `FAILED` |
| `Subtask.get()` | Returns result or throws |
| Exception handling | First exception propagated, others suppressed |

## Pattern Matching Switch

| Q | A |
|---|---|
| Expression form | Returns value: `String s = switch(x) { case A -> "a"; }` |
| Statement form | No return: `switch(x) { case A -> System.out.println(); }` |
| Arrow syntax | `case A -> expr` (no fallthrough) |
| Colon syntax | `case A: stmt; break;` (fallthrough possible) |
| Multiple constants | `case A, B, C -> "letter"` |
| Guarded pattern | `case int i when i > 0 -> "positive"` |
| Null case | `case null -> "null"` |
| Default | Required for non-exhaustive; optional for sealed |
| Exhaustiveness | Compiler checks all cases covered for sealed types |
| Return type | Common supertype of all case expressions |

## String Templates (Preview)

| Q | A |
|---|---|
| Enable preview | `--enable-preview` (compile & run) |
| `STR` processor | Standard interpolation: `STR."Hello \{name}"` |
| `FMT` processor | Formatted: `FMT."Name: \{name:%-10s}"` |
| `RAW` processor | Raw template: `RAW."SELECT * FROM \{table}"` |
| Custom processor | Implement `StringTemplate.Processor<R>` |
| Template syntax | `\{expression}` in string literal |
| Fragment access | `template.fragments()` - static parts |
| Value access | `template.values()` - dynamic parts |
| Security | Processors can validate/sanitize (e.g., SQL) |
| Preview status | Java 21 preview, may change |

## Sequenced Collections

| Q | A |
|---|---|
| `SequencedCollection` | `addFirst`, `addLast`, `getFirst`, `getLast`, `reversed()` |
| `SequencedSet` | `SequencedCollection` + `Set` semantics |
| `SequencedMap` | `putFirst`, `putLast`, `firstEntry`, `lastEntry`, `reversed()` |
| Implementations | `LinkedHashSet`, `LinkedHashMap`, `ArrayDeque` (Deque already has) |
| `reversed()` view | Lightweight reverse view (not copy) |
| `newSequencedSetFrom` | Factory for unmodifiable sequenced set |
| Reverse iteration | `for (E e : set.reversed())` |

## Foreign Function & Memory API (Java 22+)

| Q | A |
|---|---|
| `MemorySegment` | Contiguous region of memory (heap or native) |
| `Arena` | Lifecycle scope for native memory (confined, shared, global) |
| `ValueLayout` | Primitive layouts: `JAVA_INT`, `JAVA_LONG`, `JAVA_DOUBLE`, `ADDRESS` |
| `MemoryLayout.structLayout` | Define C struct layout |
| `Linker` | Access native functions (`nativeLinker()`) |
| `downcallHandle` | Create MethodHandle for native function |
| `upcallStub` | Create function pointer for Java callback |
| `SymbolLookup` | Find native symbols (`defaultLookup()`, `libraryLookup()`) |
| `FunctionDescriptor` | Describe C function signature |
| Safety | Bounds checking, temporal safety via Arena |
| `try (Arena arena = Arena.ofConfined())` | Auto-free on close |

## Scoped Values

| Q | A |
|---|---|
| Creation | `ScopedValue<MyContext> CURRENT = ScopedValue.newInstance();` |
| Binding | `ScopedValue.runWhere(CURRENT, context, () -> work())` |
| Reading | `CURRENT.get()` (throws if unbound) |
| `isBound()` | Check if bound in current scope |
| Inheritance | Automatic to virtual threads and child threads |
| Immutability | Binding is immutable for scope duration |
| Nesting | `runWhere` creates nested binding |
| vs ThreadLocal | No memory leaks, automatic inheritance, immutable |
| Use case | Request context, transaction context, security context |

## Migration Patterns

| Legacy | Modern |
|--------|--------|
| POJO with getters/setters | `record` |
| `instanceof` + cast | `instanceof Type var` |
| `if-else` chains | `switch` expressions |
| Visitor pattern | Sealed + switch |
| `Optional` for nullable | Sealed `Option<T>` |
| Exception for control flow | `Result<T, E>` sealed |
| `ThreadLocal` in pools | `ScopedValue` |
| `synchronized` in VT code | `ReentrantLock` |
| Anonymous class | Lambda / record |
| `StringBuilder` in loop | `STR` template (preview) |