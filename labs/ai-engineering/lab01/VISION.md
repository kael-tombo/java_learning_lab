# Lab 01: LLM Serving Infrastructure — Vision

## Static vs Continuous Batching

```
STATIC BATCHING
  time -->  [ r1 r2 r3 r4 | r5 r6 r7 r8 | r9 ......... ]
             fill to B=8   step        step          step
  waste 1: r4 is short, waits for the batch to drain
  waste 2: batch never fills because arrivals are not synchronized
  waste 3: a slot is idle from when r4 finished until the batch step ends
  throughput: poor (small batches) or latency: bad (long batches)

CONTINUOUS BATCHING
  time -->  [ r1 r2 r3 r4 r5 r6 r7 r8 ]
              [ r1 r2 r3 r6 r7 r8 r10 ]     r4 done -> slot 4 reused immediately
                [ r1 r2 r7 r8 r10 r11 ]    r6 done -> slot 6 reused
  batch size: always near max while requests remain
  the batch never has to drain

  why it wins: in DECODE, adding a sequence to a running batch costs almost
  nothing (weights are read anyway) but multiplies throughput.
```

## Prefill vs Decode

```
PREFILL                              DECODE
  prompt: 500 tokens                   generating token 143
       |                                   |
  [===========================================]
  all 500 tokens in parallel          one token at a time
  FLOPs  ~ 2*P*500                     FLOPs ~ 2*P*batch
  mem    read weights ONCE             mem    read weights EVERY step
  COMPUTE BOUND                        MEMORY BOUND
  latency ~ linear in prompt len       latency flat per step
  batchable perfectly                  not batchable (sequential per request)

  TTFT = prefill_time + first_step
  TPOT = step_time

  a LONG PROMPT and a LONG OUTPUT are two different problems:
    long prompt  -> TTFT problem   -> chunked prefill, separate lane
    long output  -> throughput problem -> batch, quantize, cache policy
```

## Timing: Batch Size Decides Everything

```
7B, fp16, GQA(8) x 128, 300 TFLOP/s, 3 TB/s, 131 KB cache/token

  batch   compute      memory      bound       tok/s      $/1M tokens
  --------------------------------------------------------------
     1    0.047 ms    4.7 ms      memory        213          9.40
     8    0.37 ms     4.7 ms      memory       1702          1.18
    32    1.5 ms      4.7 ms      memory       6809          0.29
    64    3.0 ms      4.7 ms      memory      13617          0.15
   128    6.0 ms      4.7 ms      compute      21333          0.09
   256   11.9 ms      4.8 ms      compute      53333          0.04

  crossover at b = bytes * FLOPS/BW = 2 * 100 = 200

  batch 1 -> 128 is  64x more throughput
  batch 1 -> 256 is 250x more throughput
  => THE ARCHITECTURE DECISION, NOT THE MODEL, IS THE COST DECISION
```

## Memory Composition

```
7B, 4096 context, fp16 weights, GQA 8 x 128

  weights                 14.0 GB   ================================================
  KV cache per sequence    0.27 GB  ===

  batch  1    14.3 GB
  batch 16    18.3 GB
  batch 64    31.2 GB
  batch 128   48.5 GB
  batch 256   83.1 GB   <-- exceeds 80 GB

  cache > weights at batch > 6  (14e9 / (2*32*8*128*4096*2) = 5.2)

  levers, multiplicative:
    GQA 8 kv heads instead of 32   4x smaller cache
    INT8 KV cache                   2x smaller cache
    sliding window W=2048           2x smaller at 4096 context
    quantized weights (int4)        4x smaller weights

  => at long context, CACHE is the constraint. at short context, WEIGHTS are.
```

## Admission Control

```
  project KV for the WHOLE lifetime, not the current length:

    kv_needed = 2*L*H_kv*d_head*(prompt + max_new)*batch*bytes

  reserve while sum(reserved) <= pool * 0.9

  under-reserving by using current length:
     prompt=2000, max_new=2000  ->  under-reserve by 2x
     prompt=500,  max_new=4000  ->  under-reserve by 9x
  -> OOM exactly when many requests generate long answers

  on rejection: 429 + Retry-After, do NOT queue.
     queueing past the memory limit converts a clean 429 into a crash
     that also kills in-flight requests.
```

