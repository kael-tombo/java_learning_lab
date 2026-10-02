# Penetration Testing — Flashcards

---

## Reconnaissance

**Q: What is passive reconnaissance?**
**A:** Gathering info without directly interacting with target: OSINT, DNS records, WHOIS, Shodan, Censys, certificate transparency, Google dorking, social media, job postings.

---

**Q: What is active reconnaissance?**
**A:** Direct interaction with target: port scanning, banner grabbing, vulnerability scanning, directory enumeration, DNS zone transfer attempts.

---

**Q: What legal risk does active reconnaissance carry?**
**A:** Unauthorized scanning violates CFAA (US), Computer Misuse Act (UK), GDPR (EU). Always require written authorization (Rules of Engagement).

---

**Q: What is a TCP SYN scan (-sS)?**
**A:** Sends SYN, receives SYN-ACK, sends RST. Never completes handshake. Stealthier than connect scan. Requires root/Administrator.

---

**Q: What is a TCP Connect scan (-sT)?**
**A:** Completes full 3-way handshake via OS connect() syscall. Works unprivileged. Fully logged on target.

---

**Q: What is UDP scanning and why is it slow?**
**A:** Sends UDP packets, infers state from ICMP port unreachable (closed) or no response (open|filtered). No handshake, no retransmission guarantee → slow, unreliable.

---

**Q: What is banner grabbing?**
**A:** Connecting to service and reading initial response to identify software/version. Netcat, nmap -sV, telnet.

---

## Scanning & Enumeration

**Q: What is service enumeration?**
**A:** Identifying specific service versions, configurations, and vulnerabilities: nmap -sV, NSE scripts, manual interaction.

---

**Q: What is SMB enumeration?**
**A:** Enum shares, users, groups, policies via RPC (enum4linux, crackmapexec, smbclient). Null sessions (legacy), authenticated sessions.

---

**Q: What is SNMP enumeration?**
**A:** Querying SNMP OIDs for system info, interfaces, processes, software. Community strings (public/private) often default.

---

**Q: What is LDAP/Active Directory enumeration?**
**A:** Querying AD for users, groups, computers, GPOs, trusts, SPNs. Tools: ldapsearch, BloodHound, PowerView.

---

**Q: What is vulnerability scanning?**
**A:** Automated checking for known CVEs, misconfigurations, missing patches. Tools: Nessus, OpenVAS, Nuclei, Nikto (web). High false positives.

---

## Exploitation

**Q: What is the difference between a vulnerability and an exploit?**
**A:** Vulnerability = weakness (CVE). Exploit = code/technique that leverages vulnerability to achieve impact (RCE, privilege escalation, data access).

---

**Q: What is a "dry run" or "safe check" in exploitation?**
**A:** Verifying vulnerability exists without causing damage (e.g., sending benign payload that triggers detectable behavior). Required by RoE.

---

**Q: What is privilege escalation?**
**A:** Gaining higher privileges: vertical (user → root/SYSTEM), horizontal (user → another user). Kernel exploits, misconfigurations, token theft, sudo abuse.

---

**Q: What is Pass-the-Hash?**
**A:** Using NTLM hash directly for authentication (SMB, WinRM, RDP) without cracking. Works because hash is the secret in challenge-response.

---

**Q: What is Pass-the-Ticket?**
**A:** Using stolen Kerberos tickets (TGT, service tickets) for authentication. Extracted from LSASS memory.

---

**Q: What is a Golden Ticket?**
**A:** Forged Kerberos TGT using KRBTGT hash. Grants arbitrary user/groups/lifetime. Requires DC compromise.

---

**Q: What is a Silver Ticket?**
**A:** Forged Kerberos service ticket using service account hash. Targets specific service. Less powerful than Golden Ticket.

---

## Post-Exploitation

**Q: What are the four post-exploitation phases?**
**A:** 1) Gain Access 2) Escalate Privileges 3) Maintain Access (Persistence) 4) Move Laterally

---

**Q: What is persistence?**
**A:** Maintaining access across reboots/remediation: scheduled tasks, services, Run keys, WMI, SSH keys, Golden Tickets, web shells.

---

**Q: What is lateral movement?**
**A:** Moving from compromised system to others: Pass-the-Hash, Pass-the-Ticket, RDP, SSH, WinRM, SMB, DCOM, WMI, RPC.

---

**Q: What is pivoting?**
**A:** Routing traffic through compromised host to reach otherwise inaccessible networks: SSH tunneling, proxychains, meterpreter route add.

---

**Q: What is data exfiltration?**
**A:** Stealing data: compression, encryption, staging, covert channels (DNS, ICMP, HTTPS), cloud storage upload.

---

## Reporting & CVSS

**Q: What are the three CVSS metric groups?**
**A:** Base (intrinsic), Temporal (time-dependent), Environmental (context-dependent).

---

**Q: What does CVSS Base score 9.8 (Critical) typically mean?**
**A:** Network vector, Low complexity, No privileges, No user interaction, Unchanged scope, High Confidentiality/Integrity/Availability impact. E.g., unauthenticated RCE.

---

**Q: What is the difference between a vulnerability scan and a penetration test?**
**A:** Scan = automated, broad, known CVEs, high false positives, no exploitation. Pen test = manual+auto, targeted, exploits to prove impact, chains findings.

---

**Q: What should a pen test finding include?**
**A:** Title, CVSS score, affected asset, description, impact, evidence (screenshots, logs), reproduction steps, remediation (specific), references.

---

**Q: Who are the three audiences for a pen test report?**
**A:** Executive (business risk), Technical (reproduction/remediation), Management (tracking/compliance).

---

## Rules of Engagement

**Q: What is Rules of Engagement (RoE)?**
**A:** Signed document defining scope, allowed techniques, time windows, contacts, data handling, legal authorization, exclusions.

---

**Q: Why is RoE critical?**
**A:** Without it, pen testing = unauthorized access = crime. Protects tester and client. Defines emergency procedures.

---

**Q: What should be excluded from scope?**
**A:** Critical production systems, third-party hosted services (unless authorized), safety-critical systems, DoS-prone systems.

---

**Q: What is "safe harbor" in RoE?**
**A:** Legal protection for tester if they follow RoE. Client agrees not to prosecute for authorized activities.

---

## Threat Modeling Flashcards

**Q: What threat does unauthorized scanning enable?**
**A:** Legal liability, service disruption, IDS alerts triggering defensive response, loss of client trust.

---

**Q: What threat does missing RoE enable?**
**A:** No legal protection, scope creep, accidental damage to production, no emergency contacts.

---

**Q: What threat does NSEC (vs NSEC3) enable?**
**A:** Zone enumeration → full subdomain map → expanded attack surface.

---

**Q: What threat does Pass-the-Hash enable?**
**A:** Lateral movement without cracking passwords → rapid domain compromise from single admin machine.

---

**Q: What threat does Golden Ticket enable?**
**A:** Persistent, undetectable domain admin access → full domain compromise, survives password resets (until KRBTGT rotation).

---

**Q: What threat does missing persistence detection enable?**
**A:** Attacker survives reboot/remediation → long-term access.

---

**Q: What threat does missing lateral movement detection enable?**
**A:** Attacker expands from single foothold to domain-wide control.

---

**Q: What threat does poor reporting enable?**
**A:** Findings not remediated, executives don't understand risk, compliance fails, wasted investment.

---

**Q: What threat does CVSS-only prioritization enable?**
**A:** Patching low-risk 9.8 on isolated host before high-risk 7.5 on crown jewels.

---

**Q: What threat does missing evidence in findings enable?**
**A:** Developers can't reproduce, remediation unverified, disputes over validity.