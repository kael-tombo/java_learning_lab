# RUNBOOKS: Production Security, Threat Response & Cryptographic Triage
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Triaging a Compromised JWT Secret or Active Forgery Attack

### 1. Severity & Trigger Condition
- **Severity**: P0 / SEV-0 (Security Breach)
- **Trigger**: SIEM alerts indicate forged administrative JWTs or unexpected token signatures bypassing authentication.

### 2. Immediate Containment Workflow

#### Step 1: Emergency Key Pair Invalidation
Rotate the asymmetric RSA/ECDSA signing key pair in the Authorization Server:
```bash
# Invalidate compromised key ID (kid) in Vault / KMS
vault write transit/keys/jwt-signer/rotate
```
Publish updated JWKS (JSON Web Key Set) with the new `kid`.

#### Step 2: Purge Active Sessions in Redis
To revoke all currently active access and refresh tokens across the cluster:
```bash
# Flush the Redis token revocation cache or execute atomic session purge:
redis-cli -h redis-auth.production.svc EVAL "
  local keys = redis.call('keys', 'session:*')
  for i=1,#keys,5000 do
    redis.call('del', unpack(keys, i, math.min(i+4999, #keys)))
  end
  return #keys
" 0
```
*Outcome*: All active sessions are immediately invalidated. Every user is forced to re-authenticate with multi-factor authentication (MFA).

#### Step 3: Verify Algorithm Pinning Across Fleet
Ensure no service is accepting tokens with `alg: "none"` or `alg: "HS256"`. Run an automated curl probe with an algorithm-confused token:
```bash
curl -i -H "Authorization: Bearer <FORGED_HS256_TOKEN>" https://api.corp.internal/v1/accounts
```
*Expected Response*: `HTTP 401 Unauthorized` (`Invalid Token Signature`).

---

## Runbook 02: Emergency Rotation of KMS Master Keys (KEK) and Vault Database Secrets

### 1. Context
A leak or unauthorized access event requires an immediate, zero-downtime rotation of the master encryption key and database credentials.

### 2. Execution Runbook

#### Step 1: Rotate Master Key (KEK) in AWS KMS
```bash
# Trigger an immediate manual rotation of the Master Key
aws kms create-key --description "Emergency Rotated Master KEK 2026"
aws kms enable-key-rotation --key-id <NEW_KEY_ID>
```
*Note*: Because Envelope Encryption is used, persisted database records encrypted with ephemeral DEKs continue to decrypt successfully using the key version embedded in the header.

#### Step 2: Rotate Dynamic PostgreSQL Database Credentials via Vault
```bash
# Instruct Vault to revoke all currently leased database credentials immediately
vault lease revoke -prefix database/creds/payment-service-role
```
Vault automatically closes the leased PostgreSQL database users.
Spring Cloud Vault detects the revocation and requests fresh credentials, seamlessly updating HikariCP without application restarts.

---

## Runbook 03: Investigating an Insecure Deserialization / RCE Attempt via eBPF Logs

### 1. Alert Context
Tetragon / Cilium eBPF alert: `ProcessSpawnedFromJavaContainer`:
```text
syscall=execve process="/bin/sh" parent_process="java" container="checkout-service"
```

### 2. Immediate Diagnostic & Isolation Workflow

#### Step 1: Isolate the Compromised Pod via NetworkPolicy
Isolate the pod immediately from the network to prevent lateral movement:
```bash
kubectl label pod <COMPROMISED_POD> quarantine=true -n production
```
Apply quarantine NetworkPolicy blocking all egress traffic:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine-pod
  namespace: production
spec:
  podSelector:
    matchLabels:
      quarantine: "true"
  policyTypes:
    - Egress
  egress: [] # Deny all outbound traffic!
```

#### Step 2: Capture Memory & Core Dump for Forensics
```bash
# Capture Linux memory dump before terminating
gdb -p $(pgrep -f "java.*checkout") --batch --eval-command="gcore /tmp/compromised-core.dump"
kubectl cp production/<COMPROMISED_POD>:/tmp/compromised-core.dump ./compromised-core.dump
```

#### Step 3: Terminate the Compromised Container
```bash
kubectl delete pod <COMPROMISED_POD> -n production --force --grace-period=0
```

---

## Runbook 04: Remediating an Active SQL Injection Vulnerability in Production

### 1. Symptoms & Alert
- WAF / Datadog Security alert: `SQLiPatternDetected` on endpoint `GET /api/v1/accounts/search`.
- Database logs show suspicious syntax errors (`syntax error at or near "DROP"`).

### 2. Rapid Mitigation via WAF Rule (Sub-5 Minutes)
Before a code patch can be built and deployed, block the malicious payload pattern at the Cloudflare / AWS WAF edge:
```bash
# Update AWS WAF WebACL to block SQL injection on the specific path
aws wafv2 update-web-acl --name Production-WAF --scope REGIONAL ... \
  --rules 'Name=BlockAccountSearchSQLi,Priority=1,Statement={ByteMatchStatement={SearchString="--",FieldToMatch={QueryString={}}}},Action={Block={}}'
```

### 3. Deploy Code Hotfix
1. Locate the vulnerable query in repository:
   - Replace string concatenation with parameterized CriteriaBuilder query (Pattern 4 of CODE DEEP DIVE).
2. Enforce strict Java `enum` validation on sorting fields.
3. Deploy via emergency canary pipeline.

---

## Runbook 05: Emergency Revocation and Re-Issuance of SPIFFE mTLS Certificates

### 1. Context
An internal worker node was compromised, potentially exposing the resident SPIRE Agent's private key and cached X.509 SVID certificates.

### 2. Execution Runbook

#### Step 1: Ban the Compromised Node Attestation in SPIRE Server
```bash
# Query SPIRE Server for agent entry:
kubectl exec -it spire-server-0 -n spire -- spire-server agent list
# Evict the compromised agent:
kubectl exec -it spire-server-0 -n spire -- spire-server agent evict -spiffeID spiffe://cluster.local/spire/agent/k8s_psat/node-14
```

#### Step 2: Invalidate Certificates via Certificate Revocation List (CRL)
Update SPIRE CRL and force renewal across all valid agents:
```bash
kubectl exec -it spire-server-0 -n spire -- spire-server bundle show > /tmp/new_bundle.crt
```
Kubelet will reload fresh X.509 certificates across all healthy pods within 60 seconds, locking out the compromised node completely.
