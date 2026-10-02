# labs/java Academy Improvement Report

## Executive Summary
Completed pedagogical artifacts for the **5 labs with the most missing artifacts** (11 missing each). All 5 labs were "empty" directories containing only a `LEETCODE_SOLUTION.md` file. Added **QUIZ.md (10 questions)**, **FLASHCARDS.md (20 cards)**, and **EXERCISES.md (5 hands-on tasks)** for each, grounded in the lab's actual topic.

---

## Inventory Overview (All 52 Numbered Labs + Deep-Dive Subdirs)

### Numbered Labs (01-52)
| Lab | Missing | Key Missing Artifacts |
|-----|---------|----------------------|
| 01-java-syntax | 2 | MINI_PROJECT, REAL_WORLD_PROJECT |
| 02-data-types | 3 | MINI_PROJECT, REAL_WORLD_PROJECT, pom.xml |
| ... | 3 | (28 labs with 3 missing: MINI_PROJECT, REAL_WORLD_PROJECT, pom.xml) |
| 34-logging | 2 | MINI_PROJECT, REAL_WORLD_PROJECT |
| 35-serialization | 2 | MINI_PROJECT, REAL_WORLD_PROJECT |
| 36-reactive-programming | 2 | MINI_PROJECT, REAL_WORLD_PROJECT |
| 39-build-tools | 2 | MINI_PROJECT, REAL_WORLD_PROJECT |
| 41-52 (deep-dive style) | 2 | MINI_PROJECT, REAL_WORLD_PROJECT |

**Pattern**: All 52 numbered labs have README, THEORY, CODE_DEEP_DIVE, MATH_FOUNDATION, EXERCISES, QUIZ, FLASHCARDS, src. Missing: MINI_PROJECT, REAL_WORLD_PROJECT, and ~half missing pom.xml.