## Chunked Prefill

```
one 32k prompt arrives, naive:
  step 1: [prefill 32768 tokens]................. 12 s
          every concurrent interactive request waits 12 s
          p99 TTFT: catastrophic

chunked (CHUNK = 512):
  step 1: [decode batch][prefill chunk  0..512  ]
  step 2: [decode batch][prefill chunk 512..1024 ]
  ...
  step 64:[decode batch][prefill chunk 32256..32768]
  every step is bounded -> interactive p99 TTFT unaffected
  total prefill time is the same; only the granularity changes

  detail that is easy to get wrong: the chunk cursor must reset when the
  job is popped, or the next long prompt starts mid-way.
```

## Load Balancing

```
replicas: R1 fast (A100), R2 fast, R3 slow (partially failed / memory pressure)
requests: 80% short (50 tok), 20% long (2000 tok)

ROUND ROBIN:
  long requests land on R1, R2, R3 in turn -> one replica holds 3 long
  generations while others idle
  R1 p95 latency: 8x baseline

LEAST CONNECTIONS:
  long requests accumulate in-flight counts -> new requests avoid that replica
  R1/R2/R3 p95 within 15% of each other

LATENCY-AWARE:
  routes away from any replica whose p95 is elevated, even before it is full
  best tail latency, needs a latency estimator that is not fooled by cold starts

  => LLM request durations vary by ORDERS OF MAGNITUDE.
     round robin is the wrong default.
```

## Autoscaling Signal Choice

```
GPU UTILIZATION (lagging):
  traffic spike -> utilization climbs slowly -> by the time you act,
  the queue is already deep and TTFT has doubled
  cold start 90 s means you are always late

QUEUE DEPTH (leading):
  traffic spike -> queued requests climb immediately -> scale now
  you scale on the CAUSE, not the symptom

  scale-up:   queued + inflight/4 > 8 * replicas   -> 1.5x
  scale-down: queued + inflight/4 < 2 * replicas   -> -1
  guard:      respect the 90 s startup delay, no flapping

  target utilization 0.6, not 0.9:
    rho 0.6 -> mean wait 2.5/mu
    rho 0.9 -> mean wait 10/mu     (4x worse tail latency for 1.5x fewer replicas)
```

## Failure Modes Map

```
symptom                        | likely cause                        | fix
-------------------------------+-------------------------------------+---------------------------
OOM under load                 | admission too permissive            | projected-KV admission
throughput plateau             | static batching / batch too small   | continuous batching
p99 TTFT spike, no saturation | one long prompt blocking decode     | chunked prefill + lane
tail latency varies by replica | round-robin with mixed lengths       | least-connections
low prefix cache hit rate      | per-request prefix variation        | stable prefix layout
capacity drops over hours      | client disconnect not detected      | heartbeat + free slots
load spikes on timeout         | naive retries                       | bounded + jitter + breaker
GPU idle during peak           | autoscale lag from wrong signal     | scale on queue depth
```

## Streaming: Perceived Latency Only

```
200 output tokens, t_step = 20 ms

BUFFERED:
  client sees nothing for prefill(500ms) + 199 steps (3.98 s) = 4.5 s
  then everything at once

STREAMED:
  client sees token 1 at 500 ms, then one every 20 ms
  perceived latency: 500 ms, a 9x improvement

  total latency: IDENTICAL. throughput: IDENTICAL. cost: IDENTICAL.
  what changes: the metric you must set the SLO on -> TTFT, not total latency.

  operational implication: streaming clients disconnect more often
  (they leave sooner), so cancel-on-disconnect must free the slot promptly
```

## Self-Check

- [ ] Continuous batching with slot recycling, not batch draining.
- [ ] Admission control on projected lifetime KV, with 429 rather than queueing.
- [ ] Chunked prefill bounded per step.
- [ ] Batch size chosen from the compute/memory crossover, not from guesswork.
- [ ] Cache memory treated as the long-context constraint.
- [ ] Least-connections balancing, not round-robin.
- [ ] Autoscaling on queue depth with a startup-delay guard.
- [ ] TTFT as the SLO metric when streaming.