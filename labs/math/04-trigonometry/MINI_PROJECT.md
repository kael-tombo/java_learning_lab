# MINI_PROJECT — Trigonometry: Signal Sampler & Wave Plotter
> Implement + sample + plot. ~3 hours.

## Goal
Build a CLI that synthesizes `A sin(ωt+φ)` signals, samples them at various rates,
detects aliasing, and ASCII-plots the waveform before/after sampling.

## Build Steps
1. `Wave.java`: `sample(t) = A*sin(2π f t + φ)` for multiple components.
2. `Sampler.java`: sample at rate Fs; report Nyquist check (Fs ≥ 2·fmax?).
3. `Plotter.java`: ASCII plot of continuous vs sampled points.
4. `AliasDemo.java`: sample a 5 Hz wave at 8 Hz — show apparent 3 Hz ghost.
5. Driver: grid of (f, Fs) runs; print PASS/FAIL for Nyquist and ghost frequency.

## Sample Output
```
f=2Hz Fs=20Hz  → samples track wave ✓
f=5Hz Fs=8Hz   → alias at |Fs-f|=3Hz ✗
f=1Hz+3Hz+9Hz, Fs=24Hz → fmax=9, need ≥18 ✓
```

## Benchmark Table (fill)
| f (Hz) | Fs (Hz) | alias detected? | ghost freq |
|--------|---------|-----------------|------------|
| 2 | 20 | | |
| 5 | 8 | | |
| 9 | 20 | | |

## Acceptance
- [ ] ASCII plot distinguishes sampled points from curve.
- [ ] Nyquist violation always flagged.
- [ ] Ghost frequency computed as |Fs − f|.

## Extensions
- Add FFT magnitude plot (naive DFT is fine at N=256).
- Compose chord tones (A4 = 2 harmonics).
