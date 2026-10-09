# Step-by-Step — Time Ordering

## Step 1: Lamport Clock
1. Class with private int counter
2. tick(): return ++counter (synchronized)
3. send(): return ++counter
4. receive(ts): counter = max(counter, ts) + 1
5. Test with threads

## Step 2: Vector Clock
1. Class with int[] vector
2. Constructor(nProcesses, ownIndex)
3. tick(): vector[ownIndex]++
4. send(): copy, increment, return copy
5. receive(other[]): element-wise max, increment own

## Step 3: HLC
1. Store physical (long) and logical (int)
2. tick(): check physical advance, update accordingly
3. receive(): extract, compute max, handle ties

## Step 4: Causal Broadcast
1. Per-process vector clock
2. On send: increment, attach, broadcast
3. On receive: check delivery condition, buffer if needed

## Step 5: Test and Benchmark
1. JUnit tests for each clock type
2. Verify complex causal patterns
3. Benchmark performance characteristics
