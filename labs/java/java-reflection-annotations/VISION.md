# Vision — Reflection & Annotations

## Direction
- Compile-time processing (annotation processors, AOT) preferred over runtime scan.
- Frameworks move to build-time metadata (Micronaut/Quarkus) for startup + native.
- Records/patterns reduce need for deep reflection.

## 5-Year Bets
1. Runtime classpath scanning disappears from new frameworks.
2. MethodHandles + hidden classes replace Unsafe hacks.
3. Native-image constraints push explicit registration over reflection.

## Constants
- Cache reflective handles; fail fast on missing opens.
- Prefer explicit SPIs over magic scanning.

## Signals
- GraalVM reachability metadata, Leyden AOT JEPs.
- Processor + codegen libs (JavaPoet, ByteBuddy).

## Career
Metaprogramming + AOT knowledge → framework/platform roles. Ship validator.

## Anti-Vision
Don't build reflection-heavy "magic" frameworks — debugging hell.
Explicit > clever.

## 30/60/90
- 30d: annotations + proxies + handles.
- 60d: processor + mini-DI.
- 90d: hardened validator framework.
