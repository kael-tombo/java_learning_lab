# VISION — Collections

## Vision Statement
**Pick the right collection the first time** — performance and correctness (ordering, uniqueness, null policy) follow from that single choice.

---
## Mental Models
### 1. Trinity: List / Set / Map
List = ordered+dupes; Set = unique; Map = key→value. Choose by semantics first.
### 2. Contract Twins
`equals/hashCode` drive `HashSet/HashMap`; `Comparable/Comparator` drive `Tree*`. Break them → lost entries.
### 3. Complexity Intuition
`ArrayList.get` O(1), insert O(n); `LinkedList` opposite; `HashMap` O(1) avg; `TreeMap` O(log n) sorted.
### 4. Fail-Fast vs Concurrency
Iterators fail-fast; mutating during loop → `ConcurrentModificationException`. Concurrent needs `ConcurrentHashMap`/`CopyOnWrite`.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Unique? | Set; sorted? TreeSet, else HashSet/LinkedHashSet |
| Key lookup? | HashMap (null-ok) vs ConcurrentHashMap (threads) |
| Iteration-heavy? | ArrayList; insert-front-heavy? ArrayDeque |
| Exposing? | Return unmodifiable copy/view |

---
## Career Trajectory
- **L1:** ArrayList/HashSet/HashMap CRUD + iteration.
- **L2:** ordering, comparators, unmodifiable views.
- **L3:** concurrent maps, sizing/load factor, allocation.
- **L4:** caching/eviction policy, collection-aware API design.

---
## 4-Week Path
```
W1: List/Set/Map basics, iteration, autoboxing.
W2: equals/hashCode, Comparable/Comparator.
W3: Deque/Queue, unmodifiable, concurrent basics.
W4: Student-registry + LRU-cache kata with benchmarks.
```
## Success Metrics
- [ ] Justify every collection choice with semantics+complexity
- [ ] Implement correct equals/hashCode/compareTo trio
- [ ] No concurrent-modification bugs under review
