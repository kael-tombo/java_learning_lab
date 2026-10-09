# Step-by-Step: Count Bitstrings With No Consecutive Zeros

Goal: count strings over {0, 1} of length n containing no substring "00".

## 1. Set Up States

Let aₙ = number of valid strings of length n. Rather than count directly, track what the string ends with:

- xₙ = valid strings of length n ending in **1**
- yₙ = valid strings of length n ending in **0**

Then aₙ = xₙ + yₙ.

## 2. Write the Transitions

- A string ending in 1 can be extended by either digit: appending 1 gives xₙ₊₁ contribution, appending 0 gives a string ending in 0 (allowed — the previous digit was 1).
  - xₙ₊₁ = xₙ + yₙ = aₙ (append 1 to *any* valid string)
  - yₙ₊₁ = xₙ (append 0 only to a string ending in 1; appending to a yₙ string would create "00")

So aₙ₊₁ = xₙ₊₁ + yₙ₊₁ = aₙ + xₙ = aₙ + aₙ₋₁.

## 3. Identify Base Cases

- n = 1: "0", "1" → a₁ = 2
- n = 2: "01", "10", "11" → a₂ = 3 (only "00" excluded)
- a₀ = 1 (the empty string is validly free of "00")

The recurrence aₙ = aₙ₋₁ + aₙ₋₂ with 1, 2, 3, … is the **Fibonacci sequence shifted**: aₙ = Fₙ₊₂ with F₁ = 1, F₂ = 1.

## 4. Compute by Hand

| n | strings | count aₙ |
|---|---|---|
| 0 | ε | 1 |
| 1 | 0, 1 | 2 |
| 2 | 01, 10, 11 | 3 |
| 3 | 010, 011, 101, 110, 111 | 5 |
| 4 | 0101, 0110, 0111, 1010, 1011, 1101, 1110, 1111 | 8 |
| 5 | (each = previous two summed) | 13 |

Check n = 3 by complement: 2³ = 8 total; only "000", "001", "100" contain "00" → 8 − 3 = 5. ✓

## 5. Verify the Exclusion List at n = 3

Forbidden strings: those containing "00" → 000, 001, 100 — exactly 3, so 8 − 3 = 5 = a₃. (010 is fine: its length-2 windows are "01" and "10".) This complement check is the fastest way to catch a transition error.

## 6. Closed Form (Optional Check)

aₙ = Fₙ₊₂ = (φⁿ⁺² − ψⁿ⁺²)/√5 with φ = (1+√5)/2, ψ = (1−√5)/2. For n = 4: F₆ = 8 ✓. Round the real expression to the nearest integer to get the exact count — the roundoff never crosses a half because |ψ|ⁿ⁺²/√5 < 1/2.

## 7. Generalize the Technique

Any local forbidden-pattern count works the same way: define states = "what suffix of a valid string matters," then aₙ = Σ over valid transitions. For "no 000" you need three states (ends in 1, ends in 10, ends in 100) giving aₙ = aₙ₋₁ + aₙ₋₂ + aₙ₋₃. The state count equals the pattern length — this is exactly the subset construction of a small DFA, previewing automata-based counting in later labs.
