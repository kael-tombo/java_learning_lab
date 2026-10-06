# Lab 03: Production Debugging — Mini Project

## Project: `ForensicsKit` — Evidence Capture and Triage Harness

**Time**: 8–12 hours | **Difficulty**: Advanced | **Stack**: Java 21, JDK tooling (`jcmd`, JFR, NMT), shell

Build a reproducible debugging environment: four pathologies you can trigger on demand, an evidence-capture script that collects everything worth collecting, and a triage runbook that maps symptoms to commands. The point is that every claim in this lab gets *practiced*, not read.

---

## Part 1 — The four pathologies

Create one app with subcommands so each can be triggered independently:

```java
public final class Target {
    public static void main(String[] args) throws Exception {
        switch (args[0]) {
            case "hang"      -> hang();          // symptom: latency up, CPU flat
            case "deadlock"  -> deadlock();      // symptom: total wedge
            case "leak"      -> leak();          // symptom: RSS up over time
            case "thrash"    -> thrash(args);    // symptom: GC pauses
            case "pin"       -> pin();           // symptom: threads > tasks
            default -> throw new IllegalArgumentException("unknown mode: " + args[0]);
        }
    }

    /** Native-I/O wait: RUNNABLE threads, low CPU. */
    static void hang() throws Exception {
        var pool = Executors.newFixedThreadPool(64);
        for (int i = 0; i < 64; i++) {
            pool.submit(() -> { try (var s = new Socket()) { s.connect(new InetSocketAddress("10.255.255.1", 8080), 60_000); } catch (Exception ignored) {} });
        }
        Thread.sleep(Long.MAX_VALUE);
    }

    /** Lock-order inversion — two-resource deadlock. */
    static void deadlock() {
        Object a = new Object(), b = new Object();
        new Thread(() -> { synchronized (a) { sleep(200); synchronized (b) { } } }, "txn-A").start();
        new Thread(() -> { synchronized (b) { sleep(200); synchronized (a) { } } }, "txn-B").start();
        Thread.sleep(Long.MAX_VALUE);
    }

    /** Unbounded cache: RSS grows, heap grows, no single class dominates. */
    static void leak() throws Exception {
        var map = new ConcurrentHashMap<Integer, byte[]>();
        for (int i = 0; i < 200_000; i++) {
            map.put(i, new byte[128 * 1024]);
            if (i % 1000 == 0) Thread.sleep(20);
        }
        Thread.sleep(Long.MAX_VALUE);
    }

    /** Allocation churn: high GC frequency, live set tiny. */
    static void thrash(String[] a) throws Exception {
        long deadline = System.nanoTime() + Long.parseLong(a[1]) * 1_000_000_000L;
        while (System.nanoTime() < deadline) new byte[4096];
    }

    /** Thread leak: executor created per request, never shut down. */
    static void pin() throws Exception {
        for (int i = 0; i < 5000; i++) {
            var pool = Executors.newFixedThreadPool(4);
            pool.submit(() -> { try { Thread.sleep(200); } catch (InterruptedException ignored) {} });
            Thread.sleep(5);
        }
        Thread.sleep(Long.MAX_VALUE);
    }
}
```

---

## Part 2 — The evidence capture script

One script that collects *everything* worth collecting, in the right order, without perturbing the system much:

