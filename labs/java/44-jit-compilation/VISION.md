# VISION — JIT Compilation Deep Dive

## Vision Statement
**Warm code is different code** — C1/C2 tiers, inlining, and
deoptimization mean steady-state performance is earned: measure warm,
read the assembly, and stop fighting the compiler with cleverness.

---
## Mental Models
### 1. Tiered Compilation Ladder
0 interpreted → C1 quick → C2 optimized (profile-guided). Flags
`-XX:+PrintCompilation` / JFR `CompilerInlining` narrate the climb.
### 2. Profiling Drives Speculation
Monomorphic call → inlined guard; megamorphic → virtual dispatch.
Uncommon traps + deopt (`made not entrant`) when the bet is wrong.
### 3. Escape Analysis Removes Allocation
Non-escaping objects scalar-replace away. Small methods inline
better — size limits (`MaxInlineSize`) are performance law.
### 4. Warmup Is Measurement Protocol
First 10k iterations lie. JMH with forks/warmups is the only fair
fight; `-Xint` vs tiered shows the gap.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Optimize? | JFR + async-profiler top frames first |
| Inline-critical? | Small, final, monomorphic, hot (9+ threshold) |
| Deopt storm? | Stop reflective/megamorphic shape flips |
| Startup vs peak? | CDS/AppCDS + tiered for start; C2 for peak |

---
## Career Trajectory
- **L1:** Warmup discipline, JMH basics, PrintCompilation reading.
- **L2:** Inlining failures,CHA/devirt, escape-analysis wins.
- **L3:** PerfAsm reading, deopt forensics, intrinsics (System.arraycopy etc).
- **L4:** Compiler-aware API design, startup/peak tradeoff governance.

---
## 4-Week Path
```
W1: JMH harness + warmup kata; PrintCompilation timeline reading.
W2: Inlining lab — final/mono vs mega; size-limit demo.
W3: Escape + deopt lab — allocation-free loop; trap-storm repro.
W4: Service warmup audit — block-hound of cold path + tuning note.
```
## Success Metrics
- [ ] Every benchmark has warmup + forks + reported error bars
- [ ] Explain one deopt from JFR/log in plain words
- [ ] One allocation removed via escape (profiler proof)
- [ ] Cold-start vs warm p99 documented for one endpoint

## What This Is Not
Reading assembly all day. It is knowing when the JIT is the suspect.

> Mantra: **Never benchmark cold; never guess hot.**
