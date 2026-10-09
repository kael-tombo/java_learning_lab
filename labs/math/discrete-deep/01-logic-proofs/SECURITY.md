# Security: Logic and Proofs

## Formal Verification of Security Protocols

Logic is used to verify that cryptographic protocols are secure. The **BAN logic** (Burrows-Abadi-Needham, 1989) and its successors reason about authentication: "If A believes K is a fresh key and A sees {X}_K, then A believes B once said X." Tools like **Isabelle/HOL** and **Coq** use higher-order logic to machine-check protocol proofs.

## Access Control Logic

Access control policies are expressed in logical languages:
- **XACML** (eXtensible Access Control Markup Language) uses first-order logic to define policies like "A user can read a file if they are in the same department and the file is not classified."
- **Role-based access control (RBAC)** can be modeled in logic: user → role → permission, with constraints expressed as logical formulas.

## Model Checking for Security

Model checkers verify security properties of systems:
- **Secrecy**: An attacker cannot learn a secret. Modeled as "the secret is never reachable in the system's state space."
- **Authentication**: A protocol ensures that if A completes a run with B, then B also ran with A. Verified by checking all possible interleavings of protocol steps.

Tools like **SPIN** and **NuSMV** have been used to find flaws in real protocols (e.g., the Needham-Schroeder protocol flaw found by Lowe in 1995 using model checking).

## Type Systems as Logic

Programming language type systems are closely related to logic (Curry-Howard correspondence):
- A type is a proposition.
- A program is a proof.
- Type checking is proof checking.

This means a well-typed program cannot have certain runtime errors—a security guarantee. For example, Rust's ownership types prevent use-after-free and data races at compile time.

## SAT-Based Attack Analysis

Attackers use SAT solvers to find vulnerabilities:
- **Password cracking**: Encode the hash function as a SAT problem and solve for a preimage.
- **Protocol attacks**: Encode the protocol and attacker model, then ask the SAT solver for a trace that violates a security property.
- **Malware analysis**: Encode the conditions under which malware activates as a SAT instance.

## Limitations

Logic-based verification has limits:
- **Undecidability**: First-order logic is undecidable, so automated tools may not terminate.
- **State explosion**: Model checking finite systems can still be infeasible due to exponential state spaces.
- **Assumption dependence**: Verification is only as good as the assumptions (e.g., perfect cryptography, trusted hardware).
