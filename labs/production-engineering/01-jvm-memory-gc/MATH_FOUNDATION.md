# Lab 01: JVM Memory & GC — Math Foundation

The formulas you actually use when sizing heaps, reading GC logs, and reasoning about pause budgets.

---

## 1. Units that matter

| Symbol | Meaning | Example |
|---|---|---|
| `S` | live set (bytes retained after full GC) | 6 GB |
| `H` | max heap (`-Xmx`) | 16 GB |
| `R` | allocation rate (bytes/sec) | 800 MB/s |
| `Y` | young-gen size | 1 GB |
| `p` | target pause | 200 ms |
| `t_surv` | survival ratio (survivors / allocated) | 0.15 |
| `U` | CPU cores available | 8 |

All math below assumes steady state and roughly constant live set — verify with a full-GC histogram at peak.

---

## 2. Allocation rate from a GC log

Between two young collections you can read the young size before/after:

```
R = (heap_before_i+1 - heap_after_i) / (t_i+1 - t_i)
```

Example: 1000M before, 128M after, 40s apart:

```
R = (1000 - 128) MB / 40 s = 21.8 MB/s
```

Sanity: if `R` exceeds your disk+network write budget for the day, you have a write-amplification problem, not a GC problem.

---

## 3. Young-gen sizing from pause target

Copy cost per GC is proportional to survivors copied:

```
copied_bytes_per_gc = R * T_gc_interval
pause ≈ c * copied_bytes / U_eff      (c ≈ 1–3 ms per 100 MB copied on one GC thread, divides across GC workers)
```

Given desired pause `p`, solve for young gen size `Y` such that survivors fit:

```
Y ≥ (R * p_seconds) / t_surv          (simplified, uses desired interval == pause target)
```

Worked example: `R = 21.8 MB/s`, `p = 0.2 s`, `t_surv = 0.15`:

```
Y ≥ (21.8 * 0.2) / 0.15 ≈ 29 MB
```

That looks tiny — and it is: **pause is dominated by live-set scanning and evacuation of old regions, not by Eden size alone.** In practice G1's `MaxGCPauseMillis` heuristics handle this, and the real constraint is:

```
Y  must be ≥  enough that GC frequency stays acceptable
GC frequency = R / Y
```

If `R = 21.8 MB/s` and you want ≤ 1 young GC every 5s: `Y ≥ 109 MB`. So allocate young gen ≥ ~110 MB and let the collector tune the rest.

---

## 4. Heap sizing from live set

```
H ≈ k · S      with k in [2.5, 4] for latency-sensitive services
```

- `S = 6 GB` → `H = 15–24 GB`. Pick `H = 16 GB` and monitor `S`.
- Below `H = 2·S` you get frequent promotion failure and full GCs.
- Above `H ≈ 6·S` you are paying memory cost for GC headroom nobody uses — unless you need room for traffic spikes.

Heap-per-request sanity check:

```
heap_per_concurrent_request ≈ S / concurrency
S = 6 GB, 3,000 concurrent in-flight requests → 2 MB/request.
```

If your per-request retained state is 40 MB, 3,000 concurrency is physically impossible — you must shed load or shard.

---

## 5. Container memory arithmetic

```
container_limit = heap_max + metaspace_max + code_cache + thread_stacks + direct + native_overhead(~10%)
```

Thread stacks: `-Xss512k × 200 threads ≈ 100 MB`. Solve backwards:

```
heap_max = container_limit × 0.70   (a common conservative default)
```

With `container_limit = 4 GB`: `heap_max ≈ 2.8 GB` → set `MaxRAMPercentage=70`, not 100.

---

## 6. Amortized cost of GC

Total CPU cost of collection is proportional to live data scanned (mark) plus garbage copied:

```
cpu_fraction = (mark_bytes + copy_bytes) / (U × bytes_allocated) ≈ 5–15% typical
```

Practical implication: reducing **allocation rate** lowers GC CPU roughly linearly; increasing heap does not.

---

## 7. Humongous allocation math (G1)

Region size `g` (default heap/2048, 1–32 MB). Any object `> g/2` is humongous:

```
humongous_regions = ceil(object_size / g)
```

A 40 MB byte array with `g = 16 MB` → 3 regions allocated directly in old gen. Repeated humongous allocation is a classic Full-GC trigger. Chunk into `≤ g/4` buffers:

```
chunk_size ≤ g / 4      → 4 MB with g = 16 MB
```

---

## 8. Latency percentiles and tail budget

Service-level p99 latency with GC pauses `q` pauses per request (probability `f`):

```
P(latency > p99) ≈ 1 - (1 - f)^q
```

If pause probability per request is `f = 0.001` and a request spans `q = 3` GC-eligible pauses, tail contribution ≈ `0.3%`. This is why **pause frequency** matters as much as pause duration: reducing `MaxGCPauseMillis` from 200ms to 20ms without reducing frequency barely moves p99.

Little's Law link to latency budget:

```
L = λ · W        →  W ≤ L / λ
```

With 3,000 concurrent sessions and 5,000 req/s: `W = 3,000/5,000 = 0.6 s` average latency ceiling. A single 800 ms full GC blows the entire budget for everything in flight.

---

## 9. Metaspace growth and class unloading

Class count grows roughly with loaded jars/classes:

```
metaspace_used ≈ classes_loaded × avg_class_size   (≈ 2–5 KB for typical app classes)
```

20,000 classes × 3 KB ≈ 60 MB. A redeploy-style leak that loads 5,000 new classes per hour grows ~15 MB/h — invisible for a day, then `OutOfMemoryError: Metaspace`.

---

## 10. Jitter-free exponential backoff (used in GC-adjacent retry logic)

```
sleep = min(cap, base × 2^attempt) × U(0.5, 1.5)     half-jitter
```

Never `base × 2^attempt` without jitter: N clients that failed together retry together, converting a brownout into an outage.

---

## 11. Quick numeric drills

1. `R = 50 MB/s`, young gen 512 MB → GC every `512/50 ≈ 10.2 s`. At `R = 500 MB/s` → every ~1 s. Which one is your p99 killer?
2. Live set 8 GB, `Xmx = 20 GB` → ratio 2.5. Predict: acceptable young GCs, but watch promotion during spikes.
3. Live set 8 GB, `Xmx = 12 GB` → ratio 1.5. Predict: `To-space exhausted`, frequent full GCs.
4. `Xmx = 30 GB` in a 32 GB container. Estimate total RSS. Answer: >32 GB with threads + direct + metaspace → OOM-kill.
5. G1 region size `g = 8 MB`; your object is 5 MB. Humongous? (`5 > 8/2 = 4` → yes.) Chunk to ≤ 2 MB.

---

## 12. Formulas worth memorizing

| Formula | Use |
|---|---|
| `R = Δheap / Δt` | allocation rate from logs |
| `GC frequency = R / Y` | why young-gen size controls pause count |
| `H = 2.5–4 × S` | heap sizing from live set |
| `heap = limit × 0.7` | container-safe default |
| `humongous if size > g/2` | G1 old-gen allocation |
| `L = λ · W` | concurrency ↔ latency budget |
| `sleep = base·2^n · jitter` | retry storms |
