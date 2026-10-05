# Flashcards — Streams & Optional

| Q | A |
|---|---|
| stream()? | Sequential pipeline |
| parallelStream? | ForkJoin parallel |
| map? | 1:1 transform |
| filter? | Keep matching |
| flatMap? | Map+flatten |
| distinct? | Dedup (stateful) |
| sorted? | Sort (barrier) |
| peek? | Debug side-effect |
| limit(n)? | First n |
| skip(n)? | Drop n |
| takeWhile? | Prefix while true |
| dropWhile? | Drop prefix |
| forEach? | Terminal consume |
| forEachOrdered? | Ordered consume |
| collect? | Mutable reduction |
| reduce? | Immutable fold |
| count/sum/avg? | Summarizing |
| min/max? | Optional result |
| findFirst? | First element |
| findAny? | Any (parallel) |
| anyMatch? | Exists short-circuit |
| allMatch? | All short-circuit |
| noneMatch? | None short-circuit |
| toList? | Unmodifiable list |
| toSet? | Set collect |
| toMap? | Map + merge fn |
| groupingBy? | Group to map |
| partitioningBy? | Boolean split |
| counting? | Count downstream |
| summingInt? | Sum downstream |
| joining? | String concat |
| teeing? | Two collectors merge |
| summarizing? | Stats bundle |
| mapping? | Map downstream |
| filtering? | Filter downstream |
| flatMapping? | Flat downstream |
| Custom collector? | supplier/acc/comb/fin |
| Characteristics? | CONCURRENT/UNORDERED/IDENTITY |
| Spliterator? | TrySplit+fast path |
| trySplit? | Halve for parallel |
| Stream<Long> box? | Boxing overhead |
| mapToLong? | Primitive stream |
| boxed? | Primitive→object |
| range? | IntStream.range |
| rangeClosed? | Inclusive end |
| generate? | Infinite supplier |
| iterate? | Seed+unary |
| Optional.of? | Non-null wrap |
| ofNullable? | Nullable wrap |
| empty? | Empty opt |
| isPresent? | Has value (avoid) |
| ifPresent? | Consume if set |
| ifPresentOrElse? | Both branches |
| map opt? | Transform if set |
| flatMap opt? | Chain optionals |
| filter opt? | Keep if pred |
| or? | Alt optional |
| orElse? | Eager default |
| orElseGet? | Lazy default |
| orElseThrow? | Throw if empty |
| stream opt? | Opt→0/1 stream |
| get()? | Avoid, throws |
| Param Optional? | Smell, overload |
| Field Optional? | Smell, nullable |
| Return Optional? | Good for find |
| Parallel common pool? | ForkJoin.commonPool |
| Custom pool? | Submit with pool |
| Thread-safe collect? | groupingByConcurrent |
| Order parallel? | forEach unordered |
| Gatherer? | Custom intermediate |
| Window gather? | Sliding window |
| Reuse stream? | IllegalStateException |
| Lazy proof? | peek not run w/o terminal |
