# ANTI-PATTERNS: Architectural Decision Making
## Lab 19 | Production Engineering Academy

---

## Anti-Pattern 1: "Ivory Tower" Architecture (Decisions in a Vacuum)

### The Mistake
An enterprise architect sitting in isolation writes a 50-page architecture specification dictating tools, frameworks, and patterns without consulting the engineers who write the code or run the on-call pager.

### Why It Fails
- Fails to reflect real production constraints, legacy nuances, and developer tooling realities.
- Developers reject or work around the mandated architecture, leading to "Shadow IT" and architectural fragmentation.

### The Correct Production Fix
Decisions must be co-authored with practicing software engineers and validated via working code prototypes before formalization.

---

## Anti-Pattern 2: The Stale ADR Repository

### The Mistake
Writing ADRs once and never updating them when technical conditions change or decisions are superseded.

### Why It Fails
New team members read outdated ADRs, implement obsolete patterns, and perpetuate superseded architectural decisions.

### The Correct Production Fix
When a decision is replaced, explicitly update the old ADR status to `SUPERSEDED by ADR-xxx` with a direct link to the new ADR.