```bash
#!/usr/bin/env bash
# usage: ./capture.sh <pid> <label>
set -euo pipefail
PID=$1; OUT="evidence/$2"; mkdir -p "$OUT"

# 1. liveness + JVM identity (cheap, no safepoint-heavy work)
jcmd "$PID" VM.command_line          > "$OUT/cmdline.txt" 2>&1 || true
jcmd "$PID" VM.flags                 > "$OUT/flags.txt"   2>&1 || true
jcmd "$PID" VM.native_memory baseline > "$OUT/nmt-baseline.txt" 2>&1 || true

# 2. heap: cheap first, expensive after
jcmd "$PID" GC.heap_info             > "$OUT/heap-info.txt" 2>&1 || true
jcmd "$PID" GC.class_histogram       > "$OUT/histo-1.txt"   2>&1 || true

# 3. threads: multiple samples over time (one dump is an anecdote)
for i in 1 2 3 4 5; do
  jcmd "$PID" Thread.print -l        > "$OUT/threads-$i.txt" 2>&1 || true
  sleep 2
done

# 4. classloader + native diff after the sample window
jcmd "$PID" VM.classloader_stats     > "$OUT/classloaders.txt" 2>&1 || true
jcmd "$PID" VM.native_memory summary.diff > "$OUT/nmt-diff.txt" 2>&1 || true
jcmd "$PID" GC.class_histogram       > "$OUT/histo-2.txt"   2>&1 || true

# 5. continuous profile (bounded duration, ~1-2% overhead)
jcmd "$PID" JFR.start name=diag settings=profile duration=60s filename="$OUT/rec.jfr" 2>&1 || true
sleep 62

# 6. GC log tail if unified logging to file is enabled
[[ -f /var/log/app/gc.log ]] && tail -5000 /var/log/app/gc.log > "$OUT/gc-tail.log" || true

# 7. process + cgroup context (works only for cgroup v2 host visibility)
cat /proc/$PID/status                 > "$OUT/proc-status.txt" 2>&1 || true
cat /proc/$PID/smaps_rollup           > "$OUT/smaps.txt"      2>&1 || true
```

Add a `--container` mode that also captures cgroup limits and throttling:

```bash
CG=$(awk -F: '/^0::/{print $3}' /proc/$PID/cgroup)
cat "/sys/fs/cgroup${CG}/cpu.stat"      >> "$OUT/cgroup.txt" 2>&1 || true
cat "/sys/fs/cgroup${CG}/memory.max"    >> "$OUT/cgroup.txt" 2>&1 || true
cat "/sys/fs/cgroup${CG}/memory.current">> "$OUT/cgroup.txt" 2>&1 || true
cat "/sys/fs/cgroup${CG}/pids.max"      >> "$OUT/cgroup.txt" 2>&1 || true
```

---

## Part 3 — The triage analyzer

Write a tool that turns thread dumps into a verdict (this is the piece that scales to real incidents):

```java
public record TriageVerdict(String dominantState, int dominantCount, int total,
                            List<String> notes, String suspect) {}

public final class ThreadDumpAnalyzer {
    private static final Pattern THREAD = Pattern.compile("^\"(?<name>[^\"]+)\".*");
    private static final Pattern STATE  = Pattern.compile("java\\.lang\\.Thread\\.State: (?<s>\\w+)");
    private static final Pattern LOCKED = Pattern.compile("- locked <0x(?<id>[0-9a-f]+)> \\(a (?<type>[\\w.$]+)\\)");
    private static final Pattern OWNER  = Pattern.compile("- <0x(?<id>[0-9a-f]+)> \\(a (?<type>[\\w.$]+)\\)");

    public static TriageVerdict analyze(List<String> dumpFiles) throws IOException {
        Map<String, Integer> states = new TreeMap<>();
        Map<String, Integer> nameCounts = new HashMap<>();
        Map<String, String> lockOwners = new HashMap<>();
        int total = 0;

        for (Path f : dumpFiles) {
            String current = null, currentState = null;
            for (String line : Files.readAllLines(f)) {
                Matcher t = THREAD.matcher(line);
                if (t.find()) { current = t.group("name"); continue; }
                Matcher s = STATE.matcher(line);
                if (s.find() && current != null) {
                    currentState = s.group("s");
                    states.merge(currentState, 1, Integer::sum);
                    nameCounts.merge(normalize(current), 1, Integer::sum);
                    total++;
                }
                Matcher l = LOCKED.matcher(line);
                if (l.find() && current != null) lockOwners.put(l.group("id"), current);
            }
        }

        String dominant = states.entrySet().stream()
                .max(Map.Entry.comparingByValue()).map(Map.Entry::getKey).orElse("?");
        List<String> notes = new ArrayList<>();
        String suspect = "unknown";

        double blockedShare = share(states, "BLOCKED");
        double waitingShare = share(states, "WAITING") + share(states, "TIMED_WAITING");
        double runnableShare = share(states, "RUNNABLE");

        if (blockedShare > 0.3) {
            suspect = "monitor contention (see 'Found one Java-level deadlock' or owner map)";
            notes.add("contended locks: " + lockOwners);
        } else if (waitingShare > 0.7) {
            String top = nameCounts.entrySet().stream()
                    .max(Map.Entry.comparingByValue()).map(Map.Entry::getKey).orElse("?");
            suspect = "pool/queue exhaustion in '" + top + "'";
            notes.add("dominant thread family: " + top + " x" + nameCounts.get(top));
        } else if (runnableShare > 0.8) {
            suspect = "CPU work or native I/O — disambiguate with a JFR ExecutionSample/SocketRead profile";
        }
        return new TriageVerdict(dominant, states.getOrDefault(dominant, 0), total, notes, suspect);
    }

    private static String normalize(String name) {
        return name.replaceAll("-?\\d+$", "").replaceAll("-\\d+$", "");
    }

    private static double share(Map<String, Integer> m, String k) {
        int t = m.values().stream().mapToInt(Integer::intValue).sum();
        return t == 0 ? 0 : m.getOrDefault(k, 0) / (double) t;
    }
}
```

