# Professional Identity — Worked Artifacts

Three identity artifacts rebuilt line by line. The people are invented
example personas (the flaws and the fixes are not), each drawn from a
different technical register so the pattern transplants.

## Artifact 1 — The Summary Paragraph

Before (data engineer, four years):

```text
Experienced data engineer with strong skills in cloud and big data
technologies. Quick learner and team player who is passionate about
technology and delivering value. Seeking new opportunities in a
growth-oriented environment.
```

The read: every sentence is a claim priced zero on evidence (no artifact,
no scale, no mechanism) and crisis-mode on relevance (the last sentence
positions the writer as available, not needed). Rebuild:

```text
Data engineer, four years, pipeline-reliability register. Ran the
provider-feed ingestion @ Medlink (health-data startup): 40+ vendor
feeds, 6-month median feed a week. Two rebuilds I own: the feed
replay tool (cut incident triage from ~2h to ~15m per incident)
and a schema-drift alarm that catches malformed feeds before they
land in partner tables.
```

Same person, ~7 more evidence units: named domain, ownership verbs,
countable surfaces, two named artifacts with mechanisms. Adjectives
declined deliberately: "passionate" priced zero, "experienced" priced
lower than "four years".

## Artifact 2 — The Skills Matrix

Before (embedded engineer):

```text
C/C++: expert | Python: expert | RTOS: advanced | Git: expert
```

The read: three "expert"s plus a version-control system marked "expert"
tells a careful reader you stop at the first resume template. Graded
rebuild with one evidence row each:

```text
C (production, 5 yrs; fixed race conditions in ISR-shared FIFOs)
Python (test tooling on host; no production CUDA/graph code)
FreeRTOS (3 shipped products; wrote the watchdog policy)
Git (fluent; bisect-to-cause is my default, not re-randomize)
```

Graded vocabulary ("fluent", "test tooling on host") costs nothing and
survives a follow-up interview question about each row.

## Artifact 3 — The Positioning One-Liner

Before (QA technician, spoken at meetups):

```text
I'm interested in quality and quality is important, so I do QA.
```

The rebuilt structure — level/function + domain + artifact proof:

```text
QA automation technician on payment terminals. I own the regression
harness that three firmware teams gate their releases on, and I've
been asked twice to say at release meetings whether we ship.
```

Not adjectives — authority evidence: who uses your work, and what
decisions flow through it.
