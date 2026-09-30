# RUNBOOK: Production Security Incidents & Compromise Triage
## Lab 09 | Production Engineering Academy

---

## RUNBOOK 01: Emergency Compromised Secret & Key Revocation

**Severity**: P0 (Active Credential Leak)  

### Step 1: Revoke the Leaked Credential Immediately
- **Database Password**:
  1. Rotate password in HashiCorp Vault / AWS Secrets Manager.
  2. Terminate all active sessions using old credential:
     ```sql
     SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE usename = 'compromised_user';
     ```
- **AWS IAM Key**:
  Deactivate access key immediately via AWS CLI:
  ```bash
  aws iam update-access-key --access-key-id <LEAKED_KEY_ID> --status Inactive
  ```

### Step 2: Audit CloudTrail & Access Logs for Exfiltration
Check actions executed by compromised principal over the last 48 hours:
```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<LEAKED_KEY_ID>
```
Isolate affected compute instances or S3 buckets.

---

## RUNBOOK 02: Triage of Active Java Deserialization / Log4Shell Exploit
1. Check process network connections:
   ```bash
   ss -tulpn | grep java
   # Look for unexpected outbound connections to LDAP (389), RMI (1099), or arbitrary remote ports
   ```
2. Capture volatile forensic memory dump:
   ```bash
   gcore -o /dumps/compromised-core $(pgrep -f java)
   ```
3. Quarantine the pod:
   ```bash
   kubectl label pod <pod-name> quarantine=true --overwrite
   # Update NetworkPolicy to deny all egress traffic
   ```
