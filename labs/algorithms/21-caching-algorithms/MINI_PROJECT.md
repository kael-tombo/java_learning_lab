# Mini-Project: LRU Cache from Scratch

## Goal

Implement an O(1) LRU cache with your own hash map plus doubly linked list
(no `LinkedHashMap`), then prove the eviction order on a fixed script.

## Inputs

- Capacity 3, fixed operation script below; no random data.
- Script: put(1,a), put(2,b), put(3,c), get(1), put(4,d), get(2), put(5,e).

## Steps

1. Create node class with key, value, prev, next pointers.
2. Create map from key to node plus head (most recent) and tail pointers.
3. Implement get: return value and move node to head, or -1 on miss.
4. Implement put: insert or update at head; drop tail when over capacity.
5. Run the script and log the key order after every operation.
6. Assert the final order and which keys were evicted.
7. Measure get/put cost constant by timing 1M mixed ops (smoke check only).

## Acceptance criteria

1. `get(2)` after `put(4,d)` returns -1 (key 2 evicted, not key 1 or 3).
2. Final key order from most to least recent is [5, 4, 1].
3. No use of `LinkedHashMap` or other ordered-map shortcuts in the cache.
4. Operation log shows the order after each of the 7 script steps.
5. Hit path and miss path both covered by printed assertions.
6. Timing smoke test completes and prints total milliseconds.
7. All output uses plain ASCII characters.

## Grading note

- One wrong eviction in the 7-step log fails the submission.
- Any ordered-map import in the cache fails the build check.
- Final order [5,4,1] plus the get(2) miss are both required.

## Stretch

- Add an LFU variant reusing the operation script; compare evicted keys.
- Add a frequency tie-break rule and document it in two sentences.
