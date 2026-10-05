# Flashcards

## Q: What problem does Backend Performance solve?
**A:** Profile, benchmark, and tune Java services for latency and throughput.

## Q: Entry-point annotation/class?
**A:** The main Spring component/controller for Backend Performance.

## Q: Default bean scope?
**A:** Singleton.

## Q: How to externalise config?
**A:** `application.yml` + `@ConfigurationProperties`.

## Q: How to test the slice?
**A:** `@WebMvcTest` / equivalent slice test.

## Q: How to handle dependency failure?
**A:** Timeouts, retry with backoff, circuit breaker.

## Q: Core math intuition?
**A:** queueing theory and percentiles over averages.

## Q: When N+1 appears here?
**A:** When fetching a parent triggers per-child queries.

## Q: What signal indicates trouble?
**A:** Rising p99, error rate, or saturation.

## Q: Best next read?
**A:** THEORY.md and CODE_DEEP_DIVE.md in this lab.
