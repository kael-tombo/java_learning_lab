# Penetration Testing — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: What is the difference between passive and active reconnaissance, and what legal risk does each carry?

**Answer**: 
- **Passive**: OSINT, DNS queries, WHOIS, Shodan, certificate transparency logs, Google dorking — no direct interaction with target. Low legal risk (public data).
- **Active**: Port scanning, banner grabbing, vulnerability scanning, directory enumeration — direct packets to target. High legal risk: unauthorized scanning violates CFAA (US), Computer Misuse Act (UK), similar laws globally.

**Threat-Model Reasoning**: Penetration testing threat model assumes *authorized* engagement. Unauthorized active recon is a crime. Passive recon is generally legal but may violate ToS. Always obtain written Rules of Engagement (RoE) defining scope, allowed techniques, IP ranges, and time windows. Document authorization before any active step.

---

### Q2: Why is TCP SYN scan (-sS) stealthier than TCP Connect scan (-sT), and what OS privilege does it require?

**Answer**: SYN scan sends SYN, receives SYN-ACK, sends RST (never completes handshake). Connect scan completes full 3-way handshake (connect() syscall). SYN scan requires raw socket access (root/Administrator). Connect scan works as unprivileged user.

**Threat-Model Reasoning**: SYN scan avoids logging on target application (since connection never established), but modern IDS/IPS still detect half-open connections. Connect scan is fully logged. Threat model: if you lack root, use connect scan; if stealth is critical and you have root, SYN scan. Both are "active" — authorization required.

---

### Q3: What is the purpose of NSEC/NSEC3 in DNSSEC, and what privacy concern does NSEC have?

**Answer**: NSEC/NSEC3 provide **authenticated denial of existence** — proof that a domain name does not exist. NSEC returns the next existing name in canonical order, enabling zone enumeration (walking the zone). NSEC3 hashes names (with salt) to prevent enumeration.

**Threat-Model Reasoning**: Zone enumeration via NSEC allows attackers to map all subdomains, revealing internal infrastructure, staging environments, forgotten services. NSEC3 mitigates but offline dictionary attacks on hashes are possible if salt is known. Threat model: external attacker enumerating attack surface. Use NSEC3 with per-zone salt, opt-out for delegation-only zones.

---

### Q4: Explain the CVSS v3.1 scoring components. What does a score of 9.8 (Critical) typically represent?

**Answer**: CVSS v3.1 has three metric groups:
- **Base** (intrinsic): Attack Vector (Network/Adjacent/Local/Physical), Attack Complexity (Low/High), Privileges Required (None/Low/High), User Interaction (None/Required), Scope (Unchanged/Changed), Confidentiality/Integrity/Availability Impact (None/Low/High)
- **Temporal** (exploit maturity, remediation level, report confidence)
- **Environmental** (asset-specific)

**9.8 Critical**: Typically Network vector, Low complexity, No privileges, No user interaction, Unchanged scope, High CIA impact — e.g., unauthenticated RCE in network service.

**Threat-Model Reasoning**: CVSS helps prioritize remediation. But base score alone ignores context: a 9.8 on an isolated test server ≠ 9.8 on production database. Threat model must consider: asset value, compensating controls (WAF, network segmentation), exploit availability, threat actor capability. Use Environmental metrics to tailor score.

---

### Q5: What is the difference between a vulnerability scan and a penetration test?

**Answer**: 
- **Vulnerability Scan**: Automated, broad coverage, known CVE matching, high false positives, no exploitation, compliance-driven.
- **Penetration Test**: Manual + automated, targeted, exploits vulnerabilities to prove impact, chains findings, validates business risk, requires skilled tester.

**Threat-Model Reasoning**: Scans find *potential* issues; pen tests prove *exploitable* issues. Threat model: compliance needs scans; risk reduction needs pen tests. A scan saying "CVE-2021-44228 possible" vs a pen test showing "RCE achieved, domain admin accessed" drives different decisions. Both needed: scan continuously, pen test periodically.

---

### Q6: Describe the four phases of post-exploitation. What is the goal of each?

**Answer**: 
1. **Gain Access**: Exploit vulnerability → initial foothold (user-level shell)
2. **Escalate Privileges**: Local privilege escalation (kernel exploit, misconfig, token theft) → SYSTEM/root
3. **Maintain Access**: Persistence (scheduled tasks, services, WMI, SSH keys, Golden Ticket) → survive reboot/remediation
4. **Move Laterally**: Pivot to other systems (Pass-the-Hash, RDP, SSH, WinRM, SMB) → expand control

**Threat-Model Reasoning**: Defender's threat model assumes breach. Each phase is a detection opportunity: initial access (EDR, network anomaly), privilege escalation (unusual process tree, token manipulation), persistence (new service, scheduled task, registry), lateral movement (SMB/WinRM anomalies, unusual auth). Pen test validates detection coverage at each phase.

---

### Q7: What is "Pass-the-Hash" and why does it work in Windows environments?

**Answer**: Attacker steals NTLM hash (from LSASS memory, SAM, NTDS.dit) and uses it directly for authentication (SMB, WinRM, RDP) without cracking. Works because Windows challenge-response uses hash as secret; server never sees plaintext password.

**Threat-Model Reasoning**: Threat model: attacker has admin on one machine, dumps LSASS (Mimikatz, built-in tools). Hashes enable lateral movement without cracking. Mitigations: Credential Guard (virtualization-based LSASS protection), Restricted Admin mode (RDP), Protected Users group, NTLM blocking, LAPS (local admin password rotation), tiered administration.

---

### Q8: How does a "Golden Ticket" attack work in Kerberos, and what does it require?

**Answer**: Attacker obtains domain KRBTGT account hash (from DC compromise). Forges TGT (Ticket Granting Ticket) with arbitrary user, groups, lifetime. Presents forged TGT to KDC → gets service tickets for any service as any user.

**Threat-Model Reasoning**: Threat model: attacker compromises Domain Controller (DC) → dumps KRBTGT hash. Golden Ticket = persistent, undetectable (if encryption type matches), works across trusts. Mitigation: KRBTGT password rotation (double reset), protect DCs (tier 0), monitor for anomalous TGTs (lifetime, PAC), AES encryption only (disable RC4).

---

### Q9: What should a professional penetration test report include, and who are the audiences?

**Answer**: Audiences: **Executive** (business risk, summary, ROI), **Technical** (findings, reproduction, remediation), **Management** (tracking, compliance). Report sections: Executive Summary, Scope/Methodology, Findings (CVSS, evidence, impact, reproduction steps, remediation, references), Appendix (tool output, raw data).

**Threat-Model Reasoning**: Report is the *deliverable* — if not actionable, test wasted. Threat model: executives need risk context (not tech jargon); engineers need exact reproduction; auditors need evidence. Findings must link technical impact to business impact. Remediation must be specific (not "patch it" but "apply KB5001234, verify registry key X").

---

### Q10: What are the Rules of Engagement (RoE) and why are they critical?

**Answer**: RoE is a signed document defining: Scope (IPs, apps, systems), Allowed Techniques (scan types, exploitation, DoS?), Time Windows, Communication Channels (emergency contacts), Data Handling (PII, screenshots), Legal Authorization (signatures), Exclusions (critical systems, third-party).

**Threat-Model Reasoning**: Without RoE, pen test = crime. RoE protects both tester and client. Threat model: tester accidentally DoSes production (excluded in RoE → not liable). Tester accesses PII (RoE defines handling). Tester finds critical vuln (RoE defines emergency contact). Never test without signed RoE.