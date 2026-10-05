# Quiz — Streams & Optional (20 Q)

1. Intermediate vs terminal?
> Lazy transforms vs eager trigger.
2. Why lazy?
> Fuse ops, short-circuit, no work until needed.
3. Stateless vs stateful op?
> map/filter vs sorted/distinct (barrier).
4. findFirst vs findAny?
> First stable vs any (parallel faster).
5. orElse vs orElseGet?
> Eager vs lazy default supplier.
6. Optional.of vs ofNullable?
> Non-null vs nullable wrap.
7. orElseThrow use?
> Fail with supplier exception.
8. groupingBy downstream?
> e.g. groupingBy(k, counting()).
9. partitioningBy?
> Two groups by predicate.
10. toMap merge fn?
> Resolve dup keys.
11. flatMap vs map?
> Flatten nested streams.
12. Parallel pitfall #1?
> Shared mutable state.
13. Spliterator role?
> Split + traverse for parallel.
14. LongStream vs Stream<Long>?
> No boxing, faster.
15. reduce identity?
> Neutral element (0, "").
16. Combiner needed?
> Merge partial parallel results.
17. sorted() cost?
> O(n log n) barrier.
18. peek use?
> Debug only, not logic.
19. Optional as field?
> Avoid; use nullable + validate.
20. Stream reuse?
> Single-use; recreate per terminal.
