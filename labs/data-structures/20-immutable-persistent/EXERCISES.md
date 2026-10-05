# Exercises: Immutable & Persistent Data Structures

Implement from scratch in Java (no AI-written core logic). Trace each exercise on paper before coding; commit the trace as a comment.

## Beginner

1. **Immutable point**: Final class with withX/withY returning new instances; prove aliasing safety.
```java
// Lab 20-immutable-persistent: Immutable point
Point p2 = p1.withX(5); // p1 unchanged
```

2. **Persistent stack**: Cons-list push returns new head sharing tail; O(1) time/space per push.
```java
// Lab 20-immutable-persistent: Persistent stack
Stack<Integer> s2 = s1.push(3); // shares tail
```

3. **Versioned map**: assoc returns new root via path copying on a BST; keep v0..vk readable.
```java
// Lab 20-immutable-persistent: Versioned map
VMap m2 = m1.assoc(k, v); assert m1.get(k)...;
```

## Intermediate

4. **Undo timeline**: Editor buffer with version list; undo/redo = pointer moves, no copying.
```java
// Lab 20-immutable-persistent: Undo timeline
history.undo(); assert text.equals(before);
```

5. **Transient batch**: Mutable builder for bulk load then freeze to immutable; bench vs per-op assoc.
```java
// Lab 20-immutable-persistent: Transient batch
Transient t = ...; t.add(x); Immutable c = t.freeze();
```

6. **Diff versions**: Walk two roots reporting changed keys only; O(d log n).
```java
// Lab 20-immutable-persistent: Diff versions
diff(v3, v7); // expect changed keys only
```

## Advanced

7. **Fat-node spike**: Single tree with version-stamped fields; query asOf(v).
```java
// Lab 20-immutable-persistent: Fat-node spike
node.read(field, version); // stamp check
```

8. **GC pressure bench**: Compare node churn: persistent updates vs mutable at 100k ops (JFR alloc).
```java
// Lab 20-immutable-persistent: GC pressure bench
// record allocation rate per op
```

## Traces and checks
- Commit one ASCII hand-trace per exercise (state before/after the hot path).
- Invariant holds after every op; trace matches execution or the exercise fails.

## Grading rubric

- Correctness 40 / hand traces 20 / edge-case tests 20 / benchmark note 20.

## How to work this set

- Timebox: Beginner 25 min, Intermediate 40 min, Advanced 60 min.
- Write the trace first; code second; fuzz last.
- If stuck more than 20 min, shrink the input to n = 3 and re-trace.

## Common wrong turns

- Skipping the hand trace and debugging blind against failing tests.
- Testing only sorted/insertion-order input; adversarial order finds the real bugs.
- Forgetting the empty and singleton cases in every new operation.
- Measuring performance without warmup and reporting noise as signal.

## Stretch

- S1. Swap one core design choice (array vs map, iterative vs recursive) and re-benchmark.
- S2. Write the 5-line lesson-learned note: what broke, what fixed it, what to check first next time.

## Done when

- [ ] 8/8 exercises green with committed traces
- [ ] Fuzz run clean for 10k random ops against the naive model
- [ ] Benchmark table filled at n = 1k / 10k / 100k
