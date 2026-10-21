# Common Mistakes

## 1. Over-Engineering

Adding unnecessary abstraction layers and patterns. Follow YAGNI — add complexity only when current requirements demand it.

## 2. Under-Engineering

Writing everything inline without structure. Apply the Single Responsibility Principle — if a method does more than one thing, extract it.

## 3. Ignoring Edge Cases

Only handling the happy path. Always test: null inputs, empty collections, negative numbers, max/min values, zero, and error conditions.

## 4. Tight Coupling

Hard-coding dependencies instead of injecting them. Constructor injection makes dependencies explicit and enables testing.

## 5. Mutable State Exposure

Returning internal collections or arrays without defensive copies. Always use Collections.unmodifiableList() or clone arrays.

## 6. Inadequate Error Handling

Catching generic exceptions or swallowing errors. Log with context. Let exceptions propagate to appropriate handlers.

## 7. Premature Optimization

Optimizing before profiling. Most guesses about performance bottlenecks are wrong. Measure first, optimize second.

## 8. Not Using Existing APIs

Reimplementing functionality already in the JDK. Check java.util, java.io, java.nio, java.time, and java.util.concurrent first.

## Prevention Checklist

- Does each class have a single responsibility?
- Are dependencies injected, not hard-coded?
- Are edge cases handled?
- Is internal state protected?
- Are errors logged with context?
- Have you profiled before optimizing?
