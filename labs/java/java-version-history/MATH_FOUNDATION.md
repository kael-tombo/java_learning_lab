# MATH_FOUNDATION — Java Version History

The timeline is qualitative; the *adoption decision* is arithmetic. Every formula
below turns "should we upgrade" into a number you can defend in a planning
review.

## 1. Amdahl's law on a partially-migrated fleet

A 500-engineer estate never finishes a migration. Let `p` = fraction of the fleet
on the new JDK and `N` = the multiplier you expect from it (throughput, cost per
request, or developer velocity).

```math
gain(p) = 1 / ( (1 − p) + p/N )
```

For `N = 2.5` (a plausible throughput-and-density figure for 8 → 25 plus compact
headers and virtual threads on IO-bound services):

| `p` | `gain(p)` | Marginal gain from the next 10% |
|---|---|---|
| 0.10 | 1.049 | 0.041 |
| 0.25 | 1.135 | 0.024 |
| 0.50 | 1.286 | 0.013 |
| 0.75 | 1.475 | 0.006 |
| 0.90 | 1.716 | — |

`d(gain)/dp = N / (N − (N−1)p)²`. At `p` = 0.5 the last 10% of services bought
1.3% of gain; the **first** 25% bought 13.5%. **Sequence low-blast-radius
services first** — that is an arithmetic consequence, not a preference.

Amdahl also warns you where the ceiling is: even at `p` = 1 you get only `N`. So
if the honest `N` is 1.4, the entire multi-year programme returns 40% and a
targeted change to the two worst services probably returns more. Compute `N` from
*measured* p99 and RPS per unit before committing the roadmap.

## 2. Compact object headers: memory-savings arithmetic

**The actual mechanism (verified against JEP 450 / JEP 519).** Today HotSpot's
64-bit object header is a mark word plus a class word, occupying **between 96
bits (12 B) and 128 bits (16 B)** depending on configuration. Compact object
headers subsume the compressed class pointer into the mark word, reducing the
header to a flat **64 bits (8 B)** on x64 and AArch64.

```math
saving = header_before − header_after      # 8 B typical (16 B → 8 B), or 4 B (12 B → 8 B)
```

**The 16-byte figure circulating in blog posts is wrong.** If you see a capacity
model assuming 16 B saved per object, it has double-counted — that would mean a
zero-byte header. Real savings are **4–8 bytes per object**, depending on whether
compressed class pointers are enabled. Use 8 B as the optimistic case.

The per-class cost is a separate, much smaller term: the class-level header is
stored once per class, and the compressed class pointer shrinks from 32 to 22
bits. Because the per-class cost is negligible at any realistic class count, the
per-object term dominates completely:

```math
saving      ≈ 8 × N_live                     # N_live = live objects
heap_saved% = saving / heap_total × 100
```

Worked example — 40 million live objects in a 2 GB heap, compressed class
pointers enabled (12 B header → 8 B, so 4 B/object):

```math
saving      = 4 × 40,000,000 = 160,000,000 bytes ≈ 153 MiB
heap_saved% = 153 / 2048 = 7.5%
```

With a 16 B header → 8 B the same workload saves ~305 MiB (~15%). **So the
honest answer is single-digit to low-double-digit percent of heap, not ~30%.**

This is consistent with what the JEPs actually report: Project Lilliput's
real-world early adopters saw **live data reduced by 10–20%**, and JEP 519 cites
**SPECjbb2015 using 22% less heap** and 8% less CPU. That is the range to quote
in a capacity review — vendor-measured, not a byte-count extrapolation.

Note also that JEP 450 observed **more than 20% of live data can be object
headers alone**, which is *why* a header reduction is worth doing even at 8 B —
the header is a large fraction of a small object.

**Relative saving per object depends on object size**, which is why the same
change is a big win for small objects and noise for large ones:

```math
relative% = 4 / (object_size + 4) × 100      # conservative 4 B case
```

| Object | Header before | Header after | Field+padding | Relative saving |
|---|---|---|---|---|
| Two `int` fields | 16 B | 8 B | 8 B → total 24→16 B | **33%** |
| `Long` (16 B value) | 16 B | 8 B | 16 B → total 32→24 B | **25%** |
| Empty holder | 16 B | 8 B | 0 B → total 16→8 B | **50%** |
| 200 B value object | 16 B | 8 B | 200 B → total 216→208 B | 3.7% |
| 2 KB buffer object | 16 B | 8 B | 2 KB → total 2,064→2,056 B | **0.4%** |

**Adoption rule.** The return scales with *object count*, not bytes, so count
objects (via JOL or a heap histogram) rather than reasoning in megabytes. For an
object-count-heavy service (caches, DTO graphs, entity managers) it justifies a
dedicated workstream; for a buffer-dominated one it is a footnote.

### Practical constraints you must check first (from JEP 450)

Compact object headers are **not** free and have hard preconditions:

- **Requires compressed class pointers** — disabled automatically otherwise.
- **Requires the 8 TB heap ceiling** for collectors other than ZGC; above that
  the feature disables itself unless you use ZGC.
