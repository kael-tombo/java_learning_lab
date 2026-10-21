# Feature Stores — Mental Models

## 1. Time machine with a one-way lock
You may look into the past (ts <= t) but never the future. Every
training row is a question: "what did we know at label time?" The as-of
join is the lock.

## 2. Two kitchens, one recipe
Offline and online are two kitchens. If they use different recipes, the
dishes differ. The registry enforces one recipe (shared transform code)
cooked in two ovens (scan vs lookup).

## 3. Library editions, not edits
Versions are book editions. v2 does not rewrite v1 copies on shelves;
models cite the edition they read. Backfill prints the new edition.

## 4. Milk expiry dates
TTL is the expiry stamp. Old milk is thrown out (treated missing), not
served quietly. Coverage is the fraction of cartons still fresh.

## 5. Receipts for every dataset
A training set without (feature, version, code hash) lineage is a
receipt-less expense: unauditable. The store staples the receipt to
every row batch.

## 6. Airport departures board
The online store is the departures board: it shows the latest status
per flight (entity), overwritten as updates arrive. The offline log is
the full tower recording. Passengers (serving) read the board; accident
investigators (training auditors) replay the tape.

## 7. Quarantine shelf
TTL-expired values sit on a quarantine shelf: visible to auditors,
untouchable by serving. Imputation is the labeled substitute issued at
the counter, with its own version stamp, so downstream never mistakes
substitute for stock.
