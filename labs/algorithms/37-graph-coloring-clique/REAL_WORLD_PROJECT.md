# REAL_WORLD_PROJECT — Graph Coloring and Cliques
> Exam timetabling service: conflict-graph coloring with a clique lower bound shown on every published timetable.

## System and inputs
- Enrollment snapshot maps each exam to its student set; conflict edge when shared students exceed zero (configurable threshold for room-sharing rules).
- Room inventory per slot (capacity, features); scheduler input is the conflict graph plus slot inventory.
- Published timetable shows slots used, the clique lower bound, and the gap.

## Design
- Welsh-Powell initial coloring, then single-vertex recolor passes (move a vertex to a lower color when its neighbors allow) until fixpoint.
- Bron-Kerbosch on the conflict graph (bounded by graph size guard; dense graphs over 200 vertices use a greedy-clique lower bound instead, labeled as such).
- Slot assignment packs color classes into rooms by size; overflow creates a documented extra slot with the cause.

## Metrics
- Slots used vs clique lower bound (gap) per scheduling run.
- Recolor-pass improvement count and runtime.
- Student-conflict violations (must stay zero; any nonzero pages).
- Runtime vs vertex/edge counts for capacity planning of the next term.

## Failure modes
- Late enrollment change invalidates the timetable: versioned snapshots; changes after freeze go to an overflow pass, never silent edits.
- Dense-graph BK blowup: vertex guard switches to the greedy-clique bound with the substitution visible on the report.
- Room inventory shortfall: explicit extra slot with cause (rooms, not colors) so the gap metric stays honest.
- Threshold misconfiguration hiding conflicts: dry-run validator reports edge counts at candidate thresholds before publish.

## Rollout
1. Shadow-schedule last term's data; compare slots and violations vs the actual timetable.
2. Schedule one small faculty live; publish the gap metric alongside.
3. Full rollout with freeze/overflow policy enforced by the tool.

## Acceptance criteria
1. Reference graph through the service path yields 3 slots with gap 0 (omega = colors = 3).
2. Verifier proves zero monochromatic conflicts on every published timetable.
3. Dense-graph guard test shows the labeled substitution, not a hang.
4. Late-change test routes to overflow with an audit entry.
5. Rollback republishes the previous frozen timetable unchanged.

## Cost and contract notes
- Room cost per extra slot priced from inventory; the gap metric converts directly into the cheapest negotiable saving.
- Scheduling runs versioned by enrollment snapshot hash; re-runs are diffable slot by slot.
- Overflow-pass exams billed at the premium invigilation rate, reported separately so the gap stays honest.
- Contract: POST /schedule takes snapshot id; GET /timetable/{id} returns slots, bound, gap, and verifier receipt.
