# Mental Models: ZGC

## 1. Colors as library due-date stamps

Each reference is a library book stamped with a due date (color). The
librarian (barrier) checks the stamp on every checkout (load). An
out-of-date stamp sends the book through re-stamping (healing) before it
leaves — one book at a time, never a whole-inventory shutdown.

## 2. Load barrier as a spell-checker

Every word you read (reference load) passes a spell-checker that fixes
stale spellings inline. Most words pass untouched (fast path, a few
instructions); the occasional stale one pauses for correction (slow
path) and then reads correctly forever. Writing speed barely changes;
reading carries the checker.

## 3. Concurrent movers as highway repaving at night

Traffic (application) keeps flowing while crews (movers) repave one lane
at a time. A driver who hits fresh asphalt follows the detour sign
(forwarding state) to the new lane automatically. The only full stops are
three brief flag-waves (mark-start, mark-end, relocate-start handshakes)
measured in microseconds.

## 4. Minors as taking out the kitchen trash

Minors empty the kitchen bin (young gen) daily — fast, frequent, most of
the waste. Majors clean the whole house including the attic (old gen)
rarely. Running whole-house cleans daily (single-generation mode) wastes
effort when the attic barely fills; the generational default matches
effort to where garbage actually accumulates.

## 5. Warmup major as commissioning a ship

The first voyage is sea trials: engines tested, charts calibrated, crew
drilled. The warmup major commissions heap sizing and metadata before
real cargo (churn) loads. Judging cruise performance by sea-trial logs
misreads routine for trouble.

## 6. Timer as a night janitor

Without the timer, an empty office never gets cleaned (no pressure, no
collection). `ZCollectionInterval` is the night janitor on schedule:
sweeps on the clock whether or not anyone worked late, so morning
arrivals (request bursts) meet a clean floor.
