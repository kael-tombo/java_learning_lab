# Exact-Cover Solver Backend on Dancing Links

Shop. A scheduling service packs shifts under hard constraints; a
tiling demo fills boards with pentominoes. Both reduce to exact cover,
and Algorithm X with dancing-links cover/uncover is the engine - O(1)
link surgery per cover step instead of matrix copies.

DLX core. Toroidal doubly-linked lists over the sparse 0/1 matrix with
column-size headers; cover removes a column and its rows, uncover
restores exactly. A restore audit re-solves after 10k cover/uncover
cycles and diffs the matrix against a snapshot - any leak fails loudly.

Scheduler caller. Shift slots as columns, candidate assignments as
rows; solutions enumerated up to a cap with timeout. A 40-slot fixture
with a planted solution must be found; an unsatisfiable variant must
report so within the timeout with the search-node count published.

Exact-cover bench. Pentomino tilings plus N-queens-as-exact-cover at
three sizes; nodes-per-second quoted alongside solution counts. Column
choice heuristic (minimum remaining values) A/B tested against naive
order with node-count ratios.

SAT-flavored caller. Small satisfiability instances translated to exact
cover where natural; solved instances checked by an independent clause
verifier. Translation limits stated - this is a benchmark, not a SAT
claim.

Search hazards. Exponential blowup fixture with node cap (search stops,
reports partial), duplicate rows (dedup rule), empty constraint set
(vacuous solution specified), timeout mid-search (partial log kept).

Ship. DLX, scheduler CLI, bench fixtures, verifier logs, heuristic A/B.
Marks: cover/restore audit 12, planted-solution plus UNSAT conduct 10,
heuristic evidence 8.
## Search budget
- Node cap posted per fixture.
- Planted solution found in CI.
- UNSAT case timed.
- Heuristic A/B archived.
- Partial logs retained.
