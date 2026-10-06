# Quiz — Geometry Algorithms

15 questions. Each key gives the reason.

---

## Q1
Write the 2D cross-product orientation formula.

<details><summary>Answer</summary>

(B.x-A.x)(C.y-A.y) - (B.y-A.y)(C.x-A.x).

</details>

## Q2
What does a positive orientation value mean?

<details><summary>Answer</summary>

A counter-clockwise turn at B.

</details>

## Q3
Andrew monotone chain time complexity?

<details><summary>Answer</summary>

Θ(n log n) from the sort; the scans are Θ(n).

</details>

## Q4
Why must the hull pop on a non-left turn?

<details><summary>Answer</summary>

A clockwise (or straight) turn means the middle point is inside or below the hull edge and cannot be a vertex.

</details>

## Q5
What predicate decides segment intersection?

<details><summary>Answer</summary>

Opposite orientation signs on both endpoint-pairs of the two segments.

</details>

## Q6
How does ray casting decide inside vs outside?

<details><summary>Answer</summary>

Odd number of edge crossings = inside.

</details>

## Q7
What is the vertex-ray double-count fix?

<details><summary>Answer</summary>

Use the half-open y-interval test (yi > y) != (yj > y).

</details>

## Q8
Closest pair: what is the strip width and why?

<details><summary>Answer</summary>

2δ around the midline — any closer pair must straddle the split within δ.

</details>

## Q9
Why the Master theorem gives Θ(n log n) for closest pair?

<details><summary>Answer</summary>

T(n)=2T(n/2)+Θ(n) ⇒ Θ(n log n).

</details>

## Q10
Why never use slopes for vertical lines?

<details><summary>Answer</summary>

Division by zero and floating-point error; cross products avoid both.

</details>

## Q11
Two collinear overlapping segments — what does the inclusive orientation test report?

<details><summary>Answer</summary>

An intersection (touching/overlap), not a proper crossing.

</details>

## Q12
What is the orientation of (0,0),(0,5),(0,10)?

<details><summary>Answer</summary>

0 — collinear.

</details>

## Q13
How many points can lie in the 2δ-strip rectangle in closest pair?

<details><summary>Answer</summary>

At most a constant (≤ 8), so the 7-neighbour check suffices.

</details>

## Q14
What does the sign of the cross product equal for collinear points?

<details><summary>Answer</summary>

0.

</details>

## Q15
Andrew's algorithm output order?

<details><summary>Answer</summary>

Counter-clockwise hull starting at the leftmost point.

</details>
