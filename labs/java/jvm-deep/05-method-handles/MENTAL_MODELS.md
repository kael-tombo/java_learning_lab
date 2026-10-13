# Mental Models: Method Handles

## 1. Handles as power-of-attorney documents

A `Lookup` is the notary verifying identity *once*: it checks you
may act on the account (access rights) and issues a signed document
(the handle) naming exact powers (`MethodType`). Every later use
just presents the document — no re-verification (unlike reflection,
which calls the notary per transaction). Forged powers
(`invokeExact` with wrong static types) are rejected at presentation
(`WrongMethodTypeException`), never honored partially.

## 2. Constructors as void forms that return buildings

The constructor lookup form reads `(int)V` — "takes an int, returns
nothing" — because constructors initialize rather than return. The
issued handle reads `(int)ArrayList`: the completed building handed
over after the form is processed. Same transaction, two framings —
the form's wording (void) and the outcome's (a reference). The
earlier THEORY erratum wrote the outcome on the form; the form
accepts only void.

## 3. bindTo vs insertArguments as reserved vs general seating

`bindTo` reserves the head seat for a named guest — who must be a
person (reference), never a number. `insertArguments` is general
admission: it seats anyone, boxing numbers into guest passes. Both
narrow the handle's type identically (`(int,int)int` → `(int)int`);
only the admission rule differs.

## 4. guardWithTest as a railroad switch

One handle, two tracks: the test lever reads the leading car(s) and
throws the switch; the full train then runs the chosen track
(`add` or `mul`, both taking every car). The switch + both tracks
are one welded unit to the JIT — a junction, not three separate
railways. Miswiring (test eating the whole train, arms fed the
tail) derails at link time, stating the expected consist in the
composed type.

## 5. Call sites as phone-number forwarding

`ConstantCallSite` is a number ported permanently — callers dial,
the exchange routes direct, no forwarding record consulted again
(the JIT deletes the indirection). `MutableCallSite` is
call-forwarding you can change: one `setTarget` update reroutes
every future caller (volatile-published). `VolatileCallSite`
re-reads the forwarding card per call. Same handset
(`dynamicInvoker`), three service plans.

## 6. invokeExact vs invoke as exact-change vs cashier

`invokeExact` is exact-change-only: the stamped denominations must
match the price (`MethodType`) precisely, or the machine rejects the
payment at the slot. `invoke` is a cashier making change (`asType`
conversions) — convenient, slightly slower, and inside generic code
the wallet holds only large bills (`Object` erasure) needing
breakdown first.
