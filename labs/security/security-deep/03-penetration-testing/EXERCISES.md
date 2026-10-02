# Penetration Testing — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: Scope Validation — Preventing Out-of-Bounds Scanning

**File**: `src/main/java/com/security/deep/lab03/ScopeValidator.java`

**Scenario**: A scanning tool accepts target ranges from user input. No validation against authorized scope. User could scan `10.0.0.0/8` instead of authorized `10.10.10.0/24`.

**Task**:
1. Implement `ScopeValidator` with authorized CIDR ranges loaded from RoE config
2. Validate every target IP/CIDR before scan: must be subset of authorized range
3. Reject targets outside scope with clear error
4. Test: authorized scan works; `10.0.0.0/8` rejected; `10.10.10.0/24` accepted; `10.10.11.0/24` rejected

**Threat Model**: Tester error or malicious input causes scanning of unauthorized systems (production, third-party, critical infrastructure). Legal liability, service disruption.

**Verification**: All out-of-scope targets rejected before any packets sent.

---

## Exercise 2: Safe Check Implementation — Vulnerability Verification Without Exploitation

**File**: `src/main/java/com/security/deep/lab03/SafeCheck.java`

**Scenario**: Testing for CVE-2021-44228 (Log4Shell). Full exploit executes arbitrary code. Safe check must verify vulnerability without RCE.

**Task**:
1. Implement safe check: send `${jndi:ldap://safe-check.example.com/xxx}` payload
2. Monitor DNS/HTTP callback to confirm JNDI lookup triggered
3. Do NOT send payload that downloads/executes code
4. Fix: if vulnerable, report with "Safe check confirmed" — never auto-exploit
5. Test: vulnerable Log4j triggers callback; patched Log4j does not

**Threat Model**: RoE prohibits exploitation without explicit approval. Auto-exploitation could damage systems, trigger alerts, violate scope.

**Verification**: Safe check detects vulnerability; no code execution occurs.

---

## Exercise 3: NSEC Zone Enumeration Detection

**File**: `src/main/java/com/security/deep/lab03/NsecEnumeration.java`

**Scenario**: Target domain uses DNSSEC with NSEC (not NSEC3). Attacker can walk the zone to enumerate all subdomains.

**Task**:
1. Implement NSEC walker: query for non-existent name, parse NSEC record for next name, repeat
2. Collect all subdomains in zone
3. Detect NSEC vs NSEC3: NSEC returns plaintext next name; NSEC3 returns hashed name
4. Report: zone enumeration possible (NSEC) or mitigated (NSEC3)
5. Test: against test zone with NSEC — full enumeration; against NSEC3 zone — hashes only

**Threat Model**: External attacker enumerates internal subdomains (dev, staging, admin panels, forgotten services) to expand attack surface.

**Verification**: NSEC zone fully enumerated; NSEC3 zone returns only hashes (offline cracking required).

---

## Exercise 4: CVSS Environmental Scoring — Contextualizing Risk

**File**: `src/main/java/com/security/deep/lab03/CvssEnvironmental.java`

**Scenario**: Scanner reports CVE-2021-44228 (CVSS 10.0 Critical) on 50 assets. Team overwhelmed. Need environmental scoring to prioritize.

**Task**:
1. Implement CVSS v3.1 Environmental calculator
2. Input: Base score (10.0), plus Environmental metrics:
   - Modified Attack Vector (Network/Adjacent/Local/Physical)
   - Modified Attack Complexity
   - Modified Privileges Required
   - Modified User Interaction
   - Modified Scope
   - Modified CIA Impact
   - Confidentiality/Integrity/Availability Requirement (Low/Medium/High)
3. Asset context: 
   - Asset A: Internal only (Adjacent), Low confidentiality requirement → Score?
   - Asset B: Internet-facing, High confidentiality → Score?
   - Asset C: Air-gapped, Physical access only → Score?
