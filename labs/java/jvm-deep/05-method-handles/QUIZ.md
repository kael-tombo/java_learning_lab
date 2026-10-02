# QUIZ — Method Handles & invokedynamic

## 1. What does `MethodHandles.lookup()` return?
<details><summary>Answer</summary>A `Lookup` object with the access permissions of the caller's class.
</details>

## 2. What is a `MethodType`?
<details><summary>Answer</summary>Describes a method signature: `(parameterTypes...)returnType`. Immutable.
</details>

## 2. Difference between `findVirtual` and `findStatic`?
<details><summary>Answer</summary>`findVirtual`: instance method (receiver first arg). `findStatic`: static method (no receiver).
</details>

## 3. What does `MethodHandle.bindTo(x)` do?
<details><summary>Answer</summary>Binds first argument to `x` (currying). `(A,B)->R` + `bindTo(a)` → `(B)->R` where first arg is fixed to `a`.
</details>

## 3. What is `asSpreader`?
<details><summary>Answer</summary>Converts array argument to spread arguments: `(A[]) -> R` becomes `(A,A,A) -> R`.
</details>

## 4. What is `asCollector`?
<details><summary>Answer</summary>Opposite of `asSpreader`: collects multiple arguments into array. `(A,A,A) -> R` becomes `(A[]) -> R`.
</details>

## 4. What is `MethodHandle.bindTo(x)`?
<details><summary>Answer</summary>Curries first argument: `(A,B)->R` + `bindTo(a)` → `(B)->R` where A=a fixed.
</details>

## 5. What does `asSpreader` do?
<details><summary>Answer</summary>Converts array argument to spread arguments: `(A[]) -> R` becomes `(A,A,A) -> R`.
</details>

## 5. What is `invokedynamic`?
<details><summary>Answer</summary>JVM instruction for dynamic method invocation; bootstrap method links call site to target MethodHandle.
</details>

## 5. What is `invokedynamic`?
<details><summary>Answer</summary>JVM instruction for dynamic method invocation; bootstrap method links call site to target MethodHandle.
</details>

## 6. What are the three CallSite types?
<details><summary>Answer</summary>`ConstantCallSite` (immutable), `VolatileCallSite` (volatile target), `MutableCallSite` (mutable target).
</details>

## 6. What is a CallSite?
<details><summary>Answer</summary>Holder for a MethodHandle target; `invokedynamic` links to a CallSite whose target can be invoked.
</details>

## 7. What is a bootstrap method?
<details><summary>Answer</summary>Static method called once per `invokedynamic` site to create the CallSite; receives Lookup, name, MethodType, static args.
</details>

## 7. What is a bootstrap method?
<details><summary>Answer</summary>Static method called once per `invokedynamic` to create the CallSite; receives Lookup, name, MethodType, static args.
</details>

## 8. What is `MethodHandle.bindTo(x)`?
<details><summary>Answer</summary>Curries first argument: `(A,B)->R` + `bindTo(a)` → `(B)->R`.
</details>

## 8. What is `asSpreader` vs `asCollector`?
<details><summary>Answer</summary>`asSpreader`: array → spread args. `asCollector`: multiple args → array.
</details>

## 8. What is `asSpreader`?
<details><summary>Answer</summary>Converts array argument to spread arguments: `(A[]) -> R` → `(A,A,A) -> R`.
</details>

## 9. Lambda → invokedynamic: what's the bootstrap?
<details><summary>Answer</summary>`LambdaMetafactory.metafactory` — creates `CallSite` with target MethodHandle for lambda body.
</details>

## 9. What is `LambdaMetafactory.metafactory`?
<details><summary>Answer</summary>Bootstrap method for lambdas; creates CallSite with lambda implementation as target.
</details>

## 10. `MethodHandle.bindTo(x)` does what?
<details><summary>Answer</summary>Curries first argument: `(A,B)->R` + `bindTo(a)` → `(B)->R`.
</details>

## 10. What does `MethodHandles.filterArguments` do?
<details><summary>Answer</summary>Transforms arguments before calling target: `(A,B)->R` + filter on arg 0 → `(A',B)->R`.
</details>