### Deep-Dive Subdirectories (15 parent dirs, 94 sub-labs)
| Lab | Missing | Status |
|-----|---------|--------|
| collections-deep/01-arraylist-vs-linkedlist | **11** | **Only LEETCODE_SOLUTION.md existed** |
| collections-deep/03-priority-queue | **11** | **Only LEETCODE_SOLUTION.md existed** |
| concurrency-deep/01-thread-creation | **11** | **Only LEETCODE_SOLUTION.md existed** |
| concurrency-deep/05-completable-future | **11** | **Only LEETCODE_SOLUTION.md existed** |
| jvm-deep/01-class-loading | **11** | **Only LEETCODE_SOLUTION.md existed** |
| java-io-nio-deep/* (5 labs) | 9 | Missing THEORY, CODE_DEEP_DIVE, MATH_FOUNDATION, EXERCISES, QUIZ, FLASHCARDS, MINI_PROJECT, REAL_WORLD_PROJECT, pom.xml |
| jvm-deep/01-class-loading (dup), 03-bytecode | 11 | Empty |
| modern-java-deep/01-lambda-expressions | 11 | Empty |
| performance-deep/01-profiling | 11 | Empty |
| testing-deep/01-unit-testing | 11 | Empty |
| ~70 other deep-dive labs | 3 | Missing MINI_PROJECT, REAL_WORLD_PROJECT, pom.xml |
| networking-deep/04-netty-framework, 05-grpc-networking | 2 | Have pom.xml + src |

---

## Work Completed: 5 Labs with 11 Missing Artifacts

### 1. collections-deep/01-arraylist-vs-linkedlist
**Topic**: ArrayList vs LinkedList performance characteristics + HashMap internals (based on LeetCode 706 Design HashMap solution)

**Files Added**:
- `QUIZ.md` — 10 questions covering: HashMap capacity/load factor, bucket index calculation, supplemental hash, treeification thresholds, ArrayList vs LinkedList complexity, cache locality
- `FLASHCARDS.md` — 20 cards: same topics in Q/A table format for spaced repetition
- `EXERCISES.md` — 5 tasks: bucket distribution analyzer, custom HashMap with linear probing, JMH benchmark, collision explorer with treeification observation, memory footprint comparison with JOL

### 2. collections-deep/03-priority-queue
**Topic**: PriorityQueue / min-heap operations + merge k sorted lists (LeetCode 23)

**Files Added**:
- `QUIZ.md` — 10 questions: offer/poll/peek complexity, min-heap vs max-heap, merge k lists complexity, thread-safety, default capacity
- `FLASHCARDS.md` — 20 cards: heap operations, array index formulas, merge k lists, alternatives (divide & conquer)
- `EXERCISES.md` — 5 tasks: min-heap from scratch, merge k sorted lists, top K frequent elements, custom Task comparator, in-place heap sort with JMH benchmark

### 3. concurrency-deep/01-thread-creation
**Topic**: Virtual threads (Java 21+) vs platform threads, structured concurrency (LeetCode 1242 Web Crawler)

**Files Added**:
- `QUIZ.md` — 10 questions: virtual vs platform thread differences, executor factories, I/O unmounting, pinning, ThreadLocal, scheduler, when to use each
- `FLASHCARDS.md` — 20 cards: memory footprint, executor factories, pinning vs unmounting, carrier threads, structured concurrency
- `EXERCISES.md` — 5 tasks: 10K task creation comparison, web crawler with HttpClient, pinning demo with synchronized vs ReentrantLock, ThreadLocal isolation, StructuredTaskScope with ShutdownOnFailure

### 4. concurrency-deep/05-completable-future
**Topic**: CompletableFuture async pipelines + work-stealing ForkJoinPool (custom WorkStealingThreadPool implementation)

**Files Added**:
- `QUIZ.md` — 10 questions: Future vs CompletableFuture, thenApply vs thenCompose vs thenCombine, allOf/anyOf, work-stealing deque mechanics, managed blocker
- `FLASHCARDS.md` — 20 cards: composition methods, work-stealing LIFO/FIFO, ForkJoinPool parallelism, compensating threads, RecursiveTask vs Action
- `EXERCISES.md` — 5 tasks: async dashboard pipeline with timeout, parallel array sum with RecursiveTask, extend WorkStealingThreadPool with Future/Callable, exception handling with retry logic, JMH benchmark comparing 4 approaches

### 5. jvm-deep/01-class-loading
**Topic**: Custom ClassLoader, delegation model, class identity, hot reload (Custom ClassLoader design)

**Files Added**:
- `QUIZ.md` — 10 questions: parent-first delegation, findClass vs loadClass, defineClass, class identity across loaders, bootstrap/platform/system loaders, ClassNotFoundException vs NoClassDefFoundError
- `FLASHCARDS.md` — 20 cards: delegation model, loader hierarchy, class identity, linkage errors, context ClassLoader, hot reload pattern
- `EXERCISES.md` — 5 tasks: directory-based ClassLoader with JAR support, classloader isolation demo (two versions of same class), child-first anti-pattern dangers, ServiceLoader with context ClassLoader, hot-reload simulation with WatchService

---

## Maven Validation

**Result**: None of the 5 labs had `pom.xml` files (all were missing per inventory). No Maven validation performed. No trivial breakages to fix.

---

## Files Added Summary

| Lab | QUIZ.md | FLASHCARDS.md | EXERCISES.md | Total |
|-----|---------|---------------|--------------|-------|
| collections-deep/01-arraylist-vs-linkedlist | ✓ | ✓ | ✓ | 3 |
| collections-deep/03-priority-queue | ✓ | ✓ | ✓ | 3 |
| concurrency-deep/01-thread-creation | ✓ | ✓ | ✓ | 3 |
| concurrency-deep/05-completable-future | ✓ | ✓ | ✓ | 3 |
| jvm-deep/01-class-loading | ✓ | ✓ | ✓ | 3 |
| **Total** | **5** | **5** | **5** | **15** |

---

## Pedagogical Design Notes

### QUIZ.md Format
- 10 multiple-choice/short-answer questions per lab
- Hidden answers in `<details>` tags for self-testing
- Questions progress from foundational → nuanced → application

### FLASHCARDS.md Format
- 20 cards per lab in markdown table
- Covers: definitions, constants, formulas, trade-offs, "why" questions
- Designed for spaced-repetition study (Anki-compatible)

### EXERCISES.md Format
- 5 hands-on tasks per lab, increasing difficulty
- Each includes: clear spec, starter code snippets, test cases, reflection questions
- Grounded in actual LeetCode problem / THEORY topic of the lab
- JMH benchmarks where performance comparison is relevant
- Real-world patterns: ServiceLoader, WatchService, StructuredTaskScope, HttpClient

---

## Recommendations for Further Improvement

1. **Add MINI_PROJECT and REAL_WORLD_PROJECT** to all 52 numbered labs (currently 0/52 have these)
2. **Add pom.xml** to deep-dive labs that have `src/` (70+ labs) for build reproducibility
3. **Populate the 4 completely empty deep-dive labs** (jvm-deep/01-class-loading, 03-bytecode; modern-java-deep/01-lambda-expressions; performance-deep/01-profiling; testing-deep/01-unit-testing) — same treatment as the 5 completed
4. **Complete java-io-nio-deep/** 5 labs (9 missing each) — they have README + src but no THEORY/EXERCISES/QUIZ/FLASHCARDS
5. **Standardize deep-dive structure**: All should have the 11-core artifact set like the numbered labs

---

*Report generated: 2026-10-01*