# RUNBOOK: Chaos Engineering Operations & Emergency Abort
## Lab 18 | Production Engineering Academy

---

## RUNBOOK 01: Emergency Abort of All Active Chaos Experiments

**Severity**: P1 / Emergency  
**Condition**: Customer error budget burn rate exceeds 2x or steady state breaks during experiment.

### Step 1: Execute Global Chaos Mesh Emergency Halt
```bash
# Delete all active Chaos Mesh experiments immediately
kubectl delete networkchaos,podchaos,stresschaos,iochaos,jvmchaos --all -A
```

### Step 2: Emergency Reset via Toxiproxy CLI
```bash
# Remove all active network toxics across proxy fleet
toxiproxy-cli toxic list <endpoint>
toxiproxy-cli toxic remove -n <toxic_name> <endpoint>
```

### Step 3: Emergency Disable of Spring Boot Chaos Monkey
```bash
curl -X POST http://localhost:8081/actuator/chaosmonkey/disable
```

### Step 4: Verify Steady State Restoration
Check Prometheus: Verify p99 latency returns $< 200\text{ms}$ and error rate drops to baseline within 60 seconds.
