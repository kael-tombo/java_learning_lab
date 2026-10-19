# Mock Interview: When Plain Layers Are the Right Answer

> Q&A format. Northfield Campus enrolls evening students; admins approve applications; teachers record attendance.

---

## Questions

1. "Justify three tiers for this."
   One team, one relational store, screens that map to tables. The layered split gives a small team exactly what it needs — thin controllers, rules in services, SQL confined to repositories — without taxing whoever maintains it after hours. Architecture should match the size of the crew.

2. "Where does 'a student can enroll only if prerequisites are signed off' live?"
   In the enrollment service. It is a rule over several tables, not persistence trivia and not presentation polish. The repository supplies candidates; the service decides. That placement is what keeps the rule verifiable in one place.

3. "A developer calls the repository straight from a controller for a dropdown."
   Cheap temptation, real cost: that lookup will acquire rules — hidden classes, closed cohorts — and then they live in a controller forever. Route the call through the layer above. If routing one read feels heavy, the read belongs in the service contract anyway.

4. "Which layer owns DTOs?"
   Presentation builds them from service results; services return domain-shaped types. When DTOs span both boundaries, the web tier has quietly married the persistence schema, and every migration couples three layers instead of two.

5. "How do exceptions travel?"
   Upward only, translated on the way. Persistence raises a constraint violation; the service reframes it — "cohort full" — and the controller decides the user-facing response. Lower layers never import HTTP types, ever.

6. "Logging and timing touch every tier — where do they live?"
   One aspect applied at service boundaries keeps them out of every class. The standing rule: nothing hand-written per layer; if a concern must touch all three tiers, it is implemented once and woven in.

---

## Probes

- "Why not skip the service for a pure read?" — because "pure reads" grow opinions: filters, privacy trims, audit notes. The seam costs one method today and buys a stable contract for years.
- "When does this layout rot?" — when persistence details leak upward as "convenience" or when controllers grow logic. Both are detectable in review, which is the actual defense.
- "Where does the auth middleware sit?" — presentation, ahead of the service call; controllers receive a principal, and services still enforce coarse checks, because middleware is a deployment fact, not a guarantee.
- "Scheduled jobs — which tier?" — they enter like users do, through the service layer; a cron trigger is just another presentation-side caller and never touches repositories directly.
- "Would you ever inject a repository into a controller?" — no, not even for a pure dropdown: the rule is worthless with exceptions, and I have never met a lookup whose rules stayed empty for long.
- "Testing story per layer?" — deep tests live at the service tier; controller tests rehearse mapping and nothing more; repository checks verify query shape against a real database in CI.
- "How does this age as the team grows?" — the service interfaces harden into the real contract, so extracting a module later starts at a boundary that already has exactly one caller and one shape.
- "Read-only pages with trivial logic — same seam?" — yes, thinner content: the service returns what it returns and the controller maps it; the seam survives on consistency, not on every read being interesting.
- "Anything the layer list itself omits?" — ownership: layers describe dependencies, not responsibility, and two services sharing one business layer still need an explicit owner apiece.

---

## Red Flag

Five layers and a dispatcher abstraction in a two-person codebase. That is a memorized diagram, not a trade-off — the interviewer hears a candidate who cannot calibrate structure to the size of the problem.
