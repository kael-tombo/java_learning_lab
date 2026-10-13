# Mental Models: Bytecode Introduction

## 1. The stack as a cafeteria tray line

Locals are labeled trays on the shelf (`iload_1` picks up tray 1).
The counter is the operand stack: each cook (`iadd`) takes the top
two plates, combines them, and puts one back. `istore_3` shelves the
result. Nobody names a burner — the line position *is* the address.

## 2. Five invokes as five phone systems

`invokestatic` dials a saved number. `invokespecial` dials family —
private lines and the constructor's unlisted number, answered
directly. `invokevirtual` calls a company switchboard (vtable) that
routes to whoever currently holds the extension. `invokeinterface`
calls an industry directory (itable) — slower lookup, works across
companies. `invokedynamic` dials an operator (bootstrap) once, who
patches you a direct line you keep.

## 3. Descriptors as customs declarations

The descriptor `(II)I` declares "two ints in, one int out" the way a
customs form declares contents. Border control (linkage) matches
forms, not intentions: `List<String>` and `List<Integer>` file
identical `List` forms (erasure), and any mismatch impounds the
shipment (`NoSuchMethodError`).

## 4. Frames as trail signs at junctions

The verifier hikes every path; at each junction a `StackMapTable`
sign states the expected party (locals) and packs (stack). Straight
trail needs no signs. `same_frame` reads "no change"; `append_frame`
"pickups joined"; `chop_frame` "drop-offs left"; `full_frame` the
complete roster. A wrong sign stops the hike (`VerifyError`).

## 5. invokedynamic as a patched hotline

First call goes through the operator (`LambdaMetafactory`), who
welds a direct wire to a cached `lambda$...` room. Every later call
uses the wire. The operator's fee is paid once; conversation after
is full speed. Capturing lambdas additionally courier a parcel
(instance) per call — the wire stays, the parcels repeat.

## 6. invokeExact as a typed keycard

The handle's `MethodType` is a lock; `invokeExact` is a keycard cut
to exact bittings (static types). A near-match card (`String` where
`double` is cut) is rejected at the door
(`WrongMethodTypeException`), never inside. `invoke` is the reception
desk that cuts adapters (`asType`) for legitimate near-matches.
