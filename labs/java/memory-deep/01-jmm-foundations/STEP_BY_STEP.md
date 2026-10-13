# Step by Step: Build the Four Edges

## Goal

Four tiny programs, four exact outputs: `1499500`, `41541750`,
`2000000`, `true`. Each step adds one edge; each run confirms one
verdict. Total time: under an hour.

## Step 1: start edge (checksum 1499500)

1. Create `Data` with `int[1000] values` and a `long checksum`.
2. In main, fill `values[i] = i * 3 + 1`, accumulating `expect`.
3. Create a thread whose body sums the array into `seen[0]`.
4. Call `t.start()`, then `t.join()`, then compare `seen[0] == expect`.
5. Run: `expected checksum = 1499500`, `thread observed = 1499500`,
   `true`. If not, the fill loop moved below `start()` — move it back.

## Step 2: join edge (squares sum 41541750)

1. Allocate `int[500] result` in main.
2. Worker body: `result[i] = i * i` for all 500.
3. `worker.start()`, then `worker.join()` — no sleep, no poll.
4. Sum in main, compute `expect` independently, compare.
5. Run: `sum = 41541750 (expected 41541750)`, `true`. Reading before
   `join()` is the deliberate breakage (exercise 2) — observe, revert.

## Step 3: monitor edge (exactly 2000000)

1. Declare `static final Object LOCK` and `static long count`.
2. Spawn 8 threads, each looping 250000 times:
   `synchronized (LOCK) { count++; }`.
3. Start all, join all, compare with `8 * 250000`.
4. Run: `count = 2000000 (expected 2000000)`, `true`. Then try the
   two-lock breakage once (exercise 3) to feel the chain snap — and
   revert immediately.

## Step 4: latch edge (graph visible: true)

1. Define `Config { String url; int timeout; int[] ports }` (plain
   fields — the edge carries them).
2. Writer thread: assign all fields, then `ready.countDown()`.
3. Reader thread: `ready.await()`, then check all four values.
4. Join both, print the boolean. Run: `true`, every time, 10/10.
5. Write the chain on paper: three links, four field names — this card
   is the template for every publication review you do next.

## Step 5: causality probe (zero invented values)

1. Plain `box[0]` writer loops 1..100000; reader samples 100000 times
   into a synchronized set, flagging anything outside `[0, 100000]`.
2. Run: `out-of-thin-air values: 0`, `true`. Note the disorder (repeats,
   skips) in the distinct count — allowed chaos, forbidden invention.

## Step 6: lock in the habit

For each program, delete the edge (move the write, split the lock,
drop the latch) and watch the verdict go racy; restore and watch it
return. The muscle memory is the deliverable: break-one-line,
explain-in-hb, restore, green. Carry that loop into every later lab.
