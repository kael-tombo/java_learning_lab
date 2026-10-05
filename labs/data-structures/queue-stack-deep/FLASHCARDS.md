# FLASHCARDS — Queue & Stack Deep

| # | Front | Back |
|---|---|---|
| 1 | Stack LIFO ops? | push/pop/peek |
| 2 | ArrayDeque stack role? | yes |
| 3 | ArrayDeque nulls? | no |
| 4 | Queue FIFO ops? | offer/poll/peek |
| 5 | ArrayDeque vs LinkedList queue? | ArrayDeque faster |
| 6 | PriorityQueue backing? | binary heap |
| 7 | PriorityQueue offer? | O(log n) sift-up |
| 8 | PriorityQueue poll? | O(log n) sift-down |
| 9 | PriorityQueue peek? | O(1) min |
| 10 | PriorityQueue iterator order? | not priority |
| 11 | Equal priorities stable? | no |
| 12 | BlockingQueue put? | blocks |
| 13 | BlockingQueue offer? | timeout/bool |
| 14 | ArrayDeque growth? | doubling |
| 15 | Stack extends? | Vector (legacy) |
| 16 | Vector methods? | synchronized |
| 17 | Two-stack queue amortized? | O(1) |
| 18 | peek vs poll? | peek doesn't remove |
| 19 | ArrayDeque ring buffer? | yes |
| 20 | Bounded deque blocking? | LinkedBlockingDeque |
| 21 | ArrayDeque iterator CME? | yes |
| 22 | PriorityQueue.remove(object)? | O(n) linear |
| 23 | Heap array index for left child? | 2i+1 |
| 24 | Heap array index for right? | 2i+2 |
| 25 | Parent of i? | (i−1)/2 |
| 26 | PriorityQueue capacity? | grows unbounded |
| 27 | PriorityBlockingQueue? | unbounded blocking |
| 28 | LinkedBlockingQueue bounded? | yes |
| 29 | ArrayBlockingQueue bounded? | yes |
| 30 | Deque peekFirst? | head |
| 31 | Deque peekLast? | tail |
| 32 | Stack legacy warnings? | use ArrayDeque |
| 33 | ArrayDeque offerFirst/Last? | O(1) amortized |
| 34 | ArrayDeque pollFirst/Last? | O(1) |
| 35 | PriorityQueue.contains? | O(n) |
| 36 | PriorityQueue.clear? | O(n) |
| 37 | Heap siftDown preserves? | heap order |
| 38 | Heap siftUp preserves? | heap order |
| 39 | ArrayDeque to use as stack? | push/pop/peek |
| 40 | Explicit null checks in ArrayDeque? | yes, throws on null |
| 41 | Eviction policy queues? | LinkedBlockingDeque |
| 42 | PriorityQueue comparator ties? | arbitrary |
| 43 | Binary heap complete tree property? | all levels filled except possibly last |
| 44 | Complete tree enables array storage? | yes |
| 45 | PriorityQueue max mode? | reverse comparator |
| 46 | ArrayDeque iterator fail-fast? | yes |
| 47 | poll returns null when empty? | yes |
| 48 | peek returns null when empty? | yes |
| 49 | remove throws on empty? | NoSuchElementException |
| 50 | element throws on empty? | NoSuchElementException |
| 51 | add vs offer on bounded queue? | add throws, offer returns false |
| 52 | put vs offer(timeout)? | put blocks indefinitely |
| 53 | drainTo bulk transfer? | yes |
| 54 | PriorityQueue.size? | size() |
| 55 | ArrayDeque clone? | shallow |
| 56 | ArrayDeque removeFirst occurrence? | first found |
| 57 | PriorityQueue shrink? | trimToSize |
| 58 | IndexQueue? | n/a, use ArrayBlockingQueue |
| 59 | Runtime JDK concurrent queue? | ConcurrentLinkedQueue |
| 60 | BlockingQueue interface adds? | blocking put/take |
