# REAL_WORLD_PROJECT — Trigonometry in Production: Audio Latency & Rotary Encoder Service
> Production use-case: sampling vibration sensors for predictive maintenance.

## 1. Scenario
- Service: edge gateway samples motor vibration at 2 kHz and FFT-buckets it.
- Constraint: detect bearing fault at 120 Hz; avoid aliasing; low CPU on the box.
- Choice: anti-alias low-pass at 1 kHz, FFT window 1024, Hann window applied.
- Data: `Sample{t, amplitude}`; pipeline in fixed-size ring buffers.

## 2. Architecture
```aw ADC → anti-alias filter → ring buffer → windowed DFT → band energy → alert
```
- Sample rate vs Nyquist documented per sensor model.
- Feature flag to change windowing (Hann/Hamming).

## 3. War-Story (plausible, representative)
- Incident: after a firmware update, bearings "failed" on every motor.
- Symptom: spurious 100 Hz component swamped the alert threshold.
- Root cause: ADC decimation changed 4 kHz→1.6 kHz but analysis still assumed 2 kHz; a real 140 Hz signal aliased to 100 Hz.
- Fix: sample rate in the config contract; startup asserts Fs vs analysis constants.
- Lesson: sampling rate is a correctness input, not a perf knob.

## 4. Metrics (before → after)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| false bearing alerts/day | 8 | 0 | −100% |
| CPU per gateway | 22% | 18% | −4pp |
| p99 ingest-to-alert | 310ms | 300ms | ~same |
| config drift incidents | 2/qtr | 0 | −100% |

## 5. Prevention Checklist
- [ ] Fs asserted against analysis constants at startup.
- [ ] Anti-alias filter before decimation.
- [ ] Window type logged with every FFT result.
- [ ] Property test: pure tone at f peaks at bin(f).
- [ ] Aliasing demo kept as a regression test.
- [ ] Detect clipped ADC values and mark data suspect.
- [ ] Expose raw + FFT overlays in debug UI.
- [ ] Dashboard: alert rate, Fs, buffer overruns.

## 6. What "Good" Looks Like
- Alerts match mechanic findings; zero "ghost tone" tickets.

## 7. Stretch
- Move to proper STFT for time-varying faults.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Nyquist–Shannon sampling theorem: https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem
- Fast Fourier transform: https://en.wikipedia.org/wiki/Fast_Fourier_transform
