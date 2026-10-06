# VISION — Lab 01: JVM Memory & GC Mastery

> From "the service got slow" to a measured, defended heap decision.

---

## The Arc

1. **Mechanics** — regions, generations, TLAB, metaspace, code cache, native memory.
2. **Collector fluency** — Serial / Parallel / G1 / ZGC / Shenandoah / Epsilon, and what each costs.
3. **Log literacy** — read `before->after(total) time` lines and `Cause` lines like an operator.
4. **Sizing discipline** — derive heap and young gen from live set and allocation rate, not vibes.
5. **Triage** — OOM by type, leak hunting with `jcmd`, NMT, histograms, dumps.
6. **Production judgment** — know when GC is *not* the bottleneck and redirect effort.

---

## Why this lab exists

The JVM's default behavior is right most of the time. That is precisely why GC knowledge decays: without deliberate practice you never build the diagnostic muscle to know when the default is wrong. The Black-Friday full-GC story is not hypothetical — it is the single most common production incident shape for JVM teams.

---

## Milestones (checkable)

- [ ] M1: Draw heap generations, metaspace, code cache, thread stacks, and direct buffers from memory, with lifecycle arrows.
- [ ] M2: Given any GC log line, state allocation rate, live set, and pause duration in one sentence.
- [ ] M3: Choose a collector for three given workload profiles (batch, 8 GB latency service, 64 GB low-pause service) and defend CPU/memory cost.
- [ ] M4: Size a heap for a stated live set + concurrency + container limit, showing every step.
- [ ] M5: Diagnose four OOM variants (heap, metaspace, direct, native thread) from error text alone and produce a fix plan for each.
- [ ] M6: Use `jcmd` (heap_info, class_histogram, Thread.print) and NMT to prove a leak and name the dominant class.
- [ ] M7: Write a canary plan changing exactly one GC variable with a defined success metric and rollback.

---

## Anti-Goals

- Cargo-cult flags: `-Xmx16g -XX:+UseG1GC` copied from a blog without measuring live set.
- Treating every latency spike as a GC problem. Most spikes are downstream dependency latency, lock contention, or cold caches.
- Enabling `-XX:+PrintGCDetails` in prod and flooding the log pipeline. Use unified logging with sampling.
- Assuming `OutOfMemoryError` always means "heap too small."
- Raising `-Xmx` blindly — this frequently converts a GC problem into a container OOM-kill.

---

## Interview Lens

- "Live set is 8 GB and we get Full GCs every 20 minutes on a 24 GB heap. What's your first hypothesis?"
- "How do you know if a memory leak is a classloader leak versus an unbounded cache?"
- "Your p99 went from 40 ms to 900 ms; GC logs show nothing unusual. What do you check next, in order?"
- "Why did G1 stop being the default recommendation for 64 GB heaps?"

---

## 30-Day Plan

- **Week 1** — THEORY sections on regions/collectors; write GC logs by hand for a tiny program. Milestone M1–M2.
- **Week 2** — `EXERCISES` sizing drills and log-reading sets; QUIZ to 13/15; FLASHCARDS twice daily. M3–M4.
- **Week 3** — MINI_PROJECT end to end: build the allocation-rate dashboard + OOM repro harness. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a one-page "heap sizing decision record" for a real or imaginary service; teach-back in 5 minutes on a whiteboard. M7.

---

## Artifacts you should be able to show

1. A GC log with your annotations (allocation rate, live set, pause histogram).
2. A sizing spreadsheet: live set → heap → young gen → container limit, with margins.
3. A heap histogram that names the leaking class and its retained size.
4. A collector-selection decision record with CPU/memory overhead tradeoffs.

---

## Done = You Can

- Open a production GC log, state the problem in one sentence, and name the next three commands you would run.
- Defend a heap size with arithmetic, and state the trigger that would make you change it.
- Tell the difference between "needs a bigger heap," "needs less allocation," and "needs a different collector."
- Explain to a non-specialist why a 6-second full GC is an availability incident, not a performance ticket.
