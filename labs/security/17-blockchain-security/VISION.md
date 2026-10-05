# VISION — Blockchain Security: Trusting the Wrong Layer
> Where this lab takes you: from "we use a smart contract" to knowing which assumptions a chain does and does not remove.

## The Arc
1. **What a chain gives you** — immutability, transparency, and distributed consensus, precisely stated.
2. **What it does not** — input correctness, key custody, bridge and oracle risk, and L1 assumptions.
3. **Smart contract vulnerabilities** — reentrancy, access control, arithmetic, and unchecked external calls.
4. **DeFi mechanics** — composability risk, flash loans, oracle manipulation, economic attacks.
5. **Operations** — audits, formal verification, upgradeability governance, and incident response.

## Milestones (checkable)
- [ ] M1: write a reentrancy exploit against a naive withdraw function and then fix it.
- [ ] M2: list the trust assumptions a "decentralised" bridge still makes.
- [ ] M3: explain how a flash loan turns an economic invariant into an exploit.
- [ ] M4: design a pause/upgrade governance process with real delay and multisig control.
- [ ] M5: state clearly what a blockchain does not protect you from.

## Core Competencies
- DeFi vulnerability classes and their root causes, not just their names.
- Oracle design and manipulation resistance; the difference between spot and TWAP.
- Access-control patterns: ownership, roles, timelocks, and upgrade key custody.
- Audit and verification workflow, and how to read an audit report critically.

## Anti-Goals
- Treating an audit as a guarantee rather than a point-in-time review of specific code.
- Assuming a contract cannot be paused, or assuming it must never be.
- Storing private keys or seeds anywhere a web server can read them.

## Anti-Goals note
Blockchain systems are unforgiving: a bug is not a rollback, it is a permanent loss. The
discipline of this lab is verification before deployment, not detection after.

## Interview Lens
- "What are the top three ways a token contract gets drained?"
- "Your bridge is 'trustless'. What is it actually trusting?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: read a vulnerable contract, exploit it locally.
- Wk2 QUIZ/FLASHCARDS to 90%+; fix the contract and add invariant tests.
- Wk3 MINI_PROJECT with a local chain, unit tests, fuzzing, and an audit writeup.
- Wk4 REAL_WORLD_PROJECT: a token launch flow with governance and incident readiness.

## Done = You Can
- Audit a simple contract for the standard vulnerability classes, explain the economic
  reasoning behind an attack, and specify the controls a launch needs.
