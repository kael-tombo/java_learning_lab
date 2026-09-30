# EXERCISES: Chaos Engineering & Failure Injection
## Lab 18 | Production Engineering Academy

---

## Exercise 1: Injecting Network Latency with Toxiproxy

### Objective
Prove that adding a Resilience4j circuit breaker prevents a slow downstream dependency from causing thread exhaustion when 2,000ms latency is injected.

### Tasks
1. Run Toxiproxy docker container and set up upstream client -> Toxiproxy -> mock downstream service.
2. Inject a 2,000ms latency toxic via Toxiproxy CLI:
   ```bash
   toxiproxy-cli toxic add -t latency -a latency=2000 downstream_mock
   ```
3. Send 100 concurrent requests against a client WITHOUT circuit breaker: observe that all 100 threads block, latency jumps to 2,000ms, and thread pools exhaust.
4. Enable Resilience4j Circuit Breaker with `slowCallDurationThreshold = 1000ms` and `failureRateThreshold = 50%`.
5. Re-run 100 concurrent requests: observe that after 10 requests, the breaker trips to OPEN, and subsequent 90 requests fail fast in $< 2\text{ms}$ with fallback response.

---

## Exercise 2: Chaos Mesh PodKill Experiment

### Tasks
1. Deploy a 3-replica Spring Boot deployment on Kind/Minikube.
2. Apply a Chaos Mesh `PodChaos` manifest configured with action `pod-kill` every 60 seconds.
3. Run continuous load test with `hey`:
   ```bash
   hey -z 180s -c 10 http://<service-ip>/health
   ```
4. Verify whether any 502 Bad Gateway errors occur during pod terminations.
5. If errors occur, tune `lifecycle.preStop` hook and verify 100% zero-error resilience under continuous pod kills.
