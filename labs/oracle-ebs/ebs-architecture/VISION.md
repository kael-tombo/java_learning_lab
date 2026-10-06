# EBS Architecture — Vision

## Where this lab takes you
A complete map of Oracle EBS R12.2: what each tier does, which component owns
which responsibility, and why the stack is shaped the way it is.

## The Arc
1. **Database tier** — the data model, public APIs, and why you never bypass them.
2. **Application tier** — Forms server, web server, concurrent processing.
3. **Desktop tier** — where the client lives and what it costs in bandwidth.
4. **Fusion Middleware** — OC4J/Oracle HTTP Server and the stack they sit in.
5. **Multi-node** — how nodes share `APPL_TOP` and what that implies.
6. **EBR** — edition-based redefinition, the upgrade safety net.
7. **File system** — `APPL_TOP`, `DB_TOP`, and the run/patch split.

## Milestones (checkable)
- [ ] M1: Label every tier and component in the R12.2 stack diagram.
- [ ] M2: Trace one request from browser click to database row and back.
- [ ] M3: Name the three major file-system roots and their contents.
- [ ] M4: Explain why the public API layer exists and what it protects.
- [ ] M5: Describe how multi-node clusters share `APPL_TOP` over NFS.
- [ ] M6: State what edition-based redefinition gives an upgrade.
- [ ] M7: Describe concurrent processing and where the workers run.
- [ ] M8: Produce an architecture page a new joiner could be onboarded from.

## Anti-Goals
- Treating EBS as a single application rather than a tiered stack.
- Calling the concurrent manager a batch queue and leaving it there.
- Assuming `APPL_TOP` is local to each node.
- Describing the stack from memory without drawing it.

## The one-sentence thesis
EBS is three tiers and a strict API boundary — most upgrade failures come from
breaking the boundary, not from the upgrade itself.