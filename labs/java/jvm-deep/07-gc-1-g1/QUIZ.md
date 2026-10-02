# QUIZ — GC: G1

## 1. What is G1's primary design goal?
<details><summary>Answer</summary>Low, predictable pause times for large heaps (4GB+); regional collection instead of full-heap.
</details>

## 2. How does G1 divide the heap?
<details><summary>Answer</summary>Into equal-sized regions (1-32 MB each); young/old regions distributed across heap.
</details>

## 3. What are G1's region states?
<details><summary>Answer</summary>Free, Humongous, Eden, Survivor, Old.
</details>

## 4. What is a humongous object in G1?
<details><summary>Answer</summary>Object > 50% region size; allocated in contiguous humongous regions.
</details>

## 4. How does G1 achieve predictable pauses?
<details><summary>Answer</summary>Collects subset of regions per cycle (mixed GC); pauses bounded by target (default 200ms).
</details>

## 5. What is a mixed GC in G1?
<details><summary>Answer</summary>Collects young + selected old regions; reclaims old gen space incrementally.
</details>

## 5. What is a mixed GC?
<details><summary>Answer</summary>Collects young + selected old regions; reclaims old gen space incrementally.
</details>

## 6. What is the RSet (Remembered Set)?
<details><summary>Answer</summary>Per-region index of incoming references from other regions; enables young GC without full heap scan.
</details>

## 6. What is the RSet (Remembered Set)?
<details><summary>Answer</summary>Per-region index of incoming references from other regions; enables young GC without full heap scan.
</details>

## 7. What is a humongous object?
<details><summary>Answer</summary>Object > 50% region size; allocated in contiguous humongous regions.
</details>

## 7. What triggers a G1 mixed GC?
<details><summary>Answer</summary>Old gen occupancy > InitiatingHeapOccupancyPercent (default 45%).
</details>

## 8. What is SATB (Snapshot-At-The-Beginning)?
<details><summary>Answer</summary>Write barrier that records old references before overwrite; preserves liveness snapshot at GC start.
</details>

## 8. What is SATB (Snapshot-At-The-Beginning)?
<details><summary>Answer</summary>Write barrier that records old references before overwrite; preserves liveness snapshot at GC start.
</details>

## 9. What triggers a G1 young GC?
<details><summary>Answer</summary>Eden space full; young regions selected for collection.
</details>

## 9. What triggers a G1 young GC?
<details><summary>Answer</summary>Eden space full; young regions selected for collection.
</details>

## 10. What is the default pause target for G1?
<details><summary>Answer</summary>200ms (configurable via -XX:MaxGCPauseMillis).
</details>

## 10. What is the default pause target for G1?
<details><summary>Answer</summary>200ms (configurable via -XX:MaxGCPauseMillis).
</details>