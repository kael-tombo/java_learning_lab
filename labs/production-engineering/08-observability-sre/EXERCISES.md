# EXERCISES: Observability & SRE in Practice
## Lab 08 | Production Engineering Academy

---

## Exercise 1: Build OpenTelemetry Context Propagation Across Virtual Threads

### Objective
Implement end-to-end distributed trace propagation that maintains W3C headers across HTTP clients, asynchronous Virtual Threads, and SLF4J MDC logging.

### Tasks
1. Set up an OpenTelemetry Java SDK harness with an in-memory span exporter.
2. Create an incoming HTTP request containing header:
   `traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`.
3. Extract the parent span and populate MDC.
4. Dispatch an asynchronous task to `Executors.newVirtualThreadPerTaskExecutor()`.
5. Verify that logs emitted inside the virtual thread contain the identical `trace_id` and child `span_id`.
6. Verify the exported spans form a parent-child span hierarchy.

---

## Exercise 2: Configure and Test a Prometheus Burn Rate Alert Rule

### Tasks
1. Define a Prometheus alerting rule in YAML calculating a 14.4x burn rate over 1-hour and 5-minute windows for an SLO target of 99.9%.
2. Simulate a failure injection by generating 100% 500 error responses for 3 minutes.
3. Validate that the alert enters `PENDING` state and transitions to `FIRING` when the burn rate threshold is breached.
