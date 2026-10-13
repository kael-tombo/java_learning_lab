# How It Works: Method Handles

## 1. Lookup checks rights and mints a typed reference

`MethodHandles.lookup()` captures your access context
(caller-sensitive: sees what your class sees). `findStatic`,
`findVirtual`, `findConstructor`, `findGetter`/`findSetter` each
verify existence, exact `MethodType`, and accessibility *now* —
including the final-field setter rejection and the constructor-void
rule (`(int)V` in, `(int)ArrayList` handle out). The returned handle
carries no further permission logic; invocation is pure execution.

## 2. MethodType is the whole contract

`(double)double`, `(String,int,int)String`, `(Point,int)void` —
return plus parameters, primitives exact, receiver first for
instance handles. `invokeExact` compares the call site's compiler-
stamped static types against this contract at link time; `invoke`
rewrites through `asType` conversion rules (boxing, casting,
widening) first. Erasure can stamp `Object` where the contract wants
`int` — the generic-helper trap, resolved by an explicit `asType`
view.

## 3. Combinators wire handles into programs

`insertArguments(add, 0, 40)` curries the primitive first arg
(`bindTo` would need a reference). `filterArguments(add, 0, dbl)`
routes arg 0 through `dbl` before `add` sees it. `guardWithTest(big,
add, mul)` builds the if-else: test consumes the leading arg(s),
both arms consume everything, the composed type equals the arm type.
`asSpreader`/`asCollector` reshape between flat and array forms.
Each combinator returns a plain handle — nestable, JIT-visible as
one unit.

## 4. Bootstrap links dynamic sites once

`invokedynamic` names a bootstrap (`LambdaMetafactory.metafactory`
for lambdas) plus static discriminators. First execution calls the
bootstrap with caller lookup, site name, full type, and static args;
it returns a `CallSite` whose target handle (e.g., to a generated
`lambda$...` body) becomes the site's linkage. Later executions jump
to the target — the dynamism budget spent once.

## 5. Call-site kinds set the relinking contract

`ConstantCallSite` folds forever (JIT: direct call) — lambda and
concat sites. `MutableCallSite.setTarget` re-points all callers
(volatile semantics — guards, caches, redefinition). A
`dynamicInvoker()` handle exposes the current target through the
same `invokeExact`/`invoke` strictness as any handle. Same call
shape, opposite linkage promises — snippet 4 runs both side by side.

## 6. Warm handles run at direct-call speed

Cold: linkage check + bind. Warm: JIT inlines through the handle
(and through constant sites entirely), primitives unboxed end to
end, no per-call access check. The cost table's ordering — direct ≈
warm handle ≪ reflection — is why frameworks migrated dispatch
internals onto handles after Java 7.
