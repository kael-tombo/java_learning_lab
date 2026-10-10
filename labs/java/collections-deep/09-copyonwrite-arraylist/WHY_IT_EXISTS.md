# Why CopyOnWriteArrayList Exists

The listener problem: a component holds registered listeners; on every
event it iterates and notifies. Listeners register rarely, events fire
constantly, notification happens on hot threads — and a listener that
unregisters *during* notification (from inside its own callback) must not
break the loop.

`synchronizedList` fails this three ways: iteration needs external locking
(the callback reentrancy deadlocks or CMEs), every read pays lock overhead
on the hottest path, and concurrent register-during-notify throws
`ConcurrentModificationException`.

COW buys the exact contract needed:

- notify-iteration is a free snapshot — reentrant unregister is safe, no
  CME is even possible (no modCount exists);
- reads cost one volatile load — negligible on event-hot paths;
- registration (rare) pays O(n) copy — invisible at low frequency.

The structure is a confession that reads outnumber writes ~1000:1 in this
niche, and it spends write budget lavishly to make reads nearly free. Use
it anywhere that ratio holds: listeners, config snapshots, routing tables.
Anywhere else, it is the wrong structure — deliberately so.
## The reentrancy win, concretely

Listener-callback unregistration during notification is the sharpest case:
under `synchronizedList`, the notifying thread holds the lock while
calling out — a callback that unregisters reenters the lock ( deadlock
with non-reentrant use, CME with fail-fast iteration). Under COW, the
notifier walks a private version with no lock held: unregister publishes a
new version the current walk never sees, and the next notification uses it.
No deadlock, no CME, no defensive copy per event — the version chain
absorbs reentrancy by construction.
