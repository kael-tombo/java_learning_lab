# Vector Spaces — Exercises

## 1. Span membership

Q: Is (1,2,1) in span{(1,1,0),(0,1,1)}? Is (1,0,2)?
A: a(1,1,0)+b(0,1,1)=(x,y,z) gives a=x, b=y-x, and needs z=y-x.
For (1,2,1): 1=2-1 holds — in the span with a=b=1.
For (1,0,2): 2 vs 0-1=-1 — outside.

## 2. Determinant pair

Q: Decide independence of {(1,2,3),(4,5,6),(7,8,10)} and of
{(1,2,3),(4,5,6),(7,8,9)}.
A: First determinant: 1*(50-48)-2*(40-42)+3*(32-35) = 2+4-9 = -3,
independent. Second: same with 9: 1*(45-48)-2*(36-42)+3*(32-35) =
-3+12-9 = 0, dependent via row3 = 2*row2 - row1:
2(4,5,6)-(1,2,3) = (7,8,9).

## 3. Rank

Q: Rank of the map with rows (1,0,2,-1),(0,1,1,3),(2,1,5,1)?
A: 2, since 2*row1+row2 = (2,1,5,1) = row3. First two rows are
independent (neither is a multiple of the other).

## 4. Null space

Q: Find a null-space basis and verify it.
A: Free x3,x4: x1 = -2x3+x4, x2 = -x3-3x4. Basis (-2,-1,1,0),
(1,-3,0,1). Dots vs row1: 1*(-2)+0+2*1-0=0; 1*1+0+0-1=0.
Vs row2: 0-1+1+0=0; 0-3+0+3=0. Nullity 2; 2+2=4.

## 5. Coordinates

Q: Coordinates of (3,7) in {(1,1),(1,-1)}?
A: c1+c2=3, c1-c2=7 gives c1=5, c2=-2. Check:
5(1,1)-2(1,-1) = (3,7).

## 6. Subspace or not

Q: Which are subspaces of R^2: (a) {xy=0}, (b) {x+y=0}, (c) {x+y=1}?
A: (a) No: (1,0)+(0,1)=(1,1) escapes. (b) Yes: line through 0.
(c) No: 0 missing.
