# VISION — Java Syntax

## Vision Statement
**Write Java that compiles cleanly and reads clearly** — master syntax as a communication tool, not trivia. Every brace and semicolon exists to make intent unambiguous to compiler and teammate.

---
## Mental Models
### 1. Source → Bytecode Contract
```
.java → javac → .class → JVM
Syntax errors = broken contract; compiler is your first reviewer.
```
### 2. Package as Namespace + Access Boundary
`package com.acme.billing;` maps to directory; controls visibility with `public/package-private`.
### 3. Entry-Point Model
`public static void main(String[])` — JVM handshake: class loading → verification → invocation.
### 4. JShell Feedback Loop
Experiment → observe → codify. Use `jshell` for syntax hypotheses before committing to files.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Naming unclear? | Rename; classes Nouns, methods verbs |
| Import wildcard? | No — explicit imports, avoid collisions |
| Magic literal? | Extract `static final` constant |
| Class too big? | Split by responsibility, one public class/file |

---
## Career Trajectory
- **L1 Operator:** write/compile/run, fix syntax errors, use IDE quick-fixes.
- **L2 Tuner:** clean package structure, javadoc, style checks (Checkstyle).
- **L3 Expert:** code reviews focused on readability, onboarding guides.
- **L4 Architect:** repo standards, build conventions, multi-module layout.

---
## 4-Week Path
```
W1: javac/java, classpath, packages, main; JShell drills.
W2: Operators, precedence, scope; 20 small katas.
W3: Reading code: JDK samples, style guides (Google Java Style).
W4: Mini CLI app with packages + README + build via javac/jar.
```
## Success Metrics
- [ ] Compile/run multi-package app from CLI without IDE
- [ ] Explain classpath vs modulepath in 2 minutes
- [ ] Zero checkstyle violations on personal project