4. Output: Prioritized list with environmental scores
5. Test: Asset B > Asset A > Asset C in priority

**Threat Model**: Base score ignores context. Internet-facing high-value asset with same vuln is higher risk than internal low-value asset.

**Verification**: Environmental scores correctly reflect asset context; prioritization actionable.

---

## Exercise 5: Pass-the-Hash Detection — Lateral Movement Simulation

**File**: `src/main/java/com/security/deep/lab03/PassTheHashDetection.java`

**Scenario**: Simulate Pass-the-Hash attack and detect it via Windows Event Log analysis.

**Task**:
1. Simulate PtH: use NTLM hash to authenticate via SMB (psexec.py style) — generate Event ID 4624 (Logon Type 3, Network)
2. Implement detector: parse Security.evtx for:
   - Logon Type 3 (Network) from unusual source IPs
   - Account used from unusual workstation
   - Multiple logons from same hash (same Logon ID)
   - NTLMv1 usage (deprecated, indicator of PtH tools)
3. Alert on anomalies
4. Fix: enable Credential Guard, restrict NTLM, monitor for PtH patterns
5. Test: PtH simulation triggers alert; legitimate admin access does not (or lower severity)

**Threat Model**: Attacker compromises one workstation, dumps LSASS, uses hashes to move laterally. Detection at logon is critical.

**Verification**: Simulated PtH detected; false positives minimized via baselining.

---

## Exercise 6: Persistence Mechanism Enumeration & Removal

**File**: `src/main/java/com/security/deep/lab03/PersistenceEnum.java`

**Scenario**: Compromised host has multiple persistence mechanisms. Need to enumerate and remove.

**Task**:
1. Implement scanner for common Windows persistence locations:
   - Registry Run/RunOnce keys (HKLM/HKCU)
   - Scheduled Tasks (`schtasks /query /fo xml`)
   - Services (`sc query`, `sc qc`)
   - Startup folder
   - WMI event subscriptions (`Get-WmiObject __EventFilter`)
   - SSH authorized_keys
   - DLL hijacking paths
   - COM hijacking
2. For each found: verify legitimacy (signed binary, known publisher, expected path)
3. Generate removal script (PowerShell) for suspicious entries
4. Test: plant 5 test persistence mechanisms; scanner finds all; removal script cleans them

**Threat Model**: Attacker maintains access across reboots. Defender must find and remove all persistence to evict attacker.

**Verification**: All test persistence mechanisms detected and removed.

---

## Exercise 7: Kerberos Delegation Misconfiguration Audit

**File**: `src/main/java/com/security/deep/lab03/KerberosDelegation.java`

**Scenario**: AD has accounts with Unconstrained Delegation or Constrained Delegation misconfigured. Enables credential theft.

**Task**:
1. Query AD for accounts with:
   - `userAccountControl` has `TRUSTED_FOR_DELEGATION` (Unconstrained)
   - `msDS-AllowedToDelegateTo` set (Constrained) — verify target SPNs are legitimate
   - Resource-Based Constrained Delegation (RBCD) — `msDS-AllowedToActOnBehalfOfOtherIdentity`
2. Identify high-value targets (Domain Controllers, service accounts, admins)
3. Report risk: Unconstrained on non-DC = critical; Constrained to sensitive SPN = high
4. Fix: Remove unnecessary delegation; use RBCD with strict controls; protect privileged accounts (Protected Users group)
5. Test: Create test accounts with delegation; scanner identifies them with correct risk rating

**Threat Model**: Attacker compromises service account with delegation → obtains tickets for any user → escalates to domain admin.

**Verification**: All delegation misconfigurations identified with correct severity.

---

## Exercise 8: BloodHound Attack Path Analysis

**File**: `src/main/java/com/security/deep/lab03/BloodHoundAnalysis.java`

**Scenario**: BloodHound data (JSON) shows AD attack paths. Need to find shortest path from compromised user to Domain Admin.