- **Disabled when JVMCI is enabled** (so Graal as a stock OpenJDK compiler is out).
- **Not compatible with legacy stack locking** — falls back automatically.
- **Still opt-in in 25.** JEP 519 promoted it to a *product* feature but
  explicitly kept it **off by default** ("It is not a goal to make compact
  object headers be the default object-header layout"). You still pass
  `-XX:+UseCompactObjectHeaders`; only `-XX:+UnlockExperimentalVMOptions`
  became unnecessary. JEP 534 tracks making it the default.

That last point is the one most secondary sources get wrong: "shipped in 25" does
not mean "on by default in 25".

Caveats that belong in the capacity model, not the marketing: heap-dump tooling
must be revalidated, and `-XX:ObjectAlignmentInBytes=16` or larger alignments
absorb some of the saving.

## 3. GC pause-time comparison arithmetic

Pause targets are budgets, so compare collectors as **budget consumption**, not
as "best pause".

```math
budget_used% = ( Σ pauses in window / wall_clock_window ) × 100
p99_pause    ≈ sorted_pauses[ ceil(0.99 × n ) ]
throughput   = live_data / ( pause_hours × write_rate )
```

For a 30 s window with a 2 GB live set and 200 GB allocated (EXERCISES 10):

| Collector | Pauses | Worst pause | Budget used | Verdict at 2 GB |
|---|---|---|---|---|
| G1 | ~600 | ~15 ms | ~1.9% | Fine — this is why G1 is the 9+ default |
| ZGC | ~40 cycles | <1 ms | ~0.05% | Overkill here |
| Shenandoah | ~30 | <1 ms | ~0.04% | Overkill here |

Now change the heap to 32 GB with the same *allocation rate* — and the ranking
changes, because G1's pause is driven by the fraction of live data in the
evacuation set:

```math
pause_G1 ≈ k × G1_EvacuationPct / G1_GCWorkerThreads × live_data
```

At 32 GB live with unchanged tuning, G1's young pauses stay bounded only if you
re-tune `-XX:G1HeapRegionSize` and the IHOP target. **This is the arithmetic
behind "re-baseline your pause SLOs when the collector changes"**: carry a
pause-time number across a collector migration without re-measuring and you are
guessing with a spreadsheet.

## 4. Virtual-thread memory economics

The 21 change is not "faster threads"; it is a **memory** change, and the
arithmetic is embarrassingly simple.

```math
platform_total = T_platform × stack_bytes                    # stack reserved, not just used
virtual_total  = C_carriers × stack_bytes + N_virt × ~256 B  # continuations stack in chunks
```

With the conventional `-Xss1m` platform default:

| Model | Threads | Stack bytes/thread | Reserved |
|---|---|---|---|
| Platform pool (today) | 200 | 1 MiB | **200 MiB** |
| Platform threads, unbounded | 20,000 | 1 MiB | **19.5 GiB** — hence the pool |
| Virtual threads | 20,000 | ~256 B of continuation | **~5 MiB + carriers** |

The 200 MiB is *reserved address space*, not resident — but it is what forces the
pool, and the pool is what forces queueing. So:

```math
p_old = pool_size = 200  → queueing when concurrency > 200
p_new = unlimited        → queueing at 0, at the cost of upstream limits instead
```

Which moves the bottleneck, and that is the whole point of Loom:

```math
new_bottleneck = min( db_pool, connection_pool, rate_limit, cpu_cores_for_compute_work )
```

So the ROI calculation is **not** "virtual threads are faster", it is: remove
your concurrency ceiling, then find what actually limits you. Two corollaries
worth writing into a design doc:

1. **`synchronized` pins the carrier.** A virtual thread that blocks while
   holding a monitor mounts for the whole wait, so a `synchronized` block around
   IO gives back the entire win. This is why migration is a `synchronized` audit.
2. **CPU work does not scale.** With 4 cores and 10,000 virtual threads doing
   CPU-bound work, throughput is 4. Use a `Semaphore` for CPU-bound sections —
   the guidance inverted from "size the pool" to "one thread per task, semaphore
   for CPU".

## 5. Cost of technical debt discounting — when to take the LTS

An upgrade postpones a future upgrade, so the true cost is the *discounted*
lifecycle cost of running an old JDK longer, not one migration's price.

```math
NPV(r, N, T) = Σ_{t=0}^{T−1}  C_t / (1 + r)^t

deferral_cost(t_now, T) = NPV(r, N, T + Δ) − NPV(r, N, T)
                          ≈ NPV(r, N, T) × Δ / T              # first-order, small Δ
total_now = M_migration + R_run_nonzero + H_hazard
defer     = deferral_cost(Δ = N − n_now)
```

Take the upgrade when `total_now < defer + H_hazard`, where `H_hazard` is the
expected cost of staying: support-EOL breach, an incident, or a lost feature you
need.

Worked example. Two LTS hops 21 → 25 → 29, `r = 10%`, horizon `T = 3` years, one
migration `M` = 200 person-days (≈ $160k all-in), recurring upgrade tax `R` =
$60k/yr.

```math
NPV(10%, 3, 3yr) = 0 + 60/1.1 + 60/1.21 = 0 + 54.5 + 49.6 = $104k
deferral(Δ = 1 hop, one year longer) ≈ 104 × (1/3) = $35k   # discounting shrinks it
total_now (25 now)  = 200×0.8 + 60 + H = $220k + H
total_now (29 later) = 200 + 35 + H = $235k + H
```

Deferring costs **$15k of pure carry**, but *rises* as `Δ` grows and collapses as
the horizon shortens:

```math
deferral(Δ) = NPV × (1 − (1+r)^(−Δ)) / T
Δ = 1 → $35k     Δ = 2 → $63k     Δ = 3 → $84k
```

**The rule that falls out:** deferral cost is proportional to how much life you
still expect from the current JDK. If your fleet has < 24 months of expected
life, `Δ = 1` and the arithmetic favours waiting. If you have hardware or a
container base image with a 3-year life, deferral is ~$84k and the migration pays
for itself on carry alone — before `H_hazard` is counted at all. `H_hazard` is
usually the dominant term for a *regulated* estate, which is why compliance
deadlines, not preference, set the schedule.

## 6. Preview-to-standard adoption math

Adopting a preview feature early is a bet. Price it.

```math
P(breaks at next release) = p_api_churn × p_you_would_rewrite
expected_port_hours       = P × (hours_per_port × surface_modules)
option_value              = P(standard) × benefit_hours_saved − expected_port_hours
adopt_early ⟺ option_value > 0
```

With `p_api_churn = 0.55` for a first-round preview, `0.30` for a second-round
one, `0.10` for a third — an empirically reasonable ladder, since preview
feedback lands in the next release:

| Feature | Preview releases | `p_churn` | Adoption decision |
|---|---|---|---|
| Records | 14, 15 | 0.30 | Adopt on 16 LTS |
| Sealed classes | 15, 16 | 0.30 | Adopt on 17 LTS |
| Pattern matching `switch` | 17, 19, 20 (3) | 0.10 | Adopt on 21 — churn risk mostly retired |
| Virtual threads | 19, 20 | 0.30 | Adopt on 21 |
| Structured concurrency | 19→ (incubator, then preview 20–25) | **0.90** | **Do not adopt** — still preview in 25 |
| String templates | 21–24 (4) | **1.00** | **Never** — withdrawn; churn realised |

Note the last two rows: a feature that stays in preview for *many* releases has
either a design problem or an ecosystem problem, and its `p_churn` should be
modelled near 1.0. **The feature that spent four releases in preview and was then
withdrawn is the calibration point** — anyone who "adopted early" paid a full
rewrite for nothing. Preview code is a bet with an unusually bad payoff
distribution, which is why the rule is *never ship preview to production* while
still using it freely in experiments.

## 7. Feature-adoption effort from version deltas

Rough sizing for a service adopting a version's features, for the plan in
`REAL_WORLD_PROJECT.md`:

```math
effort = Σ_f ( surface_f × days_per_surface ) × churn_factor(f)
churn  = 1.0 standard · 1.5 first-release-standard · 2.5 behavioural change
```

| Feature | Surface | Days | Churn | Effort |
|---|---|---|---|---|
| Records replacing DTOs | 40 classes | 0.5 | 1.5 | 30 d |
| Sealed + exhaustive switch | 12 hierarchies | 2 | 1.5 | 36 d |
| Pattern matching `switch` | 25 sites | 0.5 | 1.0 | 12 d |
| Virtual threads on IO services | 8 services | 5 | 2.5 | 100 d |
| Compact headers (capacity, not code) | — | — | — | 5 d |
| UTF-8 explicit charsets | 60 sites | 0.25 | 2.5 | 37 d |
| CLDR golden files per locale | 9 locales | 1 | 2.5 | 22 d |
| **Total** | | | | **~242 d** |

The two rows people forget — explicit charsets and CLDR golden files — are 24% of
the effort and are the *only* two that catch silent data corruption. They belong
in the plan even though they are not features you can demo.

## Summary

| Concept | Formula |
|---|---|
| Partial-fleet gain | `1 / ((1 − p) + p/N)`; marginal value falls as `p` rises |
| Compact header saving | `16 × N_live − 32 × C_live`; relative `% = 16/(size+16)` |
| GC budget consumed | `(Σ pauses / window) × 100`; G1 pause ∝ live data per evacuation |
| Virtual-thread memory | `T × stack_bytes` vs `N × ~256 B + carriers` |
| Upgrade deferral cost | `NPV × (1 − (1+r)^(−Δ)) / T` |
| Preview adoption bet | `P(standard) × benefit − p_churn × port_hours`; `p_churn` rises with preview count |
| Adoption effort | `Σ surface × days × churn` (behavioural changes get 2.5×) |