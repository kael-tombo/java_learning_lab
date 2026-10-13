# Why It Exists: JVM Tuning

Defaults must serve every workload from CLI tools to multi-GB servers,
so ergonomics derive from RAM and cores rather than guessing intent.
RAM/64 initial and RAM/4 maximum size a reasonable heap on unknown
hardware; ratios (NewRatio 2, SurvivorRatio 8) lay out a generational
geometry that suits average object demographics; TLABs and compressed
oops make the common paths (allocation, reference traffic) cheap without
asking. The flags exist because no derivation fits everyone: heaps,
pause goals, and capacity planes vary per deployment.

The tuning surface is deliberately layered. Explicit sizing (`-Xmx`,
`-Xms`) overrides derivation exactly for operators who know their box.
Collector choice (G1 default, ZGC opt-in, Parallel for batch shapes)
selects the pause/throughput posture wholesale — one flag, coherent
behavior change. Fine ratios and thresholds adjust within a posture for
measured cause (promotion pressure, survivor occupancy, marking lag).
Exotic flags sit last because each additional knob confounds the next
experiment and most fleets converge within three flags of default.

The one-flag method exists because JVM behavior is coupled: heap size
moves region sizes, worker counts, and thresholds simultaneously (labs
07-08 show both). Changing two flags per experiment makes results
unattributable. The discipline — objective, baseline logs, mechanism
hypothesis, single change, re-measure — is the only procedure that
produces transferable knowledge instead of cargo-cult flag lists.

The layering (explicit sizing, then collector, then ratios, then exotic
flags) is also a blast-radius ordering: earlier layers change behavior
coherently and reversibly, later layers interact and surprise. Teams that
respect the order get most of the win in the first three flags; teams
that start at the exotic end get most of the outages there too.

Container limits add a zeroth layer beneath sizing: the detected memory
that feeds every derivation must be read from the deployment, or the
whole stack above it optimizes for a machine the service never runs on.
Environment first, heap second, collector third — the order is the method
restated as a checklist.
