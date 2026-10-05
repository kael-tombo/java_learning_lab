# QUIZ — Lab 10: Security Response (15 questions)

1. First on leaked key? — A) Ignore B) Revoke/rotate + kill sessions C) Reboot D) Delete logs — **B**
2. Password reset alone? — A) Enough B) No—tokens/sessions survive C) Fixes image D) Patches TLS — **B**
3. Isolate via? — A) More replicas B) NetworkPolicy/quarantine, scale malicious to 0 C) Open SG D) Disable logs — **B**
4. JWT must check? — A) None B) alg allowlist + exp + aud/iss C) Only sub D) Length — **B**
5. `alg:none` is? — A) Fine B) Critical bypass C) Faster D) Encrypted — **B**
6. Cert expiry check? — A) Ping B) `openssl s_client`/`curl -v` chain dates C) Traceroute D) nslookup only — **B**
7. Preserve evidence by? — A) rm logs B) Immutable snapshot + hashes before rebuild C) Reformat only D) Hide — **B**
8. Least privilege means? — A) Admin all B) Minimal roles, short-lived creds C) Static keys D) Wildcards — **B**
9. WAF block needs? — A) Forever B) Scoped rule + review expiry C) Allow all D) No test — **B**
10. Rebuild must? — A) Same node dirty B) Clean tag + scan green + new secrets C) Old image D) Skip verify — **B**
11. Impossible-travel signals? — A) Healthy B) Account takeover C) Deploy D) Cache — **B**
12. Egress spike suggests? — A) Normal B) Exfiltration/C2, investigate C) Faster app D) Billing — **B**
13. Notify requires? — A) Rumors B) Legal/DPO per window, factual template C) Silence D) Blame — **B**
14. Static keys in repo? — A) Good B) Leak path; use OIDC/manager C) Required D) Secure — **B**
15. Return to 100% via? — A) Flip all B) Canary + enhanced monitoring C) Delete monitors D) Rush — **B**