**Expected output** on the planted pathologies:

```
$ java -cp out ForensicsAnalyzer evidence/deadlock/
dominant state : BLOCKED (2 of 2 sampled groups)
suspect        : monitor contention (Found one Java-level deadlock reported)
notes          : contended locks: {0x00000000f8a1c2d0=txn-A, 0x00000000f8a1c2e0=txn-B}

$ java -cp out ForensicsAnalyzer evidence/hang/
dominant state : RUNNABLE (64 of 64)
suspect        : CPU work or native I/O — disambiguate with a JFR ExecutionSample/SocketRead profile
```

Then open the JFR and prove the `hang` case is `SocketRead`, not CPU:

```bash
jfr summary evidence/hang/rec.jfr
jfr print --events jdk.SocketRead evidence/hang/rec.jfr | head -40
jfr print --events jdk.ExecutionSample evidence/hang/rec.jfr | head -40
```

---

## Part 4 — Symptom → command runbook

Produce `RUNBOOK_DEBUG.md` as a decision tree, with a "collect first, then decide" preamble:

| Symptom | First command | Then | Confirm with |
|---|---|---|---|
| Latency ↑, CPU flat | `jcmd <pid> Thread.print -l` ×3 | State histogram; check dominant family | JFR `SocketRead` vs `ThreadPark` |
| Latency ↑, CPU ~100% | JFR `settings=profile` 60s | `ExecutionSample` top frames | `jdk.NativeMethodSample` |
| All requests hang | `Thread.print -l`, look for deadlock report | Lock owner map | Fix lock ordering; add order-enforcement test |
| 5xx burst | Check error class + dependency metrics | Then threads | Retry/breaker counters |
| Pod restarts, exit 137 | Previous container logs | cgroup `memory.events` (`oom_kill`) | JVM logs for absence of OOME |
| Pod restarts, exit 143 | Normal termination | Liveness probe history | Deployment events |
| RSS grows over hours | `GC.class_histogram` twice, diff | `VM.native_memory summary.diff` | `smaps_rollup` |
| `OOME: Metaspace` | `VM.classloader_stats` | Classloader count | `heapdump` + classloader retention |
| `OOME: Direct buffer memory` | Check `-XX:MaxDirectMemorySize` | Find per-request direct allocs | `BufferPoolMXBean` metrics |
| Latency ↑ after deploy | JFR `jdk.ClassLoad` + GC log | Warmup vs regression | Before/after two-sample test |

---

## Acceptance Criteria

- [ ] All five pathologies trigger their documented symptom.
- [ ] `capture.sh` runs against all five and produces complete evidence directories.
- [ ] Analyzer correctly names the suspect for `deadlock`, `hang`, and `pin` (validated against your own output).
- [ ] JFR proves `hang` is native I/O, not CPU — you show the `SocketRead` events.
- [ ] `RUNBOOK_DEBUG.md` is executable by someone who has never seen the app.
- [ ] You can state, in one sentence, the difference between a symptom, a hypothesis, and evidence.

---

## Stretch

- Add OTel span correlation so the JFR/dump timestamps line up with request traces automatically.
- Build a small dashboard (Grafana JSON import) with panels derived from the triage outcomes.
- Automate `capture.sh` as a sidecar that snapshots on `oom_kill` detection, with retention limits.
