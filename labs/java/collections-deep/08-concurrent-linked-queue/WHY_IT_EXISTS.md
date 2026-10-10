# Why ConcurrentLinkedQueue Exists

A `synchronized` queue serializes producers against consumers: a producer
adding while a consumer polls waits on the same monitor, and a thread that
dies holding the lock stalls everyone. Work-stealing schedulers, event
buses, and producer/consumer pipelines need the opposite — threads that
never block each other, with progress guaranteed as long as *any* thread
runs.

The Michael–Scott design buys exactly that:

- one CAS per op instead of a monitor enter/exit pair — no descheduling,
  no convoying, no lock-holder preemption stalls;
- lagging head/tail so pointer maintenance doesn't serialize appends;
- wait-free-*ish* reads (`peek` never CASes) alongside lock-free writes.

What it deliberately omits: bounds (unbounded — memory is the bound),
blocking (`poll` returns null instead of waiting), and exact `size`.
Those belong to `LinkedBlockingQueue`/`ArrayBlockingQueue`. CLQ is the
tool for "hand off work between threads at maximum throughput and never
block" — the narrow contract that lets the implementation stay this
simple.
## The progress guarantee, precisely

Lock-free means CAS-failure implies someone else's CAS succeeded — every
retry round completes somebody's operation, so the system never wedges no
matter how threads are scheduled or preempted. A lock holder preempted
mid-critical-section stalls all waiters; a CAS thread preempted mid-offer
stalls nobody (its node simply isn't linked yet, and others proceed past
it). That scheduling-immunity — not raw speed — is why schedulers and
event buses build on CLQ: progress under adversarial scheduling.
