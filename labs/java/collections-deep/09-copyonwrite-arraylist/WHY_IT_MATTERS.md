# Why Copy-on-Write Matters

## Where it shows up

- **Event listener lists**: Swing models, bean property-change support,
  Netty pipeline handler lists — register-rarely/notify-constantly with
  reentrant callbacks.
- **Dynamic configuration**: a service swaps a config object on reload;
  thousands of request threads read the current snapshot with zero locking.
  (Often `volatile List` + copy idiom directly; COW is the packaged form.)
- **Routing/allowlist tables**: IP allowlists, feature
  flags reloaded periodically, read per request.

## What goes wrong without it

Hand-rolled `synchronizedList` + "iterate under lock" deadlocks when a
callback reenters; "iterate over a copy" (clone per notify) reinvents COW
worse — paying O(n) per *read* instead of per *write*. `ConcurrentHashMap`
newKeySet covers membership but not ordered indexed reads.

## The misuse that matters more

COW in a write-heavy path (per-request appends, growing buffers) shows up
in profiles as GC churn with no obvious hot method — allocation is spread
across tiny copies. Recognizing "this list copies per write" from a
flat-but-fat allocation profile is the diagnostic skill this lab builds.

## Interview signal

Expect: "how do iterators avoid CME?", "why does set() publish on equal
values?", "COW vs synchronizedList?", "what does addIfAbsent do under the
lock?". All four are one mechanism deep: versions + volatile + recheck.
