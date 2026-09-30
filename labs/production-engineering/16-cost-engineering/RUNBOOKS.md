# RUNBOOK: FinOps & Cloud Cost Spike Triage
## Lab 16 | Production Engineering Academy

---

## RUNBOOK 01: Triaging a Cloud Cost Anomaly Spike

**Severity**: Business Warning / FinOps P2  
**Alert**: AWS Cost Anomaly Detection or Kubecost reports $> 25\%$ daily spend increase.

### Step 1: Identify the Spend Dimension (Kubecost / AWS CUR)
```bash
# Query Kubecost for top spenders by namespace
kubectl cost --service-port 9090 --service-name kubecost-cost-analyzer \
  namespace --window 2d
```
Check if the spike is:
- **Compute (EC2 / GCE)**: Caused by runaway autoscaling or unconstrained pod requests.
- **Network (Cross-AZ Egress)**: Caused by uncompressed streaming or disabled topology routing.
- **Storage / Snapshots**: Caused by unpruned EBS snapshots or continuous heap dumps.

### Step 2: Remediate Stranded Pod Capacity
Run Kubernetes pod right-sizing audit:
```bash
kubectl top pods --all-namespaces --sort-by=memory | head -n 30
```
Compare actual usage against `kubectl describe pod` requests. If requested memory is $5\times$ higher than actual, update Helm values to right-size requests.
