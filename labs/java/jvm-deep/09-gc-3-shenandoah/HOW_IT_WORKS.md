# How It Works: Shenandoah GC

Labels: [measured] ran on the Oracle JDK 23 here; [JEP] primary source;
[reported] downstream consumer, not re-measured.

Start by probing availability [measured]: `java -XX:+UseShenandoahGC
-version` exits nonzero with "not supported" on Oracle builds. On
Temurin/Semeru/RH builds the same probe exits zero with a `Using
Shenandoah` line. Either way the JVM answers deterministically —
availability is a build property checked at startup, never inferred from
version numbers.

On a build that ships Shenandoah, the cycle runs as follows [JEP]. `Pause
Init Mark` stops the world briefly to capture roots. Concurrent marking
then traverses the heap alongside the application while the SATB write
barrier logs every overwritten reference into buffers. Concurrent
precleaning handles weak references and class-unloading preparation.

`Pause Final Mark` drains the SATB buffers and finishes marking — the
largest routine beat because it reconciles the whole snapshot. Empty
regions reclaim immediately in concurrent cleanup. Then concurrent
evacuation copies live objects out of the collection set: each mover
copies and CASes the Brooks forwarder, application reads heal through
the forwarder to the winner's copy, and no rendezvous ever stops the
world for the copy itself.

Stale references to old copies remain scattered; init/final update-refs
pauses bracket a concurrent sweep that rewrites them to the new copies,
followed by a second concurrent cleanup [JEP]. Reference pause figures
(~1 ms init-mark, ~10 ms final-mark at 8 GB in the wiki log) scale with
root sets, not heap size [JEP].

The motivation is visible without Shenandoah present [measured]: identical
churn under G1 pauses in milliseconds while concurrent evacuation (ZGC
standing in) pauses in tens of microseconds — the order-or-better gap
Shenandoah closes from the Brooks-pointer direction.
