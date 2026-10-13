# Common Mistakes: Shenandoah GC

## 1. Assuming Shenandoah exists because the version is new [measured]

Oracle builds omit it at every version measured; only the probe answers.
"JDK 23, therefore Shenandoah" is the most common false premise — probe,
don't assume (snippet 1).

## 2. Copying tuning flags onto unsupported builds [measured]

`ShenandoahGCMode`, `ShenandoahPacing`, `ShenandoahUncommit*` are absent
where the collector is compiled out (exactly 1 surviving flag). Pasted
flags are silently ignored at best — snippet 2 counts the surface before
any tuning sentence is uttered.

## 3. Presenting unmeasured behavior as observed

Every Shenandoah-behavior sentence needs its label: [JEP] for the
algorithm and phases, [reported] for Micrometer MXBean names, [measured]
for the Oracle-build probes and the G1/ZGC gap. Dropping the label turns
documentation into a false observation report.

## 4. Conflating Brooks pointers with colored pointers [JEP]

Forwarder word in the object versus color bits in the reference; read
barrier plus SATB/CAS versus load-barrier healing. Different tax shapes,
same concurrent-evacuation goal (THEORY table). Mixing them up misplaces
every performance prediction about read-heavy versus load-heavy shapes.

## 5. Reading cycle totals as pauses [measured]

Concurrent spans log in seconds; STW handshakes log as `Pause ... Xms`.
Snippet 3's dual regexes exist because one pattern misreads the other
collector by 1000x. The mistake transfers unchanged from labs 07-08.

## 6. Hardcoding collector or pool names [measured+reported]

Monitoring that matches only `G1 Young Generation` goes blind on ZGC
(snippet 4 proves the flip) and on Shenandoah's `Shenandoah Cycles` /
`Pauses` pair [reported]. Enumerate beans; never hardcode one collector.

## 7. Treating warmup collections as pressure [measured]

First-cycle majors and young pauses are commissioning on every collector
(snippet 5: G1 young work plus ZGC warmup major on identical churn).
Shenandoah's `Pause Init Mark` opens the same way on shipping builds
[JEP]. Paging on commissioning is triage noise.
