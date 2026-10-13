# Exercises: Shenandoah GC

Nothing here pretends to run Shenandoah on the Oracle build. Each task
asserts about probe outcomes ([measured]) or reads primary sources
([JEP]/[reported]). Join `-Xlog` tags with `+`.

## 1. Prove the refusal branch [measured]

```bash
java -XX:+UseShenandoahGC -version; echo "rc=$?"
```

Record exit code (reference: 1) and the "not supported" text. Assert
`supported != refused` with exactly one side true. State the corollary:
availability is a build property, never inferred from the version number.

## 2. Count the surviving surface [measured]

```bash
java -XX:+PrintFlagsFinal -version | grep -c "Shenandoah.* = "
java -XX:+PrintFlagsFinal -version | grep -cE "G1[A-Z].* = "
```

Expect 1 versus >5. Write the one-sentence conclusion: the tuning
surface (`ShenandoahGCMode`, `ShenandoahPacing`, `ShenandoahUncommit*`)
compiled out with the collector (`#ifdef INCLUDE_SHENANDOAHGC`, JEP 189
CSR). Predict what both counts print on a Temurin build.

## 3. Measure the gap Shenandoah closes [measured]

```bash
javac ChurnXY.java
java -Xmx128m -Xlog:gc* -cp . ChurnXY
java -XX:+UseZGC -Xmx128m -Xlog:gc* -cp . ChurnXY
```

Using the lab's `PauseGap` probe (dual regexes: ZGC handshake pattern
plus `G1 Evacuation Pause` pattern): assert both maxima >0 and
`zgc_max * 10 < g1_max` (reference gap ~100x: ~5 ms vs ~0.02 ms). Label
the inference [JEP]: this is the evacuation-cost gap concurrent
evacuation removes.

## 4. Enumerate, never hardcode [measured + reported]

```bash
javac WhoAmI.java
java -cp . WhoAmI
java -XX:+UseZGC -cp . WhoAmI
```

Confirm `G1` on default, `ZGC` under the opt-in. Then open Micrometer's
`JvmGcMetrics` source and find `"Shenandoah Cycles"` / `"... Pauses"`
([reported]); write the matcher change your dashboard needs so all three
collectors resolve.

## 5. Read the JEP trail directly [JEP]

Open JEP 189 (concurrent-evacuation claim + G1 contrast quote), JEP 379
(production, G1 stays default), JEP 404/521 (generational experimental /
single-gen default quote). For each, copy one sentence into your notes
with its JEP number — no paraphrase without attribution.

## 6. Confirm warmup universality [measured]

```bash
javac ZChurn.java
java -Xmx256m -Xlog:gc -cp . ZChurn
java -XX:+UseZGC -Xmx256m -Xlog:gc -cp . ZChurn
```

Verify G1 young work at startup and ZGC's `Major Collection (Warmup)`.
State the Shenandoah analogue [JEP]: `Pause Init Mark` opens its cycles
the same commissioning way on shipping builds — startup collection is
universal, never pressure.