**Task**:
1. Parse BloodHound JSON (nodes: users, computers, groups; edges: MemberOf, AdminTo, AllowedToDelegate, DCSync, etc.)
2. Implement graph algorithm (BFS/Dijkstra) to find shortest path from "Compromised User" to "Domain Admins"
3. Path types: 
   - Direct: User → MemberOf → Domain Admins
   - Indirect: User → AdminTo → Server → AllowedToDelegate → Service Account → MemberOf → Domain Admins
   - ACL-based: User → WriteDACL → Group → MemberOf → Domain Admins
4. Output: Visualizable path (GraphViz DOT), choke points (edges whose removal breaks all paths)
5. Test: On sample BloodHound data, find path and choke points

**Threat Model**: Attacker uses AD misconfigurations to escalate. Defender must identify and break attack paths.

**Verification**: Shortest path found; choke points identified; remediation breaks path.

---

## Exercise 9: Report Generation — Executive vs Technical

**File**: `src/main/java/com/security/deep/lab03/ReportGenerator.java`

**Scenario**: Raw findings from scan/exploit need to become two reports: Executive (1 page) and Technical (detailed).

**Task**:
1. Input: List of findings (title, CVSS, asset, description, evidence, reproduction, remediation)
2. Generate Executive Summary:
   - Business risk rating (Critical/High/Medium/Low)
   - Top 3 risks in plain language
   - Estimated remediation effort
   - Compliance impact
3. Generate Technical Report:
   - Per finding: reproduction steps (copy-paste runnable), evidence, specific remediation (commands, config changes), references
   - Appendix: tool output, raw data, methodology
4. Template system: Markdown → PDF/HTML
5. Test: Feed 10 sample findings; both reports generated correctly

**Threat Model**: Poor reports → findings ignored. Executive needs business context; engineers need exact steps.

**Verification**: Executive report < 1 page, no jargon; Technical report reproducible by junior engineer.

---

## Exercise 10: Design a Penetration Testing Threat Model

**File**: `docs/threat-model-pentest.md` (create this)

**Scenario**: You're building a penetration testing program for a financial services company with 5000 employees, hybrid cloud, legacy mainframe, and strict regulators.

**Task**:
1. **Assets**: Customer PII, financial transactions, trading algorithms, API keys, signing certificates, mainframe datasets, cloud credentials
2. **Adversaries**: 
   - External: APT (nation-state), ransomware gangs, opportunistic
   - Internal: Malicious admin, compromised developer, negligent employee
   - Supply chain: Compromised vendor, malicious dependency
   - Physical: Tailgating, hardware implants
3. **Trust Boundaries**: Internet ↔ DMZ ↔ Internal ↔ Restricted (PCI) ↔ Mainframe; Cloud ↔ On-prem; Prod ↔ Non-prod
4. **Testing Scope & Rules**:
   - Annual external pen test (black box)
   - Quarterly internal pen test (gray box)
   - Continuous automated scanning (vuln management)
   - Red team exercise (annual, objective-based)
   - Exclusions: Mainframe (separate program), payment processing (PCI DSS separate)
5. **Per-Phase Threats & Mitigations**:
   - Recon: Passive only external; active internal with RoE
   - Scanning: Authenticated scans preferred; rate limiting; safe checks only
   - Exploitation: Proof-of-concept only; no data exfiltration; no persistence
   - Post-exploitation: Simulated only (no actual lateral movement); validate detection
   - Reporting: 48hr critical findings; 2 week full report; retest included
6. **Detection Validation**: Blue team must detect each phase (SIEM rules, EDR, network monitoring)
7. **Compliance Mapping**: PCI DSS 11.3, SOX, GDPR, NYDFS

**Deliverable**: `THREAT_MODEL.md` with STRIDE per phase, data flows, RoE template, detection requirements, compliance mapping, retesting criteria.