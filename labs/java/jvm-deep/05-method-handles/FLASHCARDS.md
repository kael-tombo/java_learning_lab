# FLASHCARDS — Method Handles & invokedynamic

| # | Front | Back |
|---|-------|------|
| 1 | `MethodHandles.lookup()` returns? | `Lookup` with caller's access rights |
| 2 | `MethodType` describes? | `(paramTypes...)returnType` |
| 3 | `findVirtual` vs `findStatic`? | Virtual: instance method (receiver first). Static: static method (no receiver). |
| 4 | `bindTo(x)`? | Curries first arg: `(A,B)->R` + `bindTo(a)` → `(B)->R`. |
| 5 | `asSpreader` vs `asCollector`? | Spreader: array→args. Collector: args→array. |
| 6 | `asSpreader` vs `asCollector`? | Spreader: array→args. Collector: args→array. |
| 7 | `invokedynamic` bootstrap? | Static method called once per call site to create CallSite. |
| 8 | `ConstantCallSite` vs `MutableCallSite`? | Constant: immutable target. Mutable: target can change. |
| 9 | `LambdaMetafactory.metafactory` bootstrap? | Creates CallSite for lambda; static args: functional interface, impl method, instantiated type. |
| 10 | `bindTo(x)`? | Curries first arg: `(A,B)->R` + `bindTo(a)` → `(B)->R`. |
| 11 | `asSpreader` vs `asCollector`? | Spreader: array→args. Collector: args→array. |
| 12 | `guardWithTest`? | If test passes, call target; else fallback. |
| 13 | `asSpreader` vs `asCollector`? | Spreader: array→args. Collector: args→array. |
| 14 | `filterArguments`? | Transforms args before calling target. |
| 15 | `LambdaMetafactory.metafactory` bootstrap? | Creates CallSite for lambda; args: functional interface, impl method, instantiated type. |
| 16 | `MethodHandle.bindTo(x)`? | Curries first arg: `(A,B)->R` + `bindTo(a)` → `(B)->R`. |
| 17 | `asSpreader` vs `asCollector`? | Spreader: array→args. Collector: args→array. |
| 18 | `invokedynamic` bootstrap? | Static method called once per call site to create CallSite. |
| 19 | `MethodHandle.bindTo(x)`? | Curries first arg: `(A,B)->R` + `bindTo(a)` → `(B)->R`. |
| 20 | `asSpreader` vs `asCollector`? | Spreader: array→args. Collector: args→array. |