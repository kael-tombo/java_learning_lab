# MATH_FOUNDATION — Profiling Mathematics (Part 2)

## 4. Sampling Error Bounds

For a method consuming fraction `p` of CPU, with `N` samples:

```
Standard Error = √(p(1-p)/N)
95% CI = p ± 1.96 * √(p(1-p)/N)
```

**Practical rule**: To measure `p` with ±10% relative error at 95% CI:
- `p=50%` → need 100 samples
- `p=10%` → need 400 samples  
- `p=1%` → need 4000 samples
- `p=0.1%` → need 40,000 samples

At 100Hz sampling: 1% method needs 400s profiling.

---

## 3. Amdahl's Law for Optimization

```
Speedup = 1 / ((1-f) + f/s)
```

Where `f` = fraction of time in optimized code, `s` = speedup factor.

| Hotspot % | 2x faster | 10x faster |
|-----------|-----------|------------|
| 10%       | 1.05x     | 1.11x      |
| 30%       | 1.23x     | 1.43x      |
| 50%       | 1.33x     | 1.82x      |
| 80%       | 1.67x     | 5.00x      |
| 90%       | 1.82x     | 9.1x       |

**Lesson**: Profile first — small hotspots give diminishing returns.

---

## 4. Queueing Theory for Thread Pools

### M/M/c Queue Model

Thread pool = M/M/c queue:
- Arrival: Poisson (λ)
- Service: Exponential (μ)
- Servers: c threads

**Key metrics**:
- Utilization: `ρ = λ / (cμ)`
- Queue probability: Erlang C formula
- Mean wait time: `Wq = P(queue) / (cμ - λ)`

**Profiling insight**: If `ρ > 0.7`, queue builds rapidly. Profile shows threads in `WAITING` not `RUNNABLE`.