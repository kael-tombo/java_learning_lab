# Exercises — Geometry Algorithms

Attempt each before reading the hint.

## Ex 1
Classify the turn A(0,0)→B(2,0)→C(1,1).

<details><summary>Hint</summary>

cross = (2)(1)-(0)(1) = 2 > 0 ⇒ counter-clockwise.

</details>

## Ex 2
Why must the orientation product use long?

<details><summary>Hint</summary>

Coordinate differences up to 2·10⁹ multiply to ~4·10¹⁸, exceeding int.

</details>

## Ex 3
What does Andrew's scan do when three consecutive lower-hull points turn clockwise?

<details><summary>Hint</summary>

Pop the middle point — it cannot be on the lower hull.

</details>

## Ex 4
Count the y-crossings of a ray through a vertex with the half-open rule.

<details><summary>Hint</summary>

Exactly once: (yi > y) != (yj > y) counts a shared vertex once.

</details>

## Ex 5
In closest pair, why only the next 7 y-sorted candidates?

<details><summary>Hint</summary>

A packing argument: at most 7 points can sit in the δ×2δ strip rectangle.

</details>

## Ex 6
Distinguish proper vs touching intersection in the orientation test.

<details><summary>Hint</summary>

Strict sign opposition = crossing; inclusive = touching/overlap.

</details>

## Ex 7
Give the degenerate hull for three collinear points.

<details><summary>Hint</summary>

The segment between the extremes; the middle point is excluded (or kept by policy).

</details>
