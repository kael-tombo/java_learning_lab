# Lab 10: LLM Safety & Alignment — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Jailbreak | User persuasion to bypass policy |
| 2 | Prompt injection | Instructions smuggled through untrusted content |
| 3 | Difference | Injection hits apps via their own data, not the user |
| 4 | Injection is worse | The app itself supplies the payload |
| 5 | Direct injection | Instruction typed by the attacker |
| 6 | Indirect injection | Instruction inside a retrieved doc or tool result |
| 7 | Defense in depth | Attacker must defeat every layer |
| 8 | L1 input | Sanitize, length cap, encoding normalization |
| 9 | NFKC | Unicode normalization to defeat lookalikes |
| 10 | Zero-width chars | Hide instructions from human reviewers |
| 11 | Bidi controls | Text-direction spoofing to confuse review |
| 12 | Decode-and-classify | Classify base64/hex/ROT13 decodings too |
| 13 | Quote not delete | Preserve evidence; deletion is a side channel |
| 14 | L2 system | Policy in the system message |
| 15 | Privilege separation | Permissions from code, not from text |
| 16 | Model cannot self-authorize | Narrating "permission granted" grants nothing |
| 17 | L3 tools | Allowlist, typed schemas, approval gates |
| 18 | Read-only agents | No write tools at all |
| 19 | Argument injection | Payload smuggled through a tool argument |
| 20 | Pattern validation | Blocks `A-1001'; DROP TABLE` before dispatch |
| 21 | Approval scope | Argument-scoped, not tool-scoped |
| 22 | Side-effect caps | Max writes per task |
| 23 | L4 output | Schema, refusal, grounding, citations, PII, policy |
| 24 | Fail closed | Classifier error blocks; never returns content |
| 25 | Input vs output guardrails | Input protects the system; output protects the user |
| 26 | Guardrail job mismatch | Input filters over-block legitimate security questions |
| 27 | L5 monitoring | Logging, anomaly detection, incident response |
| 28 | Refusal rate | Fraction of disallowed prompts declined |
| 29 | Over-refusal | Benign requests declined |
| 30 | They trade off | Always report as a pair |
| 31 | Killer-process example | Classic false positive in developer tooling |
| 32 | Category thresholds | Security research vs self-harm need different bars |
| 33 | Red teaming | Adversarial testing by people trying to break it |
| 34 | Threat model first | Know what you protect before testing |
| 35 | Attack surface | Prompts, docs, tool output, images, files |
| 36 | Red-team loop | Generate, execute, grade, fix, regress |
| 37 | Finding becomes a test | Prevents reintroduction by refactors |
| 38 | Encoding attacks | Base64, hex, ROT13, leetspeak, reversal |
| 39 | Framing attacks | Role play, hypothetical, novel, debug mode |
| 40 | Many-shot attack | Benign examples then one adversarial pair |
| 41 | Instruction collision | Appended instruction competing with the real one |
| 42 | Split payload | Instruction spread across turns or documents |
| 43 | Authority spoofing | Fake system tags, tool-output impersonation |
| 44 | Multi-turn injection | Per-turn filters see nothing dangerous |
| 45 | Stateful detection needed | Accumulate across turns |
| 46 | Image-borne injection | Text rendered inside an image |
| 47 | Image text is data | Never instructions |
| 48 | SFT | Behavioral cloning of preferred behavior |
| 49 | RLHF/DPO | Preference optimization for refusal and helpfulness |
| 50 | Constitutional AI | Critique against principles, then revise |
| 51 | Principles are assets | Versioned and gated like prompts |
| 52 | Adversarial training | Train on found attacks; genuinely helps |
| 53 | Representation engineering | Steer along a refusal direction |
| 54 | Alignment limits | Raises the floor; new attack families still break it |
| 55 | Constitutional critic | Separate critic model checks outputs |
| 56 | Canary string | Detect system-prompt leakage in outputs |
| 57 | Canary leak = hard fail | Any appearance fails the build |
| 58 | Audit log | Append-only with a hash chain |
| 59 | Hash chain | Tamper-evident record sequence |
| 60 | Safe mode | Strict policy, tools off, no retrieval, forced blocking |
| 61 | Time to detect | Primary operational safety metric |
| 62 | Time to contain | Primary operational safety metric |
| 63 | Drift alerts | Refusal spike, jailbreak success, cost spike |
| 64 | Do not rely on prompt | Prompts are not a security boundary |
| 65 | Regex as pre-filter | Cheap but not a control |
| 66 | Never leak stack traces | Internal details to users |
| 67 | Log PII carefully | Redact before logging prompts |
| 68 | No fail-open | Non-negotiable |
| 69 | Do not publish findings early | Fix first, then disclose |
| 70 | Grounding verification | Check output claims against retrieved evidence |

## Self-Check

55+ = solid, 45-54 = redo Exercises 6 and 11, below that reread THEORY 2-8.