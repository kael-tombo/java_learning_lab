# Data Wrangling - Mental Models

## 1. The ledger model

Treat every dropped, filled, or retyped cell as a ledger entry: what changed,
why, and how many rows were touched. A cleaning run with no ledger is an
audit failure, not a shortcut.

## 2. Missingness as a mechanism, not a nuisance

Ask "what process hid this value?" before "what number do I plug in?".
MCAR is a coin flip, MAR is a rule that depends on data you can see, MNAR
is a rule that depends on the hidden value itself. The model of the holes
chooses the patch.

## 3. Fill values are borrowed, not found

Mean or median imputation borrows the center of the observed data and lends
it to the gaps. The loan is visible: variance shrinks and the sample looks
more certain than it is. Never report imputed precision as measured precision.

## 4. Keys define identity

A row has no identity until you declare the key. `(customer, date)` says two
same-day rows for one customer are one event; `(customer, date, amount)` says
they can be two. Dedup bugs are identity-definition bugs first, code bugs
second.

## 5. Parse strictly, reject loudly

Coercion is a border checkpoint: a fixed grammar, every reject stamped with
a reason, totals reconciled. Lenient parsing (empty string becomes zero) is
how phantom revenue and phantom patients are born.

## 6. Flags are referrals, not verdicts

An outlier flag refers a row to a human specialist. The IQR fence and the
z-score are two triage nurses who sometimes disagree; disagreement is
information about skew and masking, not a tie to break by coin flip.

## 7. Reconciliation as conservation law

Rows are neither created nor destroyed by cleaning, only sorted into kept,
removed, rejected, and filled buckets. `in = kept + removed + rejected` is
the conservation equation; a run that cannot balance it has a leak, and the
leak - not the analysis - is the next task.
