# Flashcards — JVM Deep

| Q | A |
|---|---|
| javap -c? | Disassemble bytecode |
| aload/iload? | Load ref/int local |
| invokevirtual? | Virtual dispatch |
| invokespecial? | Private/ctor/super |
| invokestatic? | Static call |
| invokedynamic? | Lambda/indy site |
| goto/if_icmp? | Branch ops |
| Bootstrap loader? | jdk.internal (null) |
| Platform loader? | java.sql etc |
| App loader? | Classpath |
| Delegation? | Parent-first |
| Child-first? | Plugin isolation |
| NoClassDefFound? | Runtime missing dep |
| LinkageError? | Duplicate/split |
| C1? | Client quick JIT |
| C2? | Server optimizer |
| Tiered? | 0 interp→1 C1→4 C2 |
| PrintCompilation? | JIT method log |
| PrintInlining? | Inline decisions |
| Monomorphic? | One receiver → direct |
| Bimorphic? | Two → inline cache |
| Megamorphic? | Many → vtable |
| Deopt? | Uncommon trap |
| Escape analysis? | Stack alloc/elide lock |
| On-stack replace? | OSR for long loops |
| Safepoint? | Stop-the-world point |
| TTSP? | Time to safepoint |
| G1 region? | 1-32MB chunks |
| Eden? | New alloc |
| Survivor? | Aged survivors |
| Tenured? | Old gen |
| Humongous? | >50% region object |
| Mixed GC? | Young+old reclaim |
| Full GC? | Last resort compact |
| ZGC pause? | ~1ms |
| Colored ptr? | Metadata in ref |
| Load barrier? | Check on load |
| Shenandoah? | Brooks ptr evac |
| Parallel GC? | Stop-world throughput |
| Serial GC? | Single-thread tiny |
| Xmx/Xms? | Max/init heap |
| Xss? | Thread stack |
| Metaspace size? | MaxMetaspaceSize cap |
| Direct cap? | MaxDirectMemorySize |
| NMT? | VM.native_memory |
| JFR start? | jcmd JFR.start |
| JFR dump? | JFR.dump filename |
| FlightRec? | jdk.jfr events |
| async-prof? | Sampling profiler |
| Heap dump? | jmap -dump:live |
| MAT? | Dominator analysis |
| Dominator? | Retains subtree |
| Leak suspect? | Static cache/listener |
| WeakRef? | GC-collectable ref |
| SoftRef? | Memory-sensitive cache |
| Phantom+Queue? | Post-mortem cleanup |
| Finalizer evil? | Unpredictable; use Cleaner |
| Cleaner API? | java.lang.ref.Cleaner |
| CDS archive? | AppCDS startup |
| AOT cache? | Leydenauzubin |
| TieredStopAtLevel? | Cap JIT level |
| CICompilerCount? | JIT threads |
| ReservedCodeCache? | Code cache size |
| CodeCache full? | JIT stops, slowdown |
