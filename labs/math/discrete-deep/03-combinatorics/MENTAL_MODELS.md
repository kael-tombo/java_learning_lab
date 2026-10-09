# Mental Models: Combinatorics

## 1. Counting = Exhibiting a Bijection

Every "how many" question is answered by matching the unknown set to a known one with a two-way correspondence. "Number of 2-subsets of {A,B,C} = number of 1-element choices you leave out" is C(3,2) = C(3,1) = 3 via S ↔ A∖S. When a count feels wrong, ask: what exactly does each object map to, and can I reverse it? If two constructions land on the same object, you have double-counted — that *is* inclusion–exclusion's diagnosis.

## 2. Slots First, Then Fill

Before multiplying anything, draw the slots: `_ _ _ _`. For a 4-char PIN from 10 digits with repeats: 10·10·10·10 = 10⁴. For 4 distinct digits: 10·9·8·7 = P(10,4). The slot picture automatically encodes whether repetition is allowed and whether order matters; skipping straight to "is it n! or C(n,k)?" is where the classic errors start.

## 3. Choose, Then Arrange

A favorite decomposition: count = (choose the subset) × (arrange it). Number of 5-card hands = C(52,5); number of 5-card *hands in dealt order* = C(52,5)·5! = P(52,5). When an answer looks too big or too small, ask which of the two factors you forgot — losing the ×k! means you counted unordered things as ordered (or the reverse).

## 4. The Complement Is a Shortcut, Not a Trick

"Count objects with ≥ 1 bad property" usually explodes into 2ⁿ − 1 terms; "1 − count objects with none" collapses to one clean product. Mental test: if the "none" case has a clean structure (no repeats, all distinct), use the complement. If it does not (constraints are entangled), inclusion–exclusion is the complement at each level.

## 5. Pascal's Triangle as a Merge Rule

C(n,k) = C(n−1,k−1) + C(n−1,k) has a picture: element xₙ either joins your chosen k-set (then choose k−1 from the other n−1) or stays out (choose k from n−1). Every row is the sum of two entries above it — which makes the triangle both a fast table and a proof device: identities you see visually (hockey stick, alternating sums) are proven by regrouping.

## 6. Recurrences as State Machines

aₙ = aₙ₋₁ + 2aₙ₋₂ says: any valid string of length n either ends in "1" (strip it, aₙ₋₁ ways) or ends in "00" (strip both, 2 is the count of the digit options... more precisely the *state* is the last bit). Track the last symbol as state and the recurrence is just the transition table. For bitstrings with no "00": states END-IN-1 and END-IN-0, transitions give the Fibonacci numbers.

## 7. Exponentials Beat Everything

n! ≫ cⁿ ≫ poly(n) eventually: 10! = 3,628,800 while 2¹⁰ = 1,024 and 10³ = 1,000. So before designing an algorithm, count the output size: an algorithm listing all subsets of 30 elements must do 2³⁰ ≈ 10⁹ operations even with a perfect O(1)-per-subset implementation. Counting tells you feasibility before you write a line.

## 8. Labels vs. Unlabeled

The single question that resolves most distribution problems: can I tell the boxes (people, days, positions) apart? Labeled → each ball has n choices → nᵏ or k! factors. Unlabeled → you only record the shape of the count vector → stars and bars. Get this wrong by one factor of k! and your answer is off by more than any arithmetic slip.